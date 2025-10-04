from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import PrescriptionModel, TaskModel
from exts import db

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/prescriptions/', methods=['GET'])
def prescriptions():
    if 'user_id' not in session or session.get('role') != 'patient':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    patient_id = session.get('role_id')
    if patient_id:
        prescriptions = PrescriptionModel.query.filter_by(patient_id=patient_id).all()
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
        return render_template('patient_prescriptions.html', prescriptions=prescriptions_with_status)
    flash('未找到患者信息!', 'danger')
    return redirect(url_for('auth.dashboard'))

@patient_bp.route('/prescriptions/view/<int:prescription_id>', methods=['GET'])
def prescription_detail(prescription_id):
    if 'user_id' not in session or session.get('role') != 'patient':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    patient_id = session.get('role_id')
    prescription = PrescriptionModel.query.filter_by(prescription_id=prescription_id, patient_id=patient_id).first()
    if prescription:
        task = TaskModel.query.filter_by(prescription_id=prescription_id).first()
        return render_template('patient_prescription_detail.html', prescription=prescription, task=task)
    flash('未找到该处方或无权限查看!', 'danger')
    return redirect(url_for('patient.prescriptions'))
