# SDDB - 中药代煎管理系统

简体中文 | [English](./README_en.md)

SDDB (Smart Decoction Database) 是一个专为中药代煎中心设计的现代化管理平台，旨在数字化和优化中药代煎的全流程管理。系统支持多角色协作，涵盖从处方录入到药品配制完成的完整业务链条。

## 功能特性

### 多角色管理

- **患者端**: 注册账户、查看处方状态、跟踪代煎进度
- **医生端**: 创建处方、管理患者处方、查看处方详情
- **工人端**: 接收任务、更新任务状态、管理工作流程
- **管理员端**: 用户管理、任务分配、系统监控

### 处方管理

- 处方信息录入和编辑
- 处方状态实时跟踪
- 用药指导和剂量管理
- 预计取药时间设置

### 任务流程管理

- 智能任务分配系统
- 多阶段工作流程（接收 → 配方 → 煎制）
- 实时状态更新和进度跟踪
- 工作时间记录和统计

### 安全与权限

- 基于角色的访问控制
- 用户身份验证和会话管理
- 数据安全和隐私保护

## 技术栈

- **后端框架**: Flask 3.1.2+
- **数据库**: SQLite (支持轻量级部署)
- **ORM**: Flask-SQLAlchemy 3.1.1+
- **前端**: HTML5 + CSS3 + JavaScript
- **包管理**: UV (现代 Python 包管理器)
- **Python 版本**: 3.12+

## 快速开始

### 环境要求

- Python 3.12+
- UV 包管理器 (推荐) 或 pip

### 安装步骤

1. **克隆项目**

   ```bash
   git clone https://github.com/xinyang20/SDDB.git
   cd sddb/src
   ```

2. **安装依赖**

   使用 UV (推荐):

   ```bash
   # 创建虚拟环境并安装依赖
   uv venv .venv
   uv sync
   ```

   或使用 pip:

   ```bash
   # 创建虚拟环境
   python -m venv .venv

   # 激活虚拟环境
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate

   # 安装依赖
   pip install flask flask-sqlalchemy
   ```

3. **初始化数据库**

   ```bash
   # 使用 UV
   uv run python init_db.py

   # 或使用 Python
   python init_db.py
   ```

4. **启动应用**

   ```bash
   # 使用 UV
   uv run python app.py

   # 或使用 Python
   python app.py
   ```

5. **访问应用**

   打开浏览器访问: http://localhost:5050

### 默认测试账户

系统初始化后会自动创建以下测试账户：

| 角色   | 用户名   | 密码     | 说明           |
| ------ | -------- | -------- | -------------- |
| 管理员 | admin    | admin123 | 系统管理员账户 |
| 医生   | doctor1  | 123456   | 医生测试账户   |
| 患者   | patient1 | 123456   | 患者测试账户   |
| 工人   | worker1  | 123456   | 工人测试账户   |

## 使用说明

### 患者使用流程

1. 注册患者账户或使用测试账户登录
2. 查看个人处方列表
3. 跟踪处方状态和代煎进度
4. 查看处方详情和用药指导

### 医生使用流程

1. 使用医生账户登录
2. 为患者创建新处方
3. 管理和查看处方列表
4. 查看处方详细信息

### 工人使用流程

1. 使用工人账户登录
2. 查看分配的任务列表
3. 更新任务状态和进度
4. 记录工作时间

### 管理员使用流程

1. 使用管理员账户登录
2. 管理系统用户
3. 分配工作任务
4. 监控系统运行状态

## 配置说明

### 数据库配置

系统默认使用 SQLite 数据库，配置文件位于 `config.py`：

```python
# SQLite数据库配置
SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'sddb.db'}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 安全配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
```

### 环境变量

可以通过环境变量自定义配置：

- `SECRET_KEY`: Flask 应用密钥（生产环境必须设置）

### 生产环境部署

1. **设置环境变量**

   ```bash
   export SECRET_KEY="your-very-secure-secret-key"
   ```

2. **使用生产级 WSGI 服务器**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5050 app:app
   ```

## 数据库结构

系统包含以下主要数据表：

- **users**: 用户账户信息
- **patients**: 患者详细信息
- **doctors**: 医生详细信息
- **workers**: 工人详细信息
- **admins**: 管理员详细信息
- **prescriptions**: 处方信息
- **tasks**: 任务管理信息

## 开发指南

### 项目结构说明

```
SDDB
├─ .python-version      # Python 版本文件
├─ LICENSE              # 许可证文件
├─ pyproject.toml       # 项目依赖配置
├─ README.md            # 项目说明文件
├─ README_en.md         # 项目说明文件(英文)
├─ src                  # 源代码目录
│  ├─ app.py            # Flask 应用主文件
│  ├─ config.py         # 配置文件
│  ├─ exts.py           # Flask 扩展初始化
│  ├─ init_db.py        # 数据库初始化脚本
│  ├─ models.py         # 数据库模型定义
│  ├─ static            # 静态资源
│  │  ├─ css/           # 样式文件
│  │  └─ js/            # JavaScript 文件
│  └── templates/       # HTML 模板
│      ├── components/  # 可复用组件
│      └── *.html       # 页面模板
└─ uv.lock              # UV 锁定文件
```

### 添加新功能

1. **数据库模型**: 在 `models.py` 中定义新的数据模型
2. **路由处理**: 在 `app.py` 中添加新的路由和业务逻辑
3. **前端页面**: 在 `templates/` 中创建对应的 HTML 模板
4. **样式和脚本**: 在 `static/` 中添加 CSS 和 JavaScript 文件

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串
- 保持代码简洁和可读性

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 Apache2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**注意**: 本系统仅供学习和演示使用，在生产环境中使用前请确保进行充分的安全性测试和配置。
