"""Flask-SocketIO实时推送服务器"""
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import session
from threading import Thread
import time
from datetime import datetime
from realtime.dashboard_metrics import DashboardMetrics

# SocketIO实例（将在app.py中初始化）
socketio = None

def init_socketio(app):
    """初始化SocketIO"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    # 注册事件处理器
    register_handlers()

    # 启动后台推送线程
    start_background_push(app)

    return socketio

def register_handlers():
    """注册WebSocket事件处理器"""

    @socketio.on('connect')
    def handle_connect():
        """客户端连接"""
        if 'role' in session and session.get('role') == 'admin':
            join_room('admin')
            emit('connected', {'status': 'success', 'message': '实时数据连接成功'})
            # 立即推送当前数据
            try:
                dashboard_data = DashboardMetrics.get_dashboard_data()
                emit('dashboard_update', dashboard_data)
            except Exception as e:
                emit('error', {'message': f'获取数据失败: {str(e)}'})
        else:
            emit('connected', {'status': 'error', 'message': '无权限访问'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接"""
        if 'role' in session and session.get('role') == 'admin':
            leave_room('admin')

    @socketio.on('request_update')
    def handle_update_request():
        """手动请求数据更新"""
        if 'role' in session and session.get('role') == 'admin':
            try:
                dashboard_data = DashboardMetrics.get_dashboard_data()
                emit('dashboard_update', dashboard_data)
            except Exception as e:
                emit('error', {'message': f'获取数据失败: {str(e)}'})

    @socketio.on('ping')
    def handle_ping():
        """心跳检测"""
        emit('pong', {'timestamp': datetime.now().isoformat()})

def start_background_push(app):
    """启动后台数据推送线程"""
    def background_push():
        """后台推送任务"""
        while True:
            time.sleep(60)  # 每60秒推送一次
            try:
                with app.app_context():
                    dashboard_data = DashboardMetrics.get_dashboard_data()
                    socketio.emit('dashboard_update', dashboard_data, room='admin')
            except Exception as e:
                print(f"后台推送错误: {str(e)}")

    # 创建守护线程
    thread = Thread(target=background_push, daemon=True)
    thread.start()

def broadcast_alert(alert_data):
    """广播告警消息到管理员"""
    if socketio:
        socketio.emit('new_alert', alert_data, room='admin')

def broadcast_task_update(task_id, status):
    """广播任务状态更新"""
    if socketio:
        socketio.emit('task_update', {
            'task_id': task_id,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }, room='admin')
