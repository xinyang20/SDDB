from typing import Optional
from datetime import datetime
from models import PrescriptionModel, TaskModel
from exts import db
from services.task_service import TaskService


class PrescriptionService:
    @staticmethod
    def create_prescription(
        patient_id,
        doctor_id,
        amount,
        usage_instructions,
        status: Optional[str] = None,
        expected_pickup_time: Optional[datetime] = None,
    ):
        """创建处方并自动生成任务"""
        new_prescription = PrescriptionModel(
            patient_id=patient_id,
            doctor_id=doctor_id,
            amount=amount,
            usage_instructions=usage_instructions,
            status=status or '待配方'
        )
        if expected_pickup_time is not None:
            new_prescription.expected_pickup_time = expected_pickup_time

        db.session.add(new_prescription)
        db.session.commit()

        # 自动创建关联任务
        TaskService.create_task(new_prescription.prescription_id)

        return new_prescription

    @staticmethod
    def get_prescription_with_status(prescription):
        """获取带状态的处方信息"""
        task = TaskModel.query.filter_by(prescription_id=prescription.prescription_id).first()
        status = TaskService.get_task_status(task)
        return {
            "prescription": prescription,
            "status": status,
            "task": task
        }

    @staticmethod
    def get_prescriptions_by_doctor(doctor_id):
        """获取医生的所有处方"""
        prescriptions = PrescriptionModel.query.filter_by(doctor_id=doctor_id).all()
        return [PrescriptionService.get_prescription_with_status(p) for p in prescriptions]

    @staticmethod
    def get_prescriptions_by_patient(patient_id):
        """获取患者的所有处方"""
        prescriptions = PrescriptionModel.query.filter_by(patient_id=patient_id).all()
        return [PrescriptionService.get_prescription_with_status(p) for p in prescriptions]
