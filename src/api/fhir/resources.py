"""FHIR RESTful API资源端点"""
from flask_restful import Resource
from flask import jsonify, request
from models import PrescriptionModel, PatientModel, DoctorModel, TaskModel
from api.fhir.serializers import FHIRSerializer
from services.prescription_service import PrescriptionService
from exts import db

class MedicationRequestResource(Resource):
    """FHIR MedicationRequest资源 (处方)"""

    def get(self, prescription_id=None):
        """获取处方资源"""
        if prescription_id:
            # 获取单个处方
            prescription = PrescriptionModel.query.get_or_404(prescription_id)
            fhir_resource = FHIRSerializer.prescription_to_fhir(prescription)
            return jsonify(fhir_resource)
        else:
            # 获取所有处方(Bundle资源)
            prescriptions = PrescriptionModel.query.all()
            entries = [{
                "fullUrl": f"http://localhost:5050/fhir/MedicationRequest/{p.prescription_id}",
                "resource": FHIRSerializer.prescription_to_fhir(p)
            } for p in prescriptions]

            bundle = {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": len(prescriptions),
                "entry": entries
            }
            return jsonify(bundle)

    def post(self):
        """创建新处方(支持FHIR标准输入)"""
        fhir_data = request.get_json()

        if fhir_data.get("resourceType") != "MedicationRequest":
            return {"error": "Invalid resourceType, expected MedicationRequest"}, 400

        # 将FHIR数据转换为内部模型
        prescription_data = FHIRSerializer.fhir_to_prescription(fhir_data)

        # 创建处方
        try:
            prescription = PrescriptionService.create_prescription(**prescription_data)
            fhir_response = FHIRSerializer.prescription_to_fhir(prescription)
            response = jsonify(fhir_response)
            response.status_code = 201
            return response
        except Exception as e:
            return {"error": str(e)}, 400


class PatientResource(Resource):
    """FHIR Patient资源 (患者)"""

    def get(self, patient_id=None):
        """获取患者资源"""
        if patient_id:
            # 获取单个患者
            patient = PatientModel.query.get_or_404(patient_id)
            fhir_resource = FHIRSerializer.patient_to_fhir(patient)
            return jsonify(fhir_resource)
        else:
            # 获取所有患者(Bundle资源)
            patients = PatientModel.query.all()
            entries = [{
                "fullUrl": f"http://localhost:5050/fhir/Patient/{p.patient_id}",
                "resource": FHIRSerializer.patient_to_fhir(p)
            } for p in patients]

            bundle = {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": len(patients),
                "entry": entries
            }
            return jsonify(bundle)


class PractitionerResource(Resource):
    """FHIR Practitioner资源 (医生)"""

    def get(self, doctor_id=None):
        """获取医生资源"""
        if doctor_id:
            # 获取单个医生
            doctor = DoctorModel.query.get_or_404(doctor_id)
            fhir_resource = FHIRSerializer.doctor_to_fhir(doctor)
            return jsonify(fhir_resource)
        else:
            # 获取所有医生(Bundle资源)
            doctors = DoctorModel.query.all()
            entries = [{
                "fullUrl": f"http://localhost:5050/fhir/Practitioner/{d.doctor_id}",
                "resource": FHIRSerializer.doctor_to_fhir(d)
            } for d in doctors]

            bundle = {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": len(doctors),
                "entry": entries
            }
            return jsonify(bundle)


class TaskResource(Resource):
    """FHIR Task资源 (任务)"""

    def get(self, task_id=None):
        """获取任务资源"""
        if task_id:
            # 获取单个任务
            task = TaskModel.query.get_or_404(task_id)
            prescription = PrescriptionModel.query.get(task.prescription_id)
            fhir_resource = FHIRSerializer.task_to_fhir(task, prescription)
            return jsonify(fhir_resource)
        else:
            # 获取所有任务(Bundle资源)
            tasks = TaskModel.query.all()
            entries = []
            for t in tasks:
                prescription = PrescriptionModel.query.get(t.prescription_id)
                entries.append({
                    "fullUrl": f"http://localhost:5050/fhir/Task/{t.task_id}",
                    "resource": FHIRSerializer.task_to_fhir(t, prescription)
                })

            bundle = {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": len(tasks),
                "entry": entries
            }
            return jsonify(bundle)


class CapabilityStatementResource(Resource):
    """FHIR CapabilityStatement资源 (服务器能力声明)"""

    def get(self):
        """返回FHIR服务器的能力声明"""
        capability = {
            "resourceType": "CapabilityStatement",
            "status": "active",
            "date": "2025-10-04",
            "kind": "instance",
            "software": {
                "name": "SDDB FHIR Server",
                "version": "1.0.0"
            },
            "implementation": {
                "description": "SDDB智能中药代煎系统 FHIR接口",
                "url": "http://localhost:5050/fhir"
            },
            "fhirVersion": "4.0.1",
            "format": ["json"],
            "rest": [{
                "mode": "server",
                "resource": [
                    {
                        "type": "MedicationRequest",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"},
                            {"code": "create"}
                        ]
                    },
                    {
                        "type": "Patient",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"}
                        ]
                    },
                    {
                        "type": "Practitioner",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"}
                        ]
                    },
                    {
                        "type": "Task",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"}
                        ]
                    }
                ]
            }]
        }
        return jsonify(capability)
