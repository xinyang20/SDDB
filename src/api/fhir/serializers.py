"""FHIR资源序列化器 - 将SDDB模型转换为FHIR标准格式"""
from datetime import datetime
from models import PrescriptionModel, PatientModel, DoctorModel, TaskModel

class FHIRSerializer:
    """FHIR资源序列化器基类"""

    @staticmethod
    def prescription_to_fhir(prescription: PrescriptionModel):
        """将处方模型转换为FHIR MedicationRequest"""
        return {
            "resourceType": "MedicationRequest",
            "id": str(prescription.prescription_id),
            "status": "completed" if prescription.status == "已完成" else "active",
            "intent": "order",
            "subject": {
                "reference": f"Patient/{prescription.patient_id}",
                "display": f"患者ID: {prescription.patient_id}"
            },
            "requester": {
                "reference": f"Practitioner/{prescription.doctor_id}",
                "display": f"医生ID: {prescription.doctor_id}"
            },
            "authoredOn": prescription.date.isoformat() if prescription.date else None,
            "dosageInstruction": [{
                "text": prescription.usage_instructions,
                "timing": {
                    "repeat": {
                        "frequency": 1,
                        "period": 1,
                        "periodUnit": "d"
                    }
                }
            }],
            "dispenseRequest": {
                "quantity": {
                    "value": prescription.amount,
                    "unit": "剂"
                },
                "expectedSupplyDuration": {
                    "value": prescription.amount,
                    "unit": "天"
                }
            },
            "note": [{
                "text": f"处方金额: {prescription.amount}, 用法: {prescription.usage_instructions}"
            }]
        }

    @staticmethod
    def patient_to_fhir(patient: PatientModel):
        """将患者模型转换为FHIR Patient"""
        return {
            "resourceType": "Patient",
            "id": str(patient.patient_id),
            "active": True,
            "name": [{
                "use": "official",
                "text": patient.name,
                "family": patient.name[0] if patient.name else "",
                "given": [patient.name[1:] if len(patient.name) > 1 else ""]
            }],
            "gender": "male" if patient.gender == "男" else "female" if patient.gender == "女" else "unknown",
            "birthDate": None,  # 可以根据age计算
            "telecom": [{
                "system": "phone",
                "value": patient.contact_number,
                "use": "mobile"
            }],
            "extension": [{
                "url": "http://sddb.com/fhir/StructureDefinition/patient-age",
                "valueInteger": patient.age
            }]
        }

    @staticmethod
    def doctor_to_fhir(doctor: DoctorModel):
        """将医生模型转换为FHIR Practitioner"""
        return {
            "resourceType": "Practitioner",
            "id": str(doctor.doctor_id),
            "active": True,
            "name": [{
                "use": "official",
                "text": doctor.name,
                "family": doctor.name[0] if doctor.name else "",
                "given": [doctor.name[1:] if len(doctor.name) > 1 else ""]
            }],
            "gender": "male" if doctor.gender == "男" else "female" if doctor.gender == "女" else "unknown",
            "telecom": [{
                "system": "phone",
                "value": doctor.contact_number,
                "use": "work"
            }],
            "qualification": [{
                "code": {
                    "coding": [{
                        "system": "http://sddb.com/fhir/CodeSystem/doctor-title",
                        "code": doctor.title,
                        "display": doctor.title
                    }],
                    "text": doctor.title
                }
            }],
            "extension": [{
                "url": "http://sddb.com/fhir/StructureDefinition/practitioner-department",
                "valueString": doctor.department
            }]
        }

    @staticmethod
    def task_to_fhir(task: TaskModel, prescription: PrescriptionModel = None):
        """将任务模型转换为FHIR Task"""
        status_map = {
            "未完成": "in-progress",
            "完成": "completed"
        }

        return {
            "resourceType": "Task",
            "id": str(task.task_id),
            "status": status_map.get(task.status, "in-progress"),
            "intent": "order",
            "priority": "routine",
            "description": f"中药代煎任务 - 处方ID: {task.prescription_id}",
            "focus": {
                "reference": f"MedicationRequest/{task.prescription_id}",
                "display": f"处方 #{task.prescription_id}"
            },
            "for": {
                "reference": f"Patient/{prescription.patient_id}" if prescription else None,
                "display": f"患者ID: {prescription.patient_id}" if prescription else None
            },
            "executionPeriod": {
                "start": task.receive_time.isoformat() if task.receive_time else None,
                "end": task.decoction_end_time.isoformat() if task.decoction_end_time else None
            },
            "output": [
                {
                    "type": {
                        "text": "收方阶段"
                    },
                    "valueString": f"工人: {task.receive_worker_name}, 完成时间: {task.receive_time.isoformat() if task.receive_time else '未完成'}"
                },
                {
                    "type": {
                        "text": "配方阶段"
                    },
                    "valueString": f"工人: {task.form_worker_name}, 完成时间: {task.form_time.isoformat() if task.form_time else '未完成'}"
                },
                {
                    "type": {
                        "text": "煎药阶段"
                    },
                    "valueString": f"工人: {task.decoction_worker_name}, 开始: {task.decoction_start_time.isoformat() if task.decoction_start_time else '未开始'}, 结束: {task.decoction_end_time.isoformat() if task.decoction_end_time else '未完成'}"
                }
            ]
        }

    @staticmethod
    def fhir_to_prescription(fhir_data: dict):
        """将FHIR MedicationRequest转换为处方模型数据"""
        # 提取患者ID和医生ID
        patient_ref = fhir_data.get("subject", {}).get("reference", "")
        patient_id = int(patient_ref.split("/")[-1]) if "/" in patient_ref else None

        doctor_ref = fhir_data.get("requester", {}).get("reference", "")
        doctor_id = int(doctor_ref.split("/")[-1]) if "/" in doctor_ref else None

        # 提取用法说明
        dosage = fhir_data.get("dosageInstruction", [{}])[0]
        usage_instructions = dosage.get("text", "")

        # 提取数量
        quantity = fhir_data.get("dispenseRequest", {}).get("quantity", {})
        amount = quantity.get("value", 0)

        return {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "amount": amount,
            "usage_instructions": usage_instructions,
            "status": "待配方"
        }
