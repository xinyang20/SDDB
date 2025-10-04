from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import UserModel, AdminModel, DoctorModel, WorkerModel, PatientModel, TaskModel, AlertModel
from alerts.notifiers import mark_alert_read, resolve_alert, get_unread_alerts, get_recent_alerts
from exts import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
    """管理员实时数据看板"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))
    return render_template('admin_dashboard.html')

@admin_bp.route('/users/', methods=['GET', 'POST'])
def users():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    selected_role = request.args.get('role', 'all')
    search_username = request.args.get('username', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 10

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password', '123456')
        role = request.form.get('role')

        try:
            if role == 'patient':
                name = request.form.get('name')
                gender = request.form.get('gender')
                age = request.form.get('age')
                contact_number = request.form.get('contact_number')
                new_patient = PatientModel(name=name, gender=gender, age=age, contact_number=contact_number)
                db.session.add(new_patient)
                db.session.flush()
                role_id = new_patient.patient_id

            elif role == 'worker':
                name = request.form.get('name')
                age = request.form.get('age')
                contact_number = request.form.get('contact_number')
                new_worker = WorkerModel(name=name, age=age, contact_number=contact_number)
                db.session.add(new_worker)
                db.session.flush()
                role_id = new_worker.worker_id

            elif role == 'admin':
                name = request.form.get('name')
                contact_number = request.form.get('contact_number')
                new_admin = AdminModel(name=name, contact_number=contact_number)
                db.session.add(new_admin)
                db.session.flush()
                role_id = new_admin.admin_id

            else:
                flash('角色类型错误!', 'danger')
                return redirect(url_for('admin.users'))

            existing_user = UserModel.query.filter_by(username=username).first()
            if existing_user:
                flash(f"用户名 {username} 已存在，请选择其他用户名!", 'danger')
                return redirect(url_for('admin.users'))

            new_user = UserModel(username=username, password=password, role=role, role_id=role_id)
            db.session.add(new_user)
            db.session.commit()
            flash(f"用户 {username} 添加成功! UUID: {new_user.uuid}, 角色: {role}, 角色ID: {role_id}", 'success')

        except Exception as e:
            db.session.rollback()
            flash(f"添加用户失败: {str(e)}", 'danger')

    query = UserModel.query
    if selected_role != 'all':
        query = query.filter_by(role=selected_role)
    if search_username:
        query = query.filter(UserModel.username.like(f"%{search_username}%"))

    total_users = query.count()
    users = query.order_by(UserModel.role, UserModel.role_id).offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total_users + per_page - 1) // per_page

    return render_template(
        'admin_users.html',
        users=users,
        selected_role=selected_role,
        search_username=search_username,
        current_page=page,
        total_pages=total_pages,
    )

@admin_bp.route('/users/delete/<uuid>', methods=['POST'])
def delete_user(uuid):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    try:
        user = UserModel.query.filter_by(uuid=uuid).first()
        if user:
            role = user.role
            role_id = user.role_id

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

            db.session.delete(user)
            db.session.commit()
            flash(f"用户 {user.username} 已成功删除", 'success')
        else:
            flash("未找到用户", 'danger')

    except Exception as e:
        db.session.rollback()
        flash(f"删除失败: {str(e)}", 'danger')

    return redirect(url_for('admin.users'))

@admin_bp.route('/users/validate_username', methods=['GET'])
def validate_username():
    username = request.args.get('username')
    existing_user = UserModel.query.filter_by(username=username).first()
    if existing_user:
        return {'valid': False, 'message': f"用户名 {username} 已存在"}
    return {'valid': True, 'message': f"用户名 {username} 可用"}

@admin_bp.route('/users/edit/<uuid>', methods=['GET', 'POST'])
def edit_user(uuid):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    user = UserModel.query.get_or_404(uuid)

    patient = PatientModel.query.filter_by(patient_id=user.role_id).first() if user.role == 'patient' else None
    doctor = DoctorModel.query.filter_by(doctor_id=user.role_id).first() if user.role == 'doctor' else None
    worker = WorkerModel.query.filter_by(worker_id=user.role_id).first() if user.role == 'worker' else None
    admin = AdminModel.query.filter_by(admin_id=user.role_id).first() if user.role == 'admin' else None

    if request.method == 'POST':
        user.username = request.form.get('username', user.username)
        user.password = request.form.get('password', user.password)

        if user.role == 'patient' and patient:
            patient.name = request.form.get('patient_name', patient.name)
            patient.gender = request.form.get('patient_gender', patient.gender)
            patient.age = request.form.get('patient_age', patient.age)
            patient.contact_number = request.form.get('patient_contact', patient.contact_number)
        elif user.role == 'doctor' and doctor:
            doctor.name = request.form.get('doctor_name', doctor.name)
            doctor.gender = request.form.get('doctor_gender', doctor.gender)
            doctor.department = request.form.get('doctor_department', doctor.department)
            doctor.title = request.form.get('doctor_title', doctor.title)
            doctor.contact_number = request.form.get('doctor_contact', doctor.contact_number)
        elif user.role == 'worker' and worker:
            worker.name = request.form.get('worker_name', worker.name)
            worker.age = request.form.get('worker_age', worker.age)
            worker.contact_number = request.form.get('worker_contact', worker.contact_number)
        elif user.role == 'admin' and admin:
            admin.name = request.form.get('admin_name', admin.name)
            admin.contact_number = request.form.get('admin_contact', admin.contact_number)

        db.session.commit()
        flash(f"用户 {user.username} 更新成功!", 'success')
        return redirect(url_for('admin.users'))

    return render_template('edit_user.html', user=user, patient=patient, doctor=doctor, worker=worker, admin=admin)

@admin_bp.route('/assign_tasks', methods=['GET', 'POST'])
def assign_tasks():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        task_id = request.form.get('task_id')
        operation = request.form.get('operation')

        if operation == 'assign':
            worker_id = int(request.form.get('worker_id'))
            task_type = request.form.get('task_type')

            task = TaskModel.query.get_or_404(task_id)
            worker = WorkerModel.query.get_or_404(worker_id)

            if task_type == 'formulate' and not task.receive_time:
                return jsonify({'success': False, 'message': '必须完成收方后才能分配配方任务!'})

            if task_type == 'decoction' and not task.form_time:
                return jsonify({'success': False, 'message': '必须完成配方后才能分配煎药任务!'})

            if task_type == 'receive':
                task.receive_worker_id = worker_id
                task.receive_worker_name = worker.name
            elif task_type == 'formulate':
                task.form_worker_id = worker_id
                task.form_worker_name = worker.name
            elif task_type == 'decoction':
                task.decoction_worker_id = worker_id
                task.decoction_worker_name = worker.name

            db.session.commit()
            return jsonify({'success': True, 'message': f'任务 {task_id} 成功分配给工人 {worker.name}!'})

        elif operation == 'rollback':
            rollback_password = request.form.get('rollback_password')
            admin_user = UserModel.query.filter_by(uuid=session['user_id']).first()

            if not admin_user or admin_user.password != rollback_password:
                return jsonify({'success': False, 'message': '操作密码错误! 无法执行回退操作。'})

            task = TaskModel.query.get_or_404(task_id)
            rollback_phase = request.form.get('rollback_phase')

            if rollback_phase == 'receive' and task.receive_time:
                task.receive_time = None
                task.receive_worker_id = None
                task.receive_worker_name = None
                task.status = '未完成'
                db.session.commit()
                return jsonify({'success': True, 'message': f"任务 {task_id} 已成功回退到收方前!"})

            elif rollback_phase == 'formulate' and task.form_time:
                task.form_time = None
                task.form_worker_id = None
                task.form_worker_name = None
                db.session.commit()
                return jsonify({'success': True, 'message': f"任务 {task_id} 已成功回退到配方前!"})

            else:
                return jsonify({'success': False, 'message': '无法回退到该阶段。'})

    unfinished_tasks = TaskModel.query.filter(TaskModel.status != '完成').count()
    finished_tasks = TaskModel.query.filter(TaskModel.status == '完成').count()

    stats = {'unfinished_orders': unfinished_tasks, 'finished_orders': finished_tasks}

    tasks = TaskModel.query.order_by(TaskModel.status.desc(), TaskModel.task_id.asc()).all()
    for task in tasks:
        if task.decoction_end_time:
            task.phase_status = "煎药已完成"
        elif task.decoction_start_time:
            task.phase_status = "煎药进行中"
        elif task.form_time:
            task.phase_status = "配方已完成，煎药未完成"
        elif task.receive_time:
            task.phase_status = "收方已完成，配方未完成"
        else:
            task.phase_status = "收方未完成"

    workers = WorkerModel.query.all()
    return render_template('assign_tasks.html', tasks=tasks, workers=workers, stats=stats)

@admin_bp.route('/alerts')
def alerts():
    """告警管理页面"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    # 获取最近24小时的告警
    recent_alerts = get_recent_alerts(hours=24, limit=100)
    unread_count = AlertModel.query.filter_by(is_read=False).count()

    return render_template('admin_alerts.html', alerts=recent_alerts, unread_count=unread_count)

@admin_bp.route('/alerts/mark_read/<int:alert_id>', methods=['POST'])
def mark_alert_as_read(alert_id):
    """标记告警为已读"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '无权限'}), 403

    alert = mark_alert_read(alert_id)
    if alert:
        return jsonify({'success': True, 'message': '已标记为已读'})
    return jsonify({'success': False, 'message': '告警不存在'}), 404

@admin_bp.route('/alerts/resolve/<int:alert_id>', methods=['POST'])
def resolve_alert_route(alert_id):
    """解决告警"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '无权限'}), 403

    alert = resolve_alert(alert_id)
    if alert:
        return jsonify({'success': True, 'message': '告警已解决'})
    return jsonify({'success': False, 'message': '告警不存在'}), 404

@admin_bp.route('/alerts/unread')
def get_unread_alerts_api():
    """获取未读告警（API）"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '无权限'}), 403

    alerts = get_unread_alerts()
    alerts_data = [{
        'alert_id': a.alert_id,
        'type': a.type,
        'level': a.level,
        'message': a.message,
        'task_id': a.task_id,
        'worker_id': a.worker_id,
        'created_at': a.created_at.isoformat()
    } for a in alerts]

    return jsonify({'success': True, 'alerts': alerts_data, 'count': len(alerts_data)})
