from flask import Flask, render_template, request, redirect, url_for, session, flash , jsonify
from datetime import datetime
import uuid
from models import UserModel,AdminModel,DoctorModel,WorkerModel,PatientModel,PrescriptionModel,TaskModel
import config
from exts import db

# 初始化应用
app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)

# 首页
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# 登录模块
@app.route('/login/', methods=['GET', 'POST'])
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
                session['role_id'] = user.role_id  # 存储患者 ID
            elif user.role == 'doctor':
                doctor = DoctorModel.query.filter_by(doctor_id=user.role_id).first()
                session['name'] = doctor.name if doctor else '未知医生'
                session['role_id'] = user.role_id  # 存储医生 ID
            elif user.role == 'worker':
                worker = WorkerModel.query.filter_by(worker_id=user.role_id).first()
                session['name'] = worker.name if worker else '未知工人'
                session['role_id'] = user.role_id  # 存储工人 ID
            elif user.role == 'admin':
                admin = AdminModel.query.filter_by(admin_id=user.role_id).first()
                session['name'] = admin.name if admin else '未知管理员'
                session['role_id'] = user.role_id  # 存储管理员 ID

            flash('登录成功!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误!', 'danger')
    return render_template('login.html')

# 注册模块
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 获取表单数据
        username = request.form.get('username')
        password = request.form.get('password', '123456')  # 默认密码
        name = request.form.get('name')
        gender = request.form.get('gender')
        age = request.form.get('age')
        contact_number = request.form.get('contact_number')

        # 验证角色（只能是患者）
        role = 'patient'

        # 检查用户名是否已存在
        existing_user = UserModel.query.filter_by(username=username).first()
        if existing_user:
            flash(f"用户名 {username} 已存在，请选择其他用户名!", 'danger')
            return redirect(url_for('register'))

        # 创建患者信息
        try:
            new_patient = PatientModel(name=name, gender=gender, age=age, contact_number=contact_number)
            db.session.add(new_patient)
            db.session.flush()  # 获取生成的 patient_id
            role_id = new_patient.patient_id

            # 创建用户（仅患者角色）
            new_user = UserModel(username=username, password=password, role=role, role_id=role_id)
            db.session.add(new_user)
            db.session.commit()

            flash(f"用户 {username} 注册成功! UUID: {new_user.uuid}, 角色: {role}, 角色ID: {role_id}", 'success')
            return redirect(url_for('login'))  # 注册成功后重定向到登录页面

        except Exception as e:
            db.session.rollback()
            flash(f"注册失败: {str(e)}", 'danger')
    return render_template('register.html')

# 注销模块
@app.route('/logout/')
def logout():
    session.clear()
    # flash('已注销!', 'info')
    flash(' ', 'info')
    return redirect(url_for('login'))

@app.route('/profile/')
def profile():
    if 'user_id' in session and session.get('role') == 'admin':
        admin_id = session.get('role_id')  # 获取管理员的 role_id
        admin = AdminModel.query.filter_by(admin_id=admin_id).first()

        if request.method == 'POST':
            # 修改管理员信息
            new_name = request.form.get('name')
            new_contact = request.form.get('contact_number')
            if admin:
                admin.name = new_name
                admin.contact_number = new_contact
                db.session.commit()
                flash('个人信息更新成功!', 'success')
                return redirect(url_for('admin_profile'))
            flash('管理员信息更新失败!', 'danger')

        if admin:
            return render_template('profile.html', role=admin)
        flash('管理员信息未找到!', 'danger')
    elif 'user_id' in session and session.get('role') == 'doctor':
        doctor_id = session.get('role_id')
        doctor = DoctorModel.query.filter_by(doctor_id=doctor_id).first()
        doctor_user = UserModel.query.filter_by(role_id=doctor_id, role='doctor').first()
        if request.method == 'POST':
            # 更新信息
            doctor.name = request.form.get('name')
            doctor.gender = request.form.get('gender')
            doctor.department = request.form.get('department')
            doctor.title = request.form.get('title')
            doctor.contact_number = request.form.get('contact_number')

            # 更新医生 ID
            department_code = {'内科': '01', '外科': '02', '儿科': '03', '妇科': '04'}.get(doctor.department, '00')
            title_code = {'主任医师': '01', '副主任医师': '02', '主治医师': '03', '住院医师': '04'}.get(doctor.title, '00')
            doctor_id_suffix = str(doctor.doctor_id)[-4:]  # 保留原 ID 的后四位
            doctor.doctor_id = int(department_code + title_code + doctor_id_suffix)

            db.session.commit()

            # 提示信息
            flash(
                f"信息更新成功! 新医生 ID: {doctor.doctor_id}, UUID: {doctor_user.uuid}, 姓名: {doctor.name}, 科室: {doctor.department}, 职称: {doctor.title}",
                'success'
            )
            return redirect(url_for('profile'))

        return render_template('profile.html', role=doctor)
    elif 'user_id' in session and session.get('role') == 'patient':
        patient_id = session.get('role_id')
        patient = PatientModel.query.filter_by(patient_id=patient_id).first()
        patient_user = UserModel.query.filter_by(role_id=patient_id, role='patient').first()

        if request.method == 'POST':
            # 更新信息
            patient.name = request.form.get('name')
            patient.gender = request.form.get('gender')
            patient.age = request.form.get('age')
            patient.contact_number = request.form.get('contact_number')

            db.session.commit()

            # 提示信息
            flash(
                f"信息更新成功! 患者 ID: {patient.patient_id}, UUID: {patient_user.uuid}, 姓名: {patient.name}, 年龄: {patient.age}",
                'success'
            )
            return redirect(url_for('profile'))

        return render_template('profile.html', role=patient)
    elif 'user_id' in session and session.get('role') == 'worker':
        # 获取工人 ID 并查询信息
        worker_id = session.get('role_id')
        worker = WorkerModel.query.filter_by(worker_id=worker_id).first()
        if worker:
            return render_template('profile.html', role=worker)
        flash('未找到工人信息!', 'danger')
        return redirect(url_for('dashboard'))
    else:
        flash('无权限访问!', 'danger')
        return redirect(url_for('dashboard'))

# 通用仪表盘
@app.route('/dashboard/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', role=session.get('role'))

# 用户管理/添加用户
@app.route('/admin/users/', methods=['GET', 'POST'])
def admin_users():
    if 'user_id' in session and session.get('role') == 'admin':
        selected_role = request.args.get('role', 'all')  # 获取筛选的角色，默认为 'all'
        search_username = request.args.get('username', '').strip()  # 获取搜索用户名，默认为空字符串
        page = int(request.args.get('page', 1))  # 获取当前页数，默认为第 1 页
        per_page = 10  # 每页显示用户数量

        if request.method == 'POST':
            # 添加新用户
            username = request.form.get('username')
            password = request.form.get('password', '123456')  # 默认密码
            role = request.form.get('role')

            try:
                if role == 'patient':
                    name = request.form.get('name')
                    gender = request.form.get('gender')
                    age = request.form.get('age')
                    contact_number = request.form.get('contact_number')
                    new_patient = PatientModel(name=name, gender=gender, age=age, contact_number=contact_number)
                    db.session.add(new_patient)
                    db.session.flush()  # 获取生成的 patient_id
                    role_id = new_patient.patient_id

                elif role == 'worker':
                    name = request.form.get('name')
                    age = request.form.get('age')
                    contact_number = request.form.get('contact_number')
                    new_worker = WorkerModel(name=name, age=age, contact_number=contact_number)
                    db.session.add(new_worker)
                    db.session.flush()  # 获取生成的 worker_id
                    role_id = new_worker.worker_id

                elif role == 'admin':
                    name = request.form.get('name')
                    contact_number = request.form.get('contact_number')
                    new_admin = AdminModel(name=name, contact_number=contact_number)
                    db.session.add(new_admin)
                    db.session.flush()  # 获取生成的 admin_id
                    role_id = new_admin.admin_id

                else:
                    flash('角色类型错误!', 'danger')
                    return redirect(url_for('admin_users'))

                existing_user = UserModel.query.filter_by(username=username).first()
                if existing_user:
                    flash(f"用户名 {username} 已存在，请选择其他用户名!", 'danger')
                    return redirect(url_for('admin_users'))

                new_user = UserModel(username=username, password=password, role=role, role_id=role_id)
                db.session.add(new_user)
                db.session.commit()
                flash(f"用户 {username} 添加成功! UUID: {new_user.uuid}, 角色: {role}, 角色ID: {role_id}", 'success')

            except Exception as e:
                db.session.rollback()
                flash(f"添加用户失败: {str(e)}", 'danger')

        # 构建查询语句
        query = UserModel.query

        # 按角色筛选
        if selected_role != 'all':
            query = query.filter_by(role=selected_role)

        # 按用户名模糊搜索
        if search_username:
            query = query.filter(UserModel.username.like(f"%{search_username}%"))

        # 获取总用户数
        total_users = query.count()

        # 分页处理
        users = query.order_by(UserModel.role, UserModel.role_id).offset((page - 1) * per_page).limit(per_page).all()
        total_pages = (total_users + per_page - 1) // per_page  # 计算总页数

        return render_template(
            'admin_users.html',
            users=users,
            selected_role=selected_role,
            search_username=search_username,
            current_page=page,
            total_pages=total_pages,  # 传递总页数到前端
        )
    else:
        flash('无权限访问!', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/admin/users/delete/<uuid>', methods=['POST'])
def delete_user(uuid):
    if 'user_id' in session and session.get('role') == 'admin':
        try:
            # 获取要删除的用户
            user = UserModel.query.filter_by(uuid=uuid).first()
            if user:
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
                flash(f"用户 {user.username} 已成功删除", 'success')
            else:
                flash("未找到用户", 'danger')

        except Exception as e:
            db.session.rollback()
            flash(f"删除失败: {str(e)}", 'danger')

    return redirect(url_for('admin_users'))

# 用户名查重
@app.route('/admin/users/validate_username', methods=['GET'])
def validate_username():
    username = request.args.get('username')
    existing_user = UserModel.query.filter_by(username=username).first()
    if existing_user:
        return {'valid': False, 'message': f"用户名 {username} 已存在"}
    return {'valid': True, 'message': f"用户名 {username} 可用"}

# 编辑用户
@app.route('/admin/users/edit/<uuid>', methods=['GET', 'POST'])
def edit_user(uuid):
    if 'user_id' in session and session.get('role') == 'admin':
        user = UserModel.query.get_or_404(uuid)

        # 获取具体角色的信息
        patient = PatientModel.query.filter_by(patient_id=user.role_id).first() if user.role == 'patient' else None
        doctor = DoctorModel.query.filter_by(doctor_id=user.role_id).first() if user.role == 'doctor' else None
        worker = WorkerModel.query.filter_by(worker_id=user.role_id).first() if user.role == 'worker' else None
        admin = AdminModel.query.filter_by(admin_id=user.role_id).first() if user.role == 'admin' else None

        if request.method == 'POST':
            # 修改用户信息
            user.username = request.form.get('username', user.username)
            user.password = request.form.get('password', user.password)

            # 修改对应角色信息
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
            return redirect(url_for('admin_users'))

        return render_template('edit_user.html', user=user, patient=patient, doctor=doctor, worker=worker, admin=admin)
    else:
        flash('无权限访问!', 'danger')
        return redirect(url_for('dashboard'))

# 分配任务
@app.route('/admin/assign_tasks', methods=['GET', 'POST'])
def assign_tasks():
    if 'user_id' in session and session.get('role') == 'admin':
        if request.method == 'POST':
            task_id = request.form.get('task_id')
            operation = request.form.get('operation')  # 'assign' or 'rollback'
            print(f"Received operation: {operation} for task_id: {task_id}")

            if operation == 'assign':
                worker_id = int(request.form.get('worker_id'))
                task_type = request.form.get('task_type')  # 'receive', 'formulate', 'decoction'

                # 获取任务和工人信息
                task = TaskModel.query.get_or_404(task_id)
                worker = WorkerModel.query.get_or_404(worker_id)

                # 检查任务分配规则
                print(f"Assigning task {task_id} to worker {worker_id} for task type {task_type}")

                if task_type == 'formulate' and not task.receive_time:
                    print("Error: Receive step not completed")
                    return jsonify({'success': False, 'message': '必须完成收方后才能分配配方任务!'})

                if task_type == 'decoction' and not task.form_time:
                    print("Error: Formulate step not completed")
                    return jsonify({'success': False, 'message': '必须完成配方后才能分配煎药任务!'})

                # 分配任务
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
                print(f"TaskModel {task_id} successfully assigned to {worker.name}")
                return jsonify({'success': True, 'message': f'任务 {task_id} 成功分配给工人 {worker.name}!'})

            elif operation == 'rollback':
                rollback_password = request.form.get('rollback_password')
                admin_user = UserModel.query.filter_by(uuid=session['user_id']).first()

                if not admin_user or admin_user.password != rollback_password:
                    return jsonify({'success': False, 'message': '操作密码错误! 无法执行回退操作。'})

                task = TaskModel.query.get_or_404(task_id)

                # 获取回退阶段
                rollback_phase = request.form.get('rollback_phase')

                # 回退逻辑
                if rollback_phase == 'receive' and task.receive_time:
                    task.receive_time = None
                    task.receive_worker_id = None
                    task.receive_worker_name = None
                    task.status = '未完成'  # 状态变为未完成
                    db.session.commit()
                    return jsonify({'success': True, 'message': f"任务 {task_id} 已成功回退到收方前!"})

                elif rollback_phase == 'formulate' and task.form_time:
                    task.form_time = None
                    task.form_worker_id = None
                    task.form_worker_name = None
                    db.session.commit()
                    return jsonify({'success': True, 'message': f"任务 {task_id} 已成功回退到配方前!"})

                # 检查并回退到其他阶段
                # ... (同样的逻辑可以应用于其他阶段)

                else:
                    return jsonify({'success': False, 'message': '无法回退到该阶段。'})

        # 查询任务统计信息
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

    flash('无权限访问!', 'danger')
    return redirect(url_for('dashboard'))

# 医生开处方
@app.route('/doctor/prescriptions/new/', methods=['GET', 'POST'])
def create_prescription():
    if 'user_id' in session and session.get('role') == 'doctor':
        doctor_id = session.get('role_id')  # 使用 role_id 确保匹配 doctor_id

        if request.method == 'POST':
            # 获取表单数据
            patient_id = request.form.get('patient_id')
            amount = request.form.get('amount')
            usage_instructions = request.form.get('usage_instructions')

            # 创建新处方
            new_prescription = PrescriptionModel(
                patient_id=patient_id,
                doctor_id=doctor_id,
                amount=amount,
                usage_instructions=usage_instructions,
                status='待配方'  # 默认状态
            )
            db.session.add(new_prescription)
            db.session.commit()  # 这里提交事务，生成处方ID

            # 获取新生成的处方ID
            prescription_id = new_prescription.prescription_id

            # 创建新任务，仅填写处方id，其他为空
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
                status='未完成'  # 默认任务状态
            )
            db.session.add(new_task)
            db.session.commit()  # 提交任务数据

            flash('处方创建成功，并已生成任务!', 'success')
            return redirect(url_for('doctor_prescriptions'))

        # 获取所有患者信息（供下拉选择患者）
        patients = PatientModel.query.all()
        return render_template('create_prescription.html', patients=patients)

    else:
        flash('无权限访问!', 'danger')
        return redirect(url_for('dashboard'))

# 医生查看处方
@app.route('/doctor/prescriptions/')
def doctor_prescriptions():
    if 'user_id' in session and session.get('role') == 'doctor':
        doctor_id = session.get('role_id')  # 使用 role_id 进行匹配
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
    else:
        flash('无权限访问!', 'danger')
    return redirect(url_for('dashboard'))

# 医生查看处方详情
@app.route('/doctor/prescriptions/view/<int:prescription_id>', methods=['GET'])
def doctor_prescription_detail(prescription_id):
    if 'user_id' in session and session.get('role') == 'doctor':
        # 获取医生 ID 并验证
        doctor_id = session.get('role_id')
        prescription = PrescriptionModel.query.filter_by(prescription_id=prescription_id, doctor_id=doctor_id).first()
        if prescription:
            # 查询任务信息
            task = TaskModel.query.filter_by(prescription_id=prescription_id).first()
            return render_template('doctor_prescription_detail.html', prescription=prescription, task=task)
        flash('未找到该处方或无权限查看!', 'danger')
        return redirect(url_for('doctor_prescriptions'))
    flash('无权限访问!', 'danger')
    return redirect(url_for('dashboard'))

# 患者查看处方
@app.route('/patient/prescriptions/', methods=['GET'])
def patient_prescriptions():
    if 'user_id' in session and session.get('role') == 'patient':
        patient_id = session.get('role_id')  # role_id 对应 patient_id
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
    else:
        flash('无权限访问!', 'danger')
    return redirect(url_for('dashboard'))


# 患者查看处方详情
@app.route('/patient/prescriptions/view/<int:prescription_id>', methods=['GET'])
def patient_prescription_detail(prescription_id):
    if 'user_id' in session and session.get('role') == 'patient':
        # 获取患者 ID 并验证
        patient_id = session.get('role_id')
        prescription = PrescriptionModel.query.filter_by(prescription_id=prescription_id, patient_id=patient_id).first()
        if prescription:
            # 查询任务信息
            task = TaskModel.query.filter_by(prescription_id=prescription_id).first()
            return render_template('patient_prescription_detail.html', prescription=prescription, task=task)
        flash('未找到该处方或无权限查看!', 'danger')
        return redirect(url_for('patient_prescriptions'))
    flash('无权限访问!', 'danger')
    return redirect(url_for('dashboard'))

# 工作人员查看任务
@app.route('/worker/tasks', methods=['GET'])
def worker_tasks():
    if 'user_id' in session and session.get('role') == 'worker':
        worker_id = int(session.get('role_id'))
        tasks = TaskModel.query.filter(
            (TaskModel.receive_worker_id == worker_id) |
            (TaskModel.form_worker_id == worker_id) |
            (TaskModel.decoction_worker_id == worker_id)
        ).all()
        return render_template('worker_tasks.html', tasks=tasks)

    flash('无权限访问!', 'danger')
    return redirect(url_for('dashboard'))

# 工作人员更新任务状态
@app.route('/worker/tasks/update/<int:task_id>', methods=['GET', 'POST'])
def update_task_status(task_id):
    if 'user_id' in session and session.get('role') == 'worker':
        worker_id = int(session.get('role_id'))  # 当前工人 ID
        task = TaskModel.query.get_or_404(task_id)

        # 如果任务已完成，直接跳回任务列表
        if task.status == '完成':
            flash('任务已完成，无法继续更新状态!', 'info')
            return redirect(url_for('worker_tasks'))

        # 验证任务是否分配给当前工人
        if task.receive_worker_id != worker_id and task.form_worker_id != worker_id and task.decoction_worker_id != worker_id:
            flash('无权限操作此任务!', 'danger')
            return redirect(url_for('worker_tasks'))

        if request.method == 'POST':
            action = request.form.get('action')

            # 更新任务状态逻辑
            if action == 'receive' and task.receive_worker_id == worker_id and not task.receive_time:
                task.receive_time = datetime.utcnow()
            elif action == 'formulate' and task.form_worker_id == worker_id and task.receive_time and not task.form_time:
                task.form_time = datetime.utcnow()
            elif action == 'decoction_start' and task.decoction_worker_id == worker_id and task.form_time and not task.decoction_start_time:
                task.decoction_start_time = datetime.utcnow()
            elif action == 'decoction_end' and task.decoction_worker_id == worker_id and task.decoction_start_time and not task.decoction_end_time:
                task.decoction_end_time = datetime.utcnow()
                task.status = '完成'
            else:
                flash('当前任务未满足操作条件，无法完成此操作。', 'warning')
                return redirect(url_for('update_task_status', task_id=task_id))

            db.session.commit()
            flash('任务状态更新成功!', 'success')
            return redirect(url_for('worker_tasks'))

        return render_template('update_task.html', task=task)

    flash('无权限访问!', 'danger')
    return redirect(url_for('dashboard'))

# 初始化数据库
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建所有表
    app.run(debug=True,host='0.0.0.0',port=5050)