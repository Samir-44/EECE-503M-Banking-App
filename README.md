# Online Banking System

A secure online banking system built with Flask for a Software Security course project. Includes strong authentication, role-based access control (RBAC), secure transactions, audit logging, and mitigation of common web vulnerabilities.

## Features

- **Authentication & Authorization**: User registration, login with password hashing (PBKDF2), login throttling, and CSRF protection.
- **Role-Based Access Control**: Supports four roles: `customer`, `support`, `auditor`, and `admin`.
- **Banking Operations**: 
  - Open checking/savings accounts
  - Internal transfers (between own accounts)
  - External transfers (to other users by account number)
  - Transaction history with filtering
- **Admin Features**:
  - User management (edit roles, activate/deactivate)
  - Account management (freeze/unfreeze accounts)
  - Full system oversight
- **Support System**: Customers can create support tickets; support staff can view and manage them.
- **Audit Logging**: All critical actions (login, transfer, account freeze, etc.) are logged; auditors and admins can view logs.
- **Security Best Practices**:
  - CSRF protection on all forms
  - Generic error messages on login failures
  - Login throttling after repeated failures
  - Server-side validation for all operations
  - No SQL injection (using SQLAlchemy ORM)
  - Role-based authorization checks

## Requirements

- Python 3.8+
- Virtual environment recommended
- See `requirements.txt` for dependencies

## Quick Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Samir-44/EECE-503M-Banking-App.git
   cd EECE-503M-Banking-App
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Create default users** (admin, support, auditor):
   ```bash
   python seed_admin.py
   ```

6. **Run the application**:
   ```bash
   python run.py
   ```

7. **Access the app**:
   Open your browser to `http://127.0.0.1:5000`

## Default Users

After running `seed_admin.py`, you'll have these accounts:

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@example.com` | `Admin123!` |
| Support | `support@example.com` | `Support123!` |
| Auditor | `auditor@example.com` | `Auditor123!` |

**Note**: Change these passwords immediately in production!

You can also register new customer accounts via the registration page.

## User Roles & Permissions

### Customer
- Open checking/savings accounts
- Transfer money internally (between own accounts)
- Transfer money externally (to other users)
- View transaction history
- Create support tickets
- Manage profile

### Support Agent
- View all support tickets
- Manage ticket status
- Access customer support dashboard

### Auditor
- View complete audit logs
- View all transactions (read-only)
- Generate audit reports

### Admin
- All customer permissions
- User management (create, edit, delete, change roles)
- Account management (freeze/unfreeze accounts)
- View all support tickets
- View all audit logs
- Full system access

## Testing the Application

### Basic Customer Flow
1. Register a new customer account
2. Login and open 2 accounts (checking & savings)
3. Perform internal transfer between your accounts
4. Register a second customer
5. Perform external transfer between customers
6. Create a support ticket

### Admin Flow
1. Login as admin
2. Navigate to "Manage Users" - edit user roles
3. Navigate to "Manage Accounts" - freeze/unfreeze accounts
4. View audit logs to see all system activities

### Security Testing
1. **Login Throttling**: Try 5 failed login attempts - account locks temporarily
2. **RBAC**: Login as customer and try accessing `/banking/admin/users` - should get 403 Forbidden
3. **Business Logic**: Try transferring more than account balance - should be blocked
4. **Frozen Account**: Admin freezes account, customer tries to transfer - should be blocked

## Project Structure

```
app/
├── __init__.py            # App factory
├── config.py              # Configuration
├── extensions.py          # Flask extensions
├── models.py              # Database models (User, Account, Transaction, etc.)
├── security.py            # RBAC decorators and audit helpers
├── auth/                  # Authentication blueprint
│   ├── routes.py          # Login, register, logout, profile
│   └── forms.py           # Authentication forms
├── banking/               # Banking operations blueprint
│   ├── routes.py          # Accounts, transfers, transactions, admin
│   └── forms.py           # Banking forms
├── support/               # Support tickets blueprint
│   ├── routes.py          # Ticket creation and management
│   └── forms.py           # Support forms
├── audit/                 # Audit logs blueprint
│   └── routes.py          # Audit log viewing
├── templates/             # Jinja2 templates
│   ├── base.html
│   ├── auth/
│   ├── banking/
│   ├── support/
│   └── audit/
└── static/                # CSS and static assets
    └── css/
migrations/                # Database migrations
run.py                     # Application entry point
seed_admin.py              # Create default users
requirements.txt           # Python dependencies
README.md                  # This file
```

## Security Features

### Authentication
- Password hashing using PBKDF2
- Login throttling (5 attempts per 10 minutes)
- Generic error messages to prevent user enumeration
- Session management with secure cookies

### Authorization
- Role-based access control (RBAC)
- `@roles_required` decorator on protected routes
- Server-side permission checks
- HTTP 403 responses for unauthorized access

### Input Validation
- WTForms validation on all forms
- Server-side business logic validation
- SQLAlchemy ORM (no SQL injection)
- CSRF tokens on all POST requests

### Audit Trail
- Comprehensive logging of all actions
- Append-only audit logs
- IP address tracking
- Timestamp for all events
- User attribution for actions

### Business Logic Security
- Account ownership verification
- Balance sufficiency checks
- Account status validation (active/frozen)
- Atomic database transactions
- Suspicious activity detection (≥$10,000 transfers)

## Environment Variables

For production deployment, set these environment variables:

```bash
SECRET_KEY=your-very-secure-random-key
DATABASE_URL=postgresql://user:password@localhost/dbname
FLASK_ENV=production
SESSION_COOKIE_SECURE=True
```

## Security Notes

⚠️ **Important for Production**:
- Change all default passwords immediately
- Set `SESSION_COOKIE_SECURE = True` (requires HTTPS)
- Use a strong `SECRET_KEY` from environment variable
- Use PostgreSQL or MySQL instead of SQLite
- Implement persistent login throttling (Redis/database)
- Enable HTTPS/TLS for all connections
- Regular security audits and updates
- Implement rate limiting on API endpoints
- Add input sanitization and output encoding
- Configure proper CORS policies

## Development Notes

- Debug mode is enabled by default in `run.py`
- Database file: `instance/bank.db` (SQLite)
- All data persists between restarts
- Login throttling uses in-memory storage (resets on restart)

## License

This project is for educational purposes as part of a Software Security course.

## Contributing

This is a course project. For issues or suggestions, please open an issue on GitHub.

## Acknowledgments

Built as part of EECE 503M - Software Security course project, demonstrating secure coding practices and common web security mitigations.
