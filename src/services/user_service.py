from models import UserModel, PatientModel, DoctorModel, WorkerModel, AdminModel
from exts import db

class UserService:
    @staticmethod
    def create_user(username, password, role, role_data):
        """创建用户及其角色信息"""
        # 检查用户名是否已存在
        existing_user = UserModel.query.filter_by(username=username).first()
        if existing_user:
            raise ValueError(f"用户名 {username} 已存在，请选择其他用户名!")

        # 根据角色创建相应的角色记录
        if role == 'patient':
            new_role = PatientModel(**role_data)
        elif role == 'doctor':
            new_role = DoctorModel(**role_data)
        elif role == 'worker':
            new_role = WorkerModel(**role_data)
        elif role == 'admin':
            new_role = AdminModel(**role_data)
        else:
            raise ValueError('角色类型错误!')

        db.session.add(new_role)
        db.session.flush()

        # 创建用户记录
        new_user = UserModel(
            username=username,
            password=password,
            role=role,
            role_id=new_role.patient_id if role == 'patient' else
                    new_role.doctor_id if role == 'doctor' else
                    new_role.worker_id if role == 'worker' else
                    new_role.admin_id
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user

    @staticmethod
    def delete_user(uuid):
        """删除用户及其角色信息"""
        user = UserModel.query.filter_by(uuid=uuid).first()
        if not user:
            raise ValueError("未找到用户")

        role = user.role
        role_id = user.role_id

        # 根据角色删除相应角色表数据
        if role == 'patient':
            patient = PatientModel.query.filter_by(patient_id=role_id).first()
            if patient:
                db.session.delete(patient)
        elif role == 'worker':
            worker = WorkerModel.query.filter_by(worker_id=role_id).first()
            if worker:
                db.session.delete(worker)
        elif role == 'admin':
            admin = AdminModel.query.filter_by(admin_id=role_id).first()
            if admin:
                db.session.delete(admin)

        # 删除用户
        db.session.delete(user)
        db.session.commit()
        return user.username

    @staticmethod
    def authenticate(username, password):
        """用户认证"""
        user = UserModel.query.filter_by(username=username, password=password).first()
        return user

    @staticmethod
    def get_role_info(user):
        """获取用户的角色详细信息"""
        if user.role == 'patient':
            return PatientModel.query.filter_by(patient_id=user.role_id).first()
        elif user.role == 'doctor':
            return DoctorModel.query.filter_by(doctor_id=user.role_id).first()
        elif user.role == 'worker':
            return WorkerModel.query.filter_by(worker_id=user.role_id).first()
        elif user.role == 'admin':
            return AdminModel.query.filter_by(admin_id=user.role_id).first()
        return None
