"""Celery配置文件"""
from celery import Celery
from celery.schedules import crontab

# 创建Celery应用
celery_app = Celery(
    'sddb_alerts',
    broker='redis://localhost:6379/0',  # 消息代理
    backend='redis://localhost:6379/1'  # 结果后端
)

# Celery配置
celery_app.conf.update(
    # 时区设置
    timezone='Asia/Shanghai',
    enable_utc=True,

    # 任务序列化
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # 结果过期时间（秒）
    result_expires=3600,

    # 任务路由
    task_routes={
        'alerts.rules.*': {'queue': 'alerts'},
    },

    # 定时任务配置
    beat_schedule={
        'check-alerts-every-minute': {
            'task': 'alerts.rules.run_alert_checks',
            'schedule': 60.0,  # 每60秒执行一次
        },
    },
)

# 如果Redis不可用，使用内存后端（仅用于开发测试）
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
    r.ping()
except:
    print("⚠️  警告: Redis未启动，告警系统将使用内存后端（不推荐生产使用）")
    celery_app.conf.update(
        broker_url='memory://',
        result_backend='cache+memory://'
    )
