from flask import Flask, session
from flask_restful import Api
import config
from exts import db

# 初始化应用
app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)

# 添加context processor以在所有模板中提供未读告警数量
@app.context_processor
def inject_unread_alerts():
    """向所有模板注入未读告警数量"""
    unread_count = 0
    if 'user_id' in session and session.get('role') == 'admin':
        from models import AlertModel
        unread_count = AlertModel.query.filter_by(is_read=False).count()
    return dict(unread_alerts_count=unread_count)

# 初始化Flask-RESTful API
api = Api(app)

# 注册蓝图
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.doctor import doctor_bp
from blueprints.patient import patient_bp
from blueprints.worker import worker_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(worker_bp)

# 注册FHIR API资源
from api.fhir.resources import (
    MedicationRequestResource,
    PatientResource,
    PractitionerResource,
    TaskResource,
    CapabilityStatementResource
)

api.add_resource(CapabilityStatementResource, '/fhir/metadata')
api.add_resource(MedicationRequestResource,
    '/fhir/MedicationRequest',
    '/fhir/MedicationRequest/<int:prescription_id>')
api.add_resource(PatientResource,
    '/fhir/Patient',
    '/fhir/Patient/<int:patient_id>')
api.add_resource(PractitionerResource,
    '/fhir/Practitioner',
    '/fhir/Practitioner/<int:doctor_id>')
api.add_resource(TaskResource,
    '/fhir/Task',
    '/fhir/Task/<int:task_id>')

# 初始化SocketIO实时推送
from realtime.socketio_server import init_socketio
socketio = init_socketio(app)

# 初始化数据库
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建所有表
    # 使用socketio.run代替app.run以支持WebSocket
    socketio.run(app, debug=True, host='0.0.0.0', port=5050, allow_unsafe_werkzeug=True)
