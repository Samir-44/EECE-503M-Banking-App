# Online Banking System

A secure online banking system built with Flask for a Software Security course project. Includes strong authentication, role-based access control (RBAC), secure transactions, audit logging, and mitigation of common web vulnerabilities.

## Features

- **Authentication & Authorization**: User registration, login with password hashing (PBKDF2), login throttling, and CSRF protection.
- **Role-Based Access Control**: Supports four roles: `customer`, `support`, `auditor`, and `admin`.
- **Banking Operations**: 
  - Open checking/savings accounts
  - Internal and external transfers with balance/status validation
  - Transaction history
- **Support System**: Customers can create support tickets; support staff can view and manage them.
- **Audit Logging**: All critical actions (login, transfer, account freeze, etc.) are logged; auditors and admins can view logs.
- **Security Best Practices**:
  - CSRF protection on all forms
  - Generic error messages on login failures
  - Login throttling after repeated failures
  - Server-side validation for all operations
  - No SQL injection (using SQLAlchemy ORM)

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## Setup

1. **Create a virtual environment**:
   ```powershell
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional):
   ```powershell
   $env:SECRET_KEY="your-secret-key"
   $env:FLASK_APP="run.py"
   $env:FLASK_ENV="development"
   ```

5. **Initialize the database**:
   ```powershell
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Create a default admin user** (run Python in the project directory):
   ```powershell
   python
   ```
   Then in the Python shell:
   ```python
   from app import create_app
   from app.extensions import db
   from app.models import User
   
   app = create_app()
   with app.app_context():
       admin = User(full_name="Admin User", email="admin@example.com", phone="", role="admin", is_active=True)
       admin.set_password("Admin123!")
       db.session.add(admin)
       db.session.commit()
       print("Admin user created.")
   ```
   Type `exit()` to leave the Python shell.

7. **Run the application**:
   ```powershell
   python run.py
   ```

   The app will be available at `http://127.0.0.1:5000`.

## Usage

- **Login** with the admin credentials: `admin@example.com` / `Admin123!` (change this on first login).
- **Register** as a new customer to test customer features.
- **Roles**:
  - `customer`: Can open accounts, transfer funds, view transactions, create support tickets.
  - `support`: Can view and manage support tickets.
  - `auditor`: Can view audit logs and transactions.
  - `admin`: Full access including user management, account freezing, and audit logs.

## Project Structure

```
app/
├── __init__.py            # App factory
├── config.py              # Configuration
├── extensions.py          # Flask extensions
├── models.py              # Database models
├── security.py            # RBAC decorators and audit helpers
├── auth/                  # Authentication blueprint
├── banking/               # Banking operations blueprint
├── support/               # Support tickets blueprint
├── audit/                 # Audit logs blueprint
├── templates/             # Jinja2 templates
└── static/                # CSS and static assets
run.py                     # Application entry point
requirements.txt           # Python dependencies
README.md                  # This file
```

## Security Notes

- **SESSION_COOKIE_SECURE** is set to `False` for local development. **Enable it in production** with HTTPS.
- **SECRET_KEY** should be set via environment variable in production.
- **Default admin password** (`Admin123!`) must be changed immediately.
- All forms include CSRF tokens.
- Login throttling is implemented in-memory (for dev). In production, use a persistent store (Redis, DB).

## License

This project is for educational purposes as part of a Software Security course.
