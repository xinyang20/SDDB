# SDDB - Traditional Chinese Medicine Decoction Management System

[简体中文](./README.md) | English

SDDB (Smart Decoction Database) is a modern management platform designed specifically for Traditional Chinese Medicine (TCM) decoction centers. It aims to digitize and optimize the entire process of TCM decoction management, supporting multi-role collaboration from prescription entry to medicine preparation completion.

## Features

### Multi-Role Management

- **Patient Portal**: Account registration, prescription status viewing, decoction progress tracking
- **Doctor Portal**: Prescription creation, patient prescription management, prescription details viewing
- **Worker Portal**: Task reception, task status updates, workflow management
- **Admin Portal**: User management, task assignment, system monitoring

### Prescription Management

- Prescription information entry and editing
- Real-time prescription status tracking
- Medication guidance and dosage management
- Expected pickup time setting

### Task Workflow Management

- Intelligent task assignment system
- Multi-stage workflow (Reception → Formulation → Decoction)
- Real-time status updates and progress tracking
- Work time recording and statistics

### Security & Permissions

- Role-based access control
- User authentication and session management
- Data security and privacy protection

## Technology Stack

- **Backend Framework**: Flask 3.1.2+
- **Database**: SQLite (supports lightweight deployment)
- **ORM**: Flask-SQLAlchemy 3.1.1+
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Package Manager**: UV (modern Python package manager)
- **Python Version**: 3.12+

## Quick Start

### Requirements

- Python 3.12+
- UV package manager (recommended) or pip

### Installation Steps

1. **Clone the project**

   ```bash
   git clone https://github.com/xinyang20/SDDB.git
   cd SDDB
   ```

2. **Install dependencies**

   Using UV (recommended):

   ```bash
   # Create virtual environment and install dependencies
   uv venv .venv
   uv sync
   ```

   Or using pip:

   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate

   # Install dependencies
   pip install flask flask-sqlalchemy
   ```

3. **Initialize database**

   ```bash
   # Using UV
   uv run python init_db.py

   # Or using Python
   python init_db.py
   ```

4. **Start the application**

   ```bash
   # Using UV
   uv run python app.py

   # Or using Python
   python app.py
   ```

5. **Access the application**

   Open your browser and visit: http://localhost:5050

### Default Test Accounts

The system automatically creates the following test accounts after initialization:

| Role    | Username | Password | Description                  |
| ------- | -------- | -------- | ---------------------------- |
| Admin   | admin    | admin123 | System administrator account |
| Doctor  | doctor1  | 123456   | Doctor test account          |
| Patient | patient1 | 123456   | Patient test account         |
| Worker  | worker1  | 123456   | Worker test account          |

## Usage Guide

### Patient Workflow

1. Register a patient account or login with test account
2. View personal prescription list
3. Track prescription status and decoction progress
4. View prescription details and medication guidance

### Doctor Workflow

1. Login with doctor account
2. Create new prescriptions for patients
3. Manage and view prescription list
4. View detailed prescription information

### Worker Workflow

1. Login with worker account
2. View assigned task list
3. Update task status and progress
4. Record work time

### Administrator Workflow

1. Login with administrator account
2. Manage system users
3. Assign work tasks
4. Monitor system operation status

## Configuration

### Database Configuration

The system uses SQLite database by default, configuration file located at `config.py`:

```python
# SQLite database configuration
SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'sddb.db'}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Security configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
```

### Environment Variables

You can customize configuration through environment variables:

- `SECRET_KEY`: Flask application secret key (must be set in production)

### Production Deployment

1. **Set environment variables**

   ```bash
   export SECRET_KEY="your-very-secure-secret-key"
   ```

2. **Use production-grade WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5050 app:app
   ```

## Database Structure

The system includes the following main data tables:

- **users**: User account information
- **patients**: Patient detailed information
- **doctors**: Doctor detailed information
- **workers**: Worker detailed information
- **admins**: Administrator detailed information
- **prescriptions**: Prescription information
- **tasks**: Task management information

## Development Guide

### Project Structure Description

```
SDDB/
├── app.py              # Flask application main file
├── config.py           # Configuration file
├── exts.py            # Flask extensions initialization
├── models.py          # Database model definitions
├── init_db.py         # Database initialization script
├── pyproject.toml     # Project dependency configuration
├── static/            # Static resources
│   ├── css/          # Style files
│   └── js/           # JavaScript files
└── templates/         # HTML templates
    ├── components/   # Reusable components
    └── *.html       # Page templates
```

### Adding New Features

1. **Database Models**: Define new data models in `models.py`
2. **Route Handling**: Add new routes and business logic in `app.py`
3. **Frontend Pages**: Create corresponding HTML templates in `templates/`
4. **Styles and Scripts**: Add CSS and JavaScript files in `static/`

### Code Standards

- Follow PEP 8 Python code standards
- Use meaningful variable and function names
- Add appropriate comments and docstrings
- Keep code clean and readable

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the Apache2.0 License - see the [LICENSE](LICENSE) file for details.

---

**Note**: This system is for learning and demonstration purposes only. Please ensure thorough security testing and configuration before using in production environments.
