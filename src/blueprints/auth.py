from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import UserModel, AdminModel, DoctorModel, WorkerModel, PatientModel
from exts import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = UserModel.query.filter_by(username=username, password=password).first()

        if user:  # 用户验证成功
            session['user_id'] = user.uuid
            session['role'] = user.role
            session['username'] = user.username

            # 根据角色设置角色相关的 session 信息
            if user.role == 'patient':
                patient = PatientModel.query.filter_by(patient_id=user.role_id).first()
                session['name'] = patient.name if patient else '未知患者'
                session['role_id'] = user.role_id
            elif user.role == 'doctor':
                doctor = DoctorModel.query.filter_by(doctor_id=user.role_id).first()
                session['name'] = doctor.name if doctor else '未知医生'
                session['role_id'] = user.role_id
            elif user.role == 'worker':
                worker = WorkerModel.query.filter_by(worker_id=user.role_id).first()
                session['name'] = worker.name if worker else '未知工人'
                session['role_id'] = user.role_id
            elif user.role == 'admin':
                admin = AdminModel.query.filter_by(admin_id=user.role_id).first()
                session['name'] = admin.name if admin else '未知管理员'
                session['role_id'] = user.role_id

            flash('登录成功!', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('用户名或密码错误!', 'danger')
    return render_template('login.html')

@auth_bp.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password', '123456')
        name = request.form.get('name')
        gender = request.form.get('gender')
        age = request.form.get('age')
        contact_number = request.form.get('contact_number')
        role = 'patient'

        existing_user = UserModel.query.filter_by(username=username).first()
        if existing_user:
            flash(f"用户名 {username} 已存在，请选择其他用户名!", 'danger')
            return redirect(url_for('auth.register'))

        try:
            new_patient = PatientModel(name=name, gender=gender, age=age, contact_number=contact_number)
            db.session.add(new_patient)
            db.session.flush()
            role_id = new_patient.patient_id

            new_user = UserModel(username=username, password=password, role=role, role_id=role_id)
            db.session.add(new_user)
            db.session.commit()

            flash(f"用户 {username} 注册成功! UUID: {new_user.uuid}, 角色: {role}, 角色ID: {role_id}", 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f"注册失败: {str(e)}", 'danger')
    return render_template('register.html')

@auth_bp.route('/logout/')
def logout():
    session.clear()
    flash(' ', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', role=session.get('role'))

@auth_bp.route('/profile/', methods=['GET', 'POST'])
def profile():
    if 'user_id' in session and session.get('role') == 'admin':
        admin_id = session.get('role_id')
        admin = AdminModel.query.filter_by(admin_id=admin_id).first()

        if request.method == 'POST':
            new_name = request.form.get('name')
            new_contact = request.form.get('contact_number')
            if admin:
                admin.name = new_name
                admin.contact_number = new_contact
                db.session.commit()
                flash('个人信息更新成功!', 'success')
                return redirect(url_for('auth.profile'))
            flash('管理员信息更新失败!', 'danger')

        if admin:
            return render_template('profile.html', role=admin)
        flash('管理员信息未找到!', 'danger')
    elif 'user_id' in session and session.get('role') == 'doctor':
        doctor_id = session.get('role_id')
        doctor = DoctorModel.query.filter_by(doctor_id=doctor_id).first()
        doctor_user = UserModel.query.filter_by(role_id=doctor_id, role='doctor').first()
        if request.method == 'POST':
            doctor.name = request.form.get('name')
            doctor.gender = request.form.get('gender')
            doctor.department = request.form.get('department')
            doctor.title = request.form.get('title')
            doctor.contact_number = request.form.get('contact_number')

            department_code = {'内科': '01', '外科': '02', '儿科': '03', '妇科': '04'}.get(doctor.department, '00')
            title_code = {'主任医师': '01', '副主任医师': '02', '主治医师': '03', '住院医师': '04'}.get(doctor.title, '00')
            doctor_id_suffix = str(doctor.doctor_id)[-4:]
            doctor.doctor_id = int(department_code + title_code + doctor_id_suffix)

            db.session.commit()

            flash(
                f"信息更新成功! 新医生 ID: {doctor.doctor_id}, UUID: {doctor_user.uuid}, 姓名: {doctor.name}, 科室: {doctor.department}, 职称: {doctor.title}",
                'success'
            )
            return redirect(url_for('auth.profile'))

        return render_template('profile.html', role=doctor)
    elif 'user_id' in session and session.get('role') == 'patient':
        patient_id = session.get('role_id')
        patient = PatientModel.query.filter_by(patient_id=patient_id).first()
        patient_user = UserModel.query.filter_by(role_id=patient_id, role='patient').first()

        if request.method == 'POST':
            patient.name = request.form.get('name')
            patient.gender = request.form.get('gender')
            patient.age = request.form.get('age')
            patient.contact_number = request.form.get('contact_number')

            db.session.commit()

            flash(
                f"信息更新成功! 患者 ID: {patient.patient_id}, UUID: {patient_user.uuid}, 姓名: {patient.name}, 年龄: {patient.age}",
                'success'
            )
            return redirect(url_for('auth.profile'))

        return render_template('profile.html', role=patient)
    elif 'user_id' in session and session.get('role') == 'worker':
        worker_id = session.get('role_id')
        worker = WorkerModel.query.filter_by(worker_id=worker_id).first()

        if request.method == 'POST':
            if worker:
                worker.name = request.form.get('name')
                worker.age = request.form.get('age')
                worker.contact_number = request.form.get('contact_number')

                db.session.commit()

                flash(f"信息更新成功! 工人 ID: {worker.worker_id}, 姓名: {worker.name}, 年龄: {worker.age}", 'success')
                return redirect(url_for('auth.profile'))
            flash('工人信息更新失败!', 'danger')

        if worker:
            return render_template('profile.html', role=worker)
        flash('未找到工人信息!', 'danger')
        return redirect(url_for('auth.dashboard'))
    else:
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))
