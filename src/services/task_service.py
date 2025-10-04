from datetime import datetime
from models import TaskModel, WorkerModel, PrescriptionModel
from exts import db

class TaskService:
    @staticmethod
    def create_task(prescription_id):
        """创建任务"""
        new_task = TaskModel(
            prescription_id=prescription_id,
            receive_worker_id=None,
            receive_worker_name=None,
            form_worker_id=None,
            form_worker_name=None,
            decoction_worker_id=None,
            decoction_worker_name=None,
            admin_id=None,
            admin_name=None,
            receive_time=None,
            form_time=None,
            decoction_start_time=None,
            decoction_end_time=None,
            status='未完成'
        )
        db.session.add(new_task)
        db.session.commit()
        return new_task

    @staticmethod
    def assign_worker(task_id, worker_id, phase):
        """分配工人到指定阶段"""
        task = TaskModel.query.get_or_404(task_id)
        worker = WorkerModel.query.get_or_404(worker_id)

        # 检查任务分配规则
        if phase == 'formulate' and not task.receive_time:
            raise ValueError('必须完成收方后才能分配配方任务!')

        if phase == 'decoction' and not task.form_time:
            raise ValueError('必须完成配方后才能分配煎药任务!')

        # 分配任务
        if phase == 'receive':
            task.receive_worker_id = worker_id
            task.receive_worker_name = worker.name
        elif phase == 'formulate':
            task.form_worker_id = worker_id
            task.form_worker_name = worker.name
        elif phase == 'decoction':
            task.decoction_worker_id = worker_id
            task.decoction_worker_name = worker.name

        db.session.commit()
        return task

    @staticmethod
    def update_task_status(task_id, worker_id, action):
        """更新任务状态"""
        task = TaskModel.query.get_or_404(task_id)

        if task.status == '完成':
            raise ValueError('任务已完成，无法继续更新状态!')

        if action == 'receive' and task.receive_worker_id == worker_id and not task.receive_time:
            task.receive_time = datetime.utcnow()
        elif action == 'formulate' and task.form_worker_id == worker_id and task.receive_time and not task.form_time:
            task.form_time = datetime.utcnow()
        elif action == 'decoction_start' and task.decoction_worker_id == worker_id and task.form_time and not task.decoction_start_time:
            task.decoction_start_time = datetime.utcnow()
        elif action == 'decoction_end' and task.decoction_worker_id == worker_id and task.decoction_start_time and not task.decoction_end_time:
            task.decoction_end_time = datetime.utcnow()
            task.status = '完成'
        else:
            raise ValueError('当前任务未满足操作条件，无法完成此操作。')

        db.session.commit()
        return task

    @staticmethod
    def rollback_task(task_id, phase):
        """回退任务到指定阶段"""
        task = TaskModel.query.get_or_404(task_id)

        if phase == 'receive' and task.receive_time:
            task.receive_time = None
            task.receive_worker_id = None
            task.receive_worker_name = None
            task.status = '未完成'
        elif phase == 'formulate' and task.form_time:
            task.form_time = None
            task.form_worker_id = None
            task.form_worker_name = None
        elif phase == 'decoction' and task.decoction_start_time:
            task.decoction_start_time = None
            task.decoction_end_time = None
            task.decoction_worker_id = None
            task.decoction_worker_name = None
            task.status = '未完成'
        else:
            raise ValueError('无法回退到该阶段。')

        db.session.commit()
        return task

    @staticmethod
    def get_task_status(task):
        """获取任务的当前状态"""
        if not task:
            return "未分配任务"
        elif not task.receive_time:
            return "待收方"
        elif not task.form_time:
            return "待配方"
        elif not task.decoction_start_time:
            return "待煎药"
        elif not task.decoction_end_time:
            return "煎药中"
        else:
            return "已完成"

    @staticmethod
    def get_phase_status(task):
        """获取任务的阶段状态"""
        if task.decoction_end_time:
            return "煎药已完成"
        elif task.decoction_start_time:
            return "煎药进行中"
        elif task.form_time:
            return "配方已完成，煎药未完成"
        elif task.receive_time:
            return "收方已完成，配方未完成"
        else:
            return "收方未完成"
