"""告警通知器"""
from datetime import datetime
from models import AlertModel
from exts import db

def send_alert(type, level, message, task_id=None, worker_id=None, data=None):
    """
    发送告警

    Args:
        type: 告警类型 (timeout_receive, timeout_formulate, timeout_decoction, abnormal_fast, backlog, low_efficiency)
        level: 告警级别 (high, medium, low)
        message: 告警消息
        task_id: 关联任务ID (可选)
        worker_id: 关联工人ID (可选)
        data: 额外数据 (可选)
    """
    # 1. 保存到数据库
    alert = AlertModel(
        type=type,
        level=level,
        message=message,
        task_id=task_id,
        worker_id=worker_id
    )
    db.session.add(alert)
    db.session.commit()

    # 2. 实时推送到管理员（通过WebSocket）
    try:
        from realtime.socketio_server import broadcast_alert
        alert_data = {
            'alert_id': alert.alert_id,
            'type': type,
            'level': level,
            'message': message,
            'task_id': task_id,
            'worker_id': worker_id,
            'timestamp': alert.created_at.isoformat()
        }
        broadcast_alert(alert_data)
    except Exception as e:
        print(f"WebSocket推送失败: {str(e)}")

    # 3. 其他通知渠道（可扩展）
    # - 发送邮件
    # - 发送短信
    # - 企业微信/钉钉推送
    # send_email_notification(alert)
    # send_sms_notification(alert)

    return alert

def mark_alert_read(alert_id):
    """标记告警为已读"""
    alert = AlertModel.query.get(alert_id)
    if alert:
        alert.is_read = True
        db.session.commit()
    return alert

def resolve_alert(alert_id):
    """解决告警"""
    alert = AlertModel.query.get(alert_id)
    if alert:
        alert.is_read = True
        alert.resolved_at = datetime.utcnow()
        db.session.commit()
    return alert

def get_unread_alerts():
    """获取未读告警列表"""
    return AlertModel.query.filter_by(is_read=False).order_by(AlertModel.created_at.desc()).all()

def get_alerts_by_type(alert_type, limit=10):
    """按类型获取告警"""
    return AlertModel.query.filter_by(type=alert_type).order_by(AlertModel.created_at.desc()).limit(limit).all()

def get_recent_alerts(hours=24, limit=50):
    """获取最近的告警"""
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    return AlertModel.query.filter(
        AlertModel.created_at >= time_threshold
    ).order_by(AlertModel.created_at.desc()).limit(limit).all()

# 导入timedelta
from datetime import timedelta
