"""实时数据看板指标计算模块"""
from datetime import datetime, timedelta
from models import PrescriptionModel, TaskModel, WorkerModel
from sqlalchemy import func

class DashboardMetrics:
    """看板指标计算器"""

    @staticmethod
    def get_dashboard_data():
        """获取看板所有数据"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": DashboardMetrics.get_core_metrics(),
            "stage_distribution": DashboardMetrics.get_stage_distribution(),
            "worker_efficiency": DashboardMetrics.get_worker_efficiency(),
            "hourly_stats": DashboardMetrics.get_hourly_stats()
        }

    @staticmethod
    def get_core_metrics():
        """获取核心指标"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        return {
            "total_prescriptions": PrescriptionModel.query.count(),
            "today_prescriptions": PrescriptionModel.query.filter(
                PrescriptionModel.date >= today_start
            ).count(),
            "pending_tasks": TaskModel.query.filter_by(status='未完成').count(),
            "completed_today": TaskModel.query.filter(
                TaskModel.status == '完成',
                TaskModel.decoction_end_time >= today_start
            ).count(),
            "total_tasks": TaskModel.query.count()
        }

    @staticmethod
    def get_stage_distribution():
        """获取任务阶段分布"""
        # 待收方：receive_time为空
        receive_pending = TaskModel.query.filter(
            TaskModel.receive_time.is_(None),
            TaskModel.status == '未完成'
        ).count()

        # 待配方：receive_time有值，form_time为空
        formulate_pending = TaskModel.query.filter(
            TaskModel.receive_time.isnot(None),
            TaskModel.form_time.is_(None),
            TaskModel.status == '未完成'
        ).count()

        # 待煎药：form_time有值，decoction_end_time为空
        decoction_pending = TaskModel.query.filter(
            TaskModel.form_time.isnot(None),
            TaskModel.decoction_end_time.is_(None),
            TaskModel.status == '未完成'
        ).count()

        return {
            "receive": receive_pending,
            "formulate": formulate_pending,
            "decoction": decoction_pending
        }

    @staticmethod
    def get_worker_efficiency():
        """获取工人效率排行（今日完成任务数）"""
        workers = WorkerModel.query.all()
        efficiency = []

        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for worker in workers:
            # 统计今日完成的任务
            completed_tasks = TaskModel.query.filter(
                (
                    (TaskModel.receive_worker_id == worker.worker_id) |
                    (TaskModel.form_worker_id == worker.worker_id) |
                    (TaskModel.decoction_worker_id == worker.worker_id)
                ),
                TaskModel.status == '完成',
                TaskModel.decoction_end_time >= today_start
            ).count()

            efficiency.append({
                "worker_id": worker.worker_id,
                "name": worker.name,
                "completed_count": completed_tasks
            })

        # 按完成数量降序排序，取前5名
        return sorted(efficiency, key=lambda x: x['completed_count'], reverse=True)[:5]

    @staticmethod
    def get_hourly_stats():
        """获取最近24小时的任务完成趋势"""
        now = datetime.now()
        hours = []
        completed = []

        for i in range(24, 0, -1):
            hour_start = now - timedelta(hours=i)
            hour_end = now - timedelta(hours=i-1)

            count = TaskModel.query.filter(
                TaskModel.status == '完成',
                TaskModel.decoction_end_time >= hour_start,
                TaskModel.decoction_end_time < hour_end
            ).count()

            hours.append(hour_start.strftime('%H:00'))
            completed.append(count)

        return {
            "hours": hours,
            "completed": completed
        }

    @staticmethod
    def get_average_processing_time():
        """计算平均处理时间"""
        completed_tasks = TaskModel.query.filter(
            TaskModel.status == '完成',
            TaskModel.receive_time.isnot(None),
            TaskModel.decoction_end_time.isnot(None)
        ).all()

        if not completed_tasks:
            return {
                "average_minutes": 0,
                "fastest_minutes": 0,
                "slowest_minutes": 0
            }

        processing_times = []
        for task in completed_tasks:
            duration = (task.decoction_end_time - task.receive_time).total_seconds() / 60
            processing_times.append(duration)

        return {
            "average_minutes": round(sum(processing_times) / len(processing_times), 1),
            "fastest_minutes": round(min(processing_times), 1),
            "slowest_minutes": round(max(processing_times), 1)
        }
