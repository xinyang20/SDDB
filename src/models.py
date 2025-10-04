from exts import db
from datetime import datetime
import uuid

# 数据库模型
class UserModel(db.Model):
    __tablename__ = 'users'
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    role_id = db.Column(db.Integer)

class PatientModel(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    contact_number = db.Column(db.String(15))

class DoctorModel(db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    department = db.Column(db.String(50))
    title = db.Column(db.String(50))
    contact_number = db.Column(db.String(15))

class WorkerModel(db.Model):
    __tablename__ = 'workers'
    worker_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    contact_number = db.Column(db.String(15))

class AdminModel(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    contact_number = db.Column(db.String(15))

class PrescriptionModel(db.Model):
    __tablename__ = 'prescriptions'
    prescription_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float)
    usage_instructions = db.Column(db.Text)
    status = db.Column(db.String(20), default='待配方')
    expected_pickup_time = db.Column(db.DateTime)

class TaskModel(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.prescription_id'))
    receive_worker_id = db.Column(db.Integer, db.ForeignKey('workers.worker_id'))
    receive_worker_name = db.Column(db.String(50))
    form_worker_id = db.Column(db.Integer, db.ForeignKey('workers.worker_id'))
    form_worker_name = db.Column(db.String(50))
    decoction_worker_id = db.Column(db.Integer, db.ForeignKey('workers.worker_id'))
    decoction_worker_name = db.Column(db.String(50))
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.admin_id'))
    admin_name = db.Column(db.String(50))
    receive_time = db.Column(db.DateTime)
    form_time = db.Column(db.DateTime)
    decoction_start_time = db.Column(db.DateTime)
    decoction_end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='未完成')

class AlertModel(db.Model):
    """告警记录模型"""
    __tablename__ = 'alerts'
    alert_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # timeout, abnormal_fast, backlog, low_efficiency
    level = db.Column(db.String(20), nullable=False)  # high, medium, low
    message = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.worker_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)