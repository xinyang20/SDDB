#!/usr/bin/env python3
"""
数据库初始化脚本
创建SQLite数据库并添加示例数据
使用方法：python init_db.py
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from models import (
    UserModel, PatientModel, DoctorModel, WorkerModel, 
    AdminModel, PrescriptionModel, TaskModel
)
from exts import db
import config

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config)
    return app

def init_database():
    """初始化数据库"""
    print("正在初始化SQLite数据库...")
    
    app = create_app()
    db.init_app(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建完成！")
        
        # 检查是否已有数据
        if UserModel.query.first():
            print("数据库中已存在数据，跳过示例数据创建")
            return
        
        # 创建示例数据
        create_sample_data()

def create_sample_data():
    """创建示例数据"""
    print("正在创建示例数据...")
    
    app = create_app()
    db.init_app(app)
    
    with app.app_context():
        try:
            # 创建示例管理员
            admin = AdminModel(name="系统管理员", contact_number="13800138000")
            db.session.add(admin)
            db.session.flush()
            
            admin_user = UserModel(
                username="admin",
                password="admin123",
                role="admin",
                role_id=admin.admin_id
            )
            db.session.add(admin_user)
            
            # 创建示例医生
            doctor = DoctorModel(
                name="张医生",
                gender="男",
                department="内科",
                title="主治医师",
                contact_number="13800138001"
            )
            db.session.add(doctor)
            db.session.flush()
            
            doctor_user = UserModel(
                username="doctor1",
                password="123456",
                role="doctor",
                role_id=doctor.doctor_id
            )
            db.session.add(doctor_user)
            
            # 创建示例患者
            patient = PatientModel(
                name="李患者",
                gender="女",
                age=35,
                contact_number="13800138002"
            )
            db.session.add(patient)
            db.session.flush()
            
            patient_user = UserModel(
                username="patient1",
                password="123456",
                role="patient",
                role_id=patient.patient_id
            )
            db.session.add(patient_user)
            
            # 创建示例工人
            worker = WorkerModel(
                name="王工人",
                age=28,
                contact_number="13800138003"
            )
            db.session.add(worker)
            db.session.flush()
            
            worker_user = UserModel(
                username="worker1",
                password="123456",
                role="worker",
                role_id=worker.worker_id
            )
            db.session.add(worker_user)
            
            # 提交所有更改
            db.session.commit()
            
            print("示例数据创建完成！")
            print("\n默认测试账户：")
            print("  管理员: admin / admin123")
            print("  医生: doctor1 / 123456")
            print("  患者: patient1 / 123456")
            print("  工人: worker1 / 123456")
            
        except Exception as e:
            db.session.rollback()
            print(f"创建示例数据失败: {e}")
            raise

if __name__ == "__main__":
    print("=== 数据库初始化工具 ===")
    print("初始化SQLite数据库并创建示例数据")
    print()
    
    try:
        init_database()
        print("\n数据库初始化完成！现在可以运行应用了。")
        print("运行命令: python app.py")
    except Exception as e:
        print(f"初始化失败: {e}")
        sys.exit(1)
