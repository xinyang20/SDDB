from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import PatientModel, PrescriptionModel, TaskModel
from exts import db

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/prescriptions/new/', methods=['GET', 'POST'])
def create_prescription():
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    doctor_id = session.get('role_id')

    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        amount = request.form.get('amount')
        usage_instructions = request.form.get('usage_instructions')

        new_prescription = PrescriptionModel(
            patient_id=patient_id,
            doctor_id=doctor_id,
            amount=amount,
            usage_instructions=usage_instructions,
            status='待配方'
        )
        db.session.add(new_prescription)
        db.session.commit()

        prescription_id = new_prescription.prescription_id

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

        flash('处方创建成功，并已生成任务!', 'success')
        return redirect(url_for('doctor.prescriptions'))

    patients = PatientModel.query.all()
    return render_template('create_prescription.html', patients=patients)

@doctor_bp.route('/prescriptions/')
def prescriptions():
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    doctor_id = session.get('role_id')
    if doctor_id:
        prescriptions = PrescriptionModel.query.filter_by(doctor_id=doctor_id).all()
        prescriptions_with_status = []
        for prescription in prescriptions:
            task = TaskModel.query.filter_by(prescription_id=prescription.prescription_id).first()
            if not task:
                status = "未分配任务"
            elif not task.receive_time:
                status = "待收方"
            elif not task.form_time:
                status = "待配方"
            elif not task.decoction_start_time:
                status = "待煎药"
            elif not task.decoction_end_time:
                status = "煎药中"
            else:
                status = "已完成"
            prescriptions_with_status.append({
                "prescription": prescription,
                "status": status
            })
        return render_template('doctor_prescriptions.html', prescriptions=prescriptions_with_status)
    flash('未找到医生信息!', 'danger')
    return redirect(url_for('auth.dashboard'))

@doctor_bp.route('/prescriptions/view/<int:prescription_id>', methods=['GET'])
def prescription_detail(prescription_id):
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    doctor_id = session.get('role_id')
    prescription = PrescriptionModel.query.filter_by(prescription_id=prescription_id, doctor_id=doctor_id).first()
    if prescription:
        task = TaskModel.query.filter_by(prescription_id=prescription_id).first()
        return render_template('doctor_prescription_detail.html', prescription=prescription, task=task)
    flash('未找到该处方或无权限查看!', 'danger')
    return redirect(url_for('doctor.prescriptions'))
