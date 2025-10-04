"""智能预警规则引擎"""
from datetime import datetime, timedelta
from alerts.celery_config import celery_app
from models import TaskModel, WorkerModel, PrescriptionModel, AlertModel
from alerts.notifiers import send_alert
from exts import db
from app import app

@celery_app.task(name='alerts.rules.run_alert_checks')
def run_alert_checks():
    """执行所有预警检查（Celery定时任务）"""
    with app.app_context():
        try:
            check_timeout_tasks()
            check_abnormal_fast_tasks()
            check_task_backlog()
            check_worker_efficiency()
            return {'status': 'success', 'timestamp': datetime.now().isoformat()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

def check_timeout_tasks():
    """检查超时任务"""
    now = datetime.utcnow()

    # 收方超时(>30分钟)
    timeout_receive_tasks = TaskModel.query.filter(
        TaskModel.receive_worker_id.isnot(None),
        TaskModel.receive_time.is_(None),
        TaskModel.status == '未完成'
    ).all()

    for task in timeout_receive_tasks:
        prescription = PrescriptionModel.query.get(task.prescription_id)
        if prescription and (now - prescription.date).total_seconds() > 1800:  # 30分钟
            # 检查是否已经发送过相同告警
            existing_alert = AlertModel.query.filter_by(
                task_id=task.task_id,
                type='timeout_receive',
                is_read=False
            ).first()

            if not existing_alert:
                send_alert(
                    type='timeout_receive',
                    level='high',
                    message=f'任务 #{task.task_id} 收方阶段超时(>30分钟)，负责工人: {task.receive_worker_name}',
                    task_id=task.task_id,
                    worker_id=task.receive_worker_id
                )

    # 配方超时(>1小时)
    timeout_formulate_tasks = TaskModel.query.filter(
        TaskModel.receive_time.isnot(None),
        TaskModel.form_time.is_(None),
        TaskModel.form_worker_id.isnot(None),
        TaskModel.status == '未完成'
    ).all()

    for task in timeout_formulate_tasks:
        if (now - task.receive_time).total_seconds() > 3600:  # 1小时
            existing_alert = AlertModel.query.filter_by(
                task_id=task.task_id,
                type='timeout_formulate',
                is_read=False
            ).first()

            if not existing_alert:
                send_alert(
                    type='timeout_formulate',
                    level='high',
                    message=f'任务 #{task.task_id} 配方阶段超时(>1小时)，负责工人: {task.form_worker_name}',
                    task_id=task.task_id,
                    worker_id=task.form_worker_id
                )

    # 煎药超时(>2小时)
    timeout_decoction_tasks = TaskModel.query.filter(
        TaskModel.form_time.isnot(None),
        TaskModel.decoction_start_time.isnot(None),
        TaskModel.decoction_end_time.is_(None),
        TaskModel.status == '未完成'
    ).all()

    for task in timeout_decoction_tasks:
        if (now - task.decoction_start_time).total_seconds() > 7200:  # 2小时
            existing_alert = AlertModel.query.filter_by(
                task_id=task.task_id,
                type='timeout_decoction',
                is_read=False
            ).first()

            if not existing_alert:
                send_alert(
                    type='timeout_decoction',
                    level='high',
                    message=f'任务 #{task.task_id} 煎药阶段超时(>2小时)，负责工人: {task.decoction_worker_name}',
                    task_id=task.task_id,
                    worker_id=task.decoction_worker_id
                )

def check_abnormal_fast_tasks():
    """检查异常快速完成的任务"""
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    fast_tasks = TaskModel.query.filter(
        TaskModel.status == '完成',
        TaskModel.decoction_end_time >= one_hour_ago,
        TaskModel.receive_time.isnot(None)
    ).all()

    for task in fast_tasks:
        total_time = (task.decoction_end_time - task.receive_time).total_seconds()
        if total_time < 1800:  # 少于30分钟完成全流程
            existing_alert = AlertModel.query.filter_by(
                task_id=task.task_id,
                type='abnormal_fast'
            ).first()

            if not existing_alert:
                send_alert(
                    type='abnormal_fast',
                    level='medium',
                    message=f'任务 #{task.task_id} 完成时间异常快({int(total_time//60)}分钟)，请检查操作是否规范',
                    task_id=task.task_id
                )

def check_task_backlog():
    """检查任务积压"""
    pending_count = TaskModel.query.filter_by(status='未完成').count()

    if pending_count > 10:  # 阈值可配置
        # 检查最近是否发送过积压告警（避免重复告警）
        recent_alert = AlertModel.query.filter(
            AlertModel.type == 'backlog',
            AlertModel.created_at >= datetime.utcnow() - timedelta(minutes=30),
            AlertModel.is_read == False
        ).first()

        if not recent_alert:
            send_alert(
                type='backlog',
                level='high',
                message=f'待处理任务积压严重(当前 {pending_count} 单)，请增加人力或优化流程',
                data={'pending_count': pending_count}
            )

def check_worker_efficiency():
    """检查工人效率"""
    workers = WorkerModel.query.all()

    # 计算平均效率
    total_completed = 0
    worker_count = 0
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    for worker in workers:
        completed = TaskModel.query.filter(
            (
                (TaskModel.receive_worker_id == worker.worker_id) |
                (TaskModel.form_worker_id == worker.worker_id) |
                (TaskModel.decoction_worker_id == worker.worker_id)
            ),
            TaskModel.status == '完成',
            TaskModel.decoction_end_time >= today_start
        ).count()

        total_completed += completed
        worker_count += 1

    if worker_count == 0:
        return

    avg_efficiency = total_completed / worker_count

    # 检查低效工人
    for worker in workers:
        completed = TaskModel.query.filter(
            (
                (TaskModel.receive_worker_id == worker.worker_id) |
                (TaskModel.form_worker_id == worker.worker_id) |
                (TaskModel.decoction_worker_id == worker.worker_id)
            ),
            TaskModel.status == '完成',
            TaskModel.decoction_end_time >= today_start
        ).count()

        if completed < avg_efficiency * 0.7:  # 低于平均70%
            # 检查是否已发送告警
            existing_alert = AlertModel.query.filter(
                AlertModel.worker_id == worker.worker_id,
                AlertModel.type == 'low_efficiency',
                AlertModel.created_at >= today_start,
                AlertModel.is_read == False
            ).first()

            if not existing_alert:
                percentage = (completed / avg_efficiency * 100) if avg_efficiency > 0 else 0
                send_alert(
                    type='low_efficiency',
                    level='medium',
                    message=f'工人 {worker.name} 今日效率异常(仅为平均的 {percentage:.0f}%)，已完成 {completed} 个任务',
                    worker_id=worker.worker_id
                )
