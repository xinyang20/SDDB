import os
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).parent

# SQLite数据库配置
SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'sddb.db'}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 安全配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
