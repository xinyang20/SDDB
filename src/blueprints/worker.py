from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from models import TaskModel
from exts import db

worker_bp = Blueprint('worker', __name__, url_prefix='/worker')

@worker_bp.route('/tasks', methods=['GET'])
def tasks():
    if 'user_id' not in session or session.get('role') != 'worker':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    worker_id = int(session.get('role_id'))
    tasks = TaskModel.query.filter(
        (TaskModel.receive_worker_id == worker_id) |
        (TaskModel.form_worker_id == worker_id) |
        (TaskModel.decoction_worker_id == worker_id)
    ).all()
    return render_template('worker_tasks.html', tasks=tasks)

@worker_bp.route('/tasks/update/<int:task_id>', methods=['GET', 'POST'])
def update_task_status(task_id):
    if 'user_id' not in session or session.get('role') != 'worker':
        flash('无权限访问!', 'danger')
        return redirect(url_for('auth.dashboard'))

    worker_id = int(session.get('role_id'))
    task = TaskModel.query.get_or_404(task_id)

    if task.status == '完成':
        flash('任务已完成，无法继续更新状态!', 'info')
        return redirect(url_for('worker.tasks'))

    if task.receive_worker_id != worker_id and task.form_worker_id != worker_id and task.decoction_worker_id != worker_id:
        flash('无权限操作此任务!', 'danger')
        return redirect(url_for('worker.tasks'))

    if request.method == 'POST':
        action = request.form.get('action')

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
            return redirect(url_for('worker.update_task_status', task_id=task_id))

        db.session.commit()
        flash('任务状态更新成功!', 'success')
        return redirect(url_for('worker.tasks'))

    return render_template('update_task.html', task=task)
