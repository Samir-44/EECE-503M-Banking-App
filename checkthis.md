PROMPT FOR CLAUDE (BANKING APP PROJECT)

You are an AI coding assistant inside my IDE.

I’m doing a Software Security course project. The spec (from a PDF) defines an “Online Banking System” built in Flask with strong security: authentication, RBAC, secure transactions, audit logs, and mitigation of common web vulnerabilities.

Important constraints:

Focus on correct security and clean/simple architecture, not on fancy UI.

No weird features. Just the bare minimum required by the project description.

Frontend: simple HTML templates with some Bootstrap from CDN. Functional and not ugly, but very basic.

Backend: Python + Flask + SQLAlchemy + Flask-Login + Flask-WTF (for CSRF).

“Multiservice”: structure the backend so we clearly separate:

an auth + RBAC + user management module/service,

a core banking module/service (accounts, transfers, transactions),

plus the database as its own service.
For now this can all live in one codebase with Blueprints and a separate DB container/service (e.g. SQLite locally, PostgreSQL later). But keep the code modular so I can easily split into separate Flask services/containers if needed.

I want you to actually implement the code for this app, step by step.

1. Project structure

Create this folder structure:

app/

__init__.py

config.py

extensions.py # db, login_manager, csrf, migrate, etc.

models.py # SQLAlchemy models

security.py # RBAC decorators, helpers

auth/

__init__.py

routes.py

forms.py

banking/

__init__.py

routes.py

forms.py

support/

__init__.py

routes.py

forms.py

audit/

__init__.py

routes.py

templates/

base.html

auth/ (login, register, profile)

banking/ (dashboard, open_account, transfer_internal, transfer_external, transactions_list)

support/ (tickets_list, ticket_detail)

admin/ (users_list, user_edit, accounts_list)

audit/ (logs_list)

static/

css/ (simple main.css)

migrations/ # for Flask-Migrate

run.py

requirements.txt

README.md

2. Dependencies

In requirements.txt include:

flask

flask_sqlalchemy

flask_migrate

flask_login

flask_wtf

email-validator # for WTForms email field

python-dotenv # for environment variables, e.g. SECRET_KEY

(optional) argon2-cffi or passlib[argon2] if you want Argon2 hashing; otherwise Werkzeug’s PBKDF2 is fine.

3. Configuration & app factory

Create app/__init__.py with an application factory pattern:

create_app() that:

loads config from config.py.

initializes extensions (db, migrate, login_manager, csrf).

registers blueprints:

auth_bp at /auth

banking_bp at /banking

support_bp at /support

audit_bp at /audit

defines a simple index route that redirects:

logged-out users → /auth/login

logged-in users → /banking/dashboard

config.py:

SECRET_KEY from environment or fallback (but comment that real deployment must set env var).

SQLALCHEMY_DATABASE_URI – use SQLite by default: sqlite:///bank.db.

SQLALCHEMY_TRACK_MODIFICATIONS = False.

Cookie settings:

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SECURE = False for dev, but add a comment that in real deployment it must be True under HTTPS.

Also configure some simple settings like WTF_CSRF_TIME_LIMIT.

extensions.py:

instantiate db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

csrf = CSRFProtect()

Initialize them in create_app.

4. Database models (in models.py)

Implement minimal models matching the project:

User

id (int, PK)

full_name (string)

email (string, unique)

phone (string)

password_hash (string)

role (string enum: "customer", "support", "auditor", "admin")

is_active (bool, default True)

created_at (DateTime)

Implement:

set_password(self, raw_password) using werkzeug.security.generate_password_hash with pbkdf2:sha256.

check_password(self, raw_password) with check_password_hash.

Make User compatible with Flask-Login (mixin or implementing is_authenticated, etc.).

Account

id (int, PK)

account_number (string, unique; auto-generated)

owner_id (FK → User.id)

type (string: "checking" or "savings")

balance (Numeric/Decimal)

status (string: "active", "frozen", "closed")

created_at (DateTime)

Transaction

id (int, PK)

sender_account_id (nullable FK → Account.id)

receiver_account_id (nullable FK → Account.id)

amount (Numeric)

type (string: "debit" or "credit")

description (string)

timestamp (DateTime)

initiated_by_user_id (FK → User.id)

SupportTicket

id (int, PK)

customer_id (FK → User.id)

subject (string)

description (text)

status (string: "open", "in_progress", "resolved")

created_at, updated_at (DateTime)

last_updated_by_id (FK → User.id)

AuditLog

id (int, PK)

user_id (nullable FK → User.id)

action (string)
e.g. "LOGIN_SUCCESS", "LOGIN_FAILURE", "ACCOUNT_FROZEN", "ACCOUNT_UNFROZEN", "ROLE_CHANGED", "TRANSFER_CREATED", "SUSPICIOUS_TRANSFER", etc.

details (text) – can store a small JSON string or human-readable text.

ip_address (string)

timestamp (DateTime)

This table is append-only; do not implement any route that allows users to edit or delete audit logs.

5. RBAC helpers (in security.py)

Implement:

@roles_required(*allowed_roles) decorator that:

checks current_user.is_authenticated.

checks current_user.role in allowed_roles.

returns 403 if not allowed.

Also a helper to log security/audit events:

from .models import AuditLog
from flask import request
from .extensions import db
from flask_login import current_user

def log_event(action, details=""):
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        details=details,
        ip_address=request.remote_addr,
    )
    db.session.add(log)
    db.session.commit()


Use this helper across the app.

6. Auth blueprint (auth/routes.py and auth/forms.py)

Forms:

RegisterForm:

full_name, email, phone, password, confirm_password.

Basic validation.

LoginForm:

email, password.

Routes:

GET /auth/register + POST /auth/register:

Only for new customers (not logged in).

When creating, default role = "customer".

Hash password.

Log event "REGISTER_SUCCESS".

GET /auth/login + POST /auth/login:

On POST:

Look up user by email.

If user not found or password wrong → add generic error like: “Invalid email or password” (no distinction).

Implement basic login throttling: keep a simple in-memory or DB table of failed attempts per email/IP and block or delay after e.g. 5 attempts within 10 minutes.

On success:

login_user(user).

Log "LOGIN_SUCCESS".

On failure:

Log "LOGIN_FAILURE".

Redirect logged-in users to /banking/dashboard.

GET /auth/logout:

logout_user().

Log "LOGOUT".

GET /auth/profile:

@login_required.

Allow user to edit their own full_name, phone.

Admin can have a separate page for editing any user (see admin section later).

LoginManager in extensions.py:

Set login_view = "auth.login".

7. Banking blueprint (banking/routes.py, banking/forms.py)

Forms:

OpenAccountForm:

type (select: checking/savings).

opening_balance (Decimal).

InternalTransferForm:

source_account (select from current_user’s accounts).

target_account (also from current_user’s accounts).

amount, description.

ExternalTransferForm:

source_account (one of user’s accounts).

target_account_number (string).

amount, description.

Routes:

GET /banking/dashboard

@login_required, @roles_required("customer", "admin", "support", "auditor").

If customer: show only their accounts and last 5 transactions per account.

If admin/support/auditor: maybe a simple message + link to their specific areas.

GET/POST /banking/open-account

@login_required

If role is "customer": create account with owner = current user.

If role is "admin" and there is a query param or form field owner_user_id, allow admin to create for any user.

Generate account_number as a random 10–12 digit string (ensure uniqueness).

Status = "active".

Log event "ACCOUNT_CREATED" with details account_number and owner_id.

GET/POST /banking/transfer/internal

@login_required, role "customer" only (except admin).

Validate:

Both accounts belong to current_user (unless admin is using).

Both accounts have status "active".

Sufficient balance.

If valid:

Deduct from source, add to target, create two Transaction records (debit/credit) inside a single DB transaction.

Log "TRANSFER_CREATED", and if amount > threshold (e.g. 10,000) also log "SUSPICIOUS_TRANSFER".

If not valid: show error; do not rely on front-end order or hidden fields (to avoid business logic bugs).

GET/POST /banking/transfer/external

Similar to internal, but:

Find target account by account_number.

Check source account belongs to current_user and is active.

Check target account is active and exists.

Same logging rules.

GET /banking/transactions

@login_required.

If customer: show only transactions for accounts they own.

Include simple filter parameters in query string:

date_from, date_to, type, min_amount, max_amount.

Support agent/auditor/admin will have separate views to see all transactions.

8. Admin & support & auditor routes (inside existing blueprints)

Admin pages (can be under /banking/admin or a small admin section inside banking.routes):

GET /banking/admin/users

@roles_required("admin").

List all users with role badges and quick links to edit.

GET/POST /banking/admin/users/<int:user_id>/edit

@roles_required("admin").

Edit name, email, phone, role, active state.

Do not allow changing your own role from admin to something else (to avoid locking out the system).

Log "ROLE_CHANGED" or "USER_UPDATED".

GET /banking/admin/accounts

@roles_required("admin").

List all accounts, their status, owner, balance, etc.

POST /banking/admin/accounts/<int:account_id>/freeze

@roles_required("admin").

Set status to "frozen".

Log "ACCOUNT_FROZEN".

POST /banking/admin/accounts/<int:account_id>/unfreeze

Same but status "active".

Log "ACCOUNT_UNFROZEN".

Support routes (support/routes.py)

GET /support/tickets

@roles_required("support", "admin").

List all tickets by status.

GET/POST /support/tickets/<int:ticket_id>

@roles_required("support", "admin").

View ticket details, change status, add note.

Log "TICKET_UPDATED".

Customer routes (can be in banking or support):

GET/POST /support/create

@roles_required("customer").

Create ticket with subject + description.

Status = "open".

Log "TICKET_CREATED".

Auditor routes (audit/routes.py)

GET /audit/logs

@roles_required("auditor", "admin").

Paginated list of AuditLog, with simple filters (by action, date, user_id).

GET /audit/transactions

@roles_required("auditor", "admin").

View all transactions with filters; read-only.

9. Templates

Keep templates simple:

base.html

Basic Bootstrap navbar with:

Brand (Online Bank).

When logged in: show user name + role + Logout link.

Top-level links depending on role:

Customer: Dashboard, Open Account, Transfers, My Transactions, Support Ticket.

Support: Support Tickets.

Auditor: Audit Logs, Transactions.

Admin: Users, Accounts, Audit Logs.

Each page:

Uses a simple container and maybe card from Bootstrap.

Tables for listing users, accounts, tickets, logs.

WTForms rendering with CSRF token.

No need for SPA or heavy JavaScript.

10. Security details to respect in implementation

When you generate the code, please explicitly implement the following safeguards (they are important for my grading):

CSRF protection

Initialize CSRFProtect(app) in the app factory.

All HTML forms include {{ form.hidden_tag() }} for the CSRF token.

Authentication hardening

Passwords hashed via generate_password_hash.

Login errors are generic.

Log every success and failure to AuditLog.

Implement a simple login-throttling mechanism (even if minimal).

RBAC and least privilege

Use @roles_required decorator on every route that should not be accessible to all roles.

Default when role not allowed: return HTTP 403.

Input validation & injection

Use WTForms for all forms and SQLAlchemy ORM only.

No SQL strings built via string concatenation / f-strings.

Business logic

For all transfers:

Verify account ownership (customers can only operate on their own accounts).

Verify account status is "active".

Verify sufficient balance.

Do not assume step order; all checks are server-side.

Do not base admin vs user logic on absence/presence of a parameter; always use the role field.

SSRF

Do NOT implement any feature that fetches or calls a URL provided by the user.

Audit log is append-only

No route for editing or deleting audit logs.

Only auditor and admin can read them.

11. Seed data

Add a simple CLI or a small script to:

Create tables (flask db upgrade).

Insert a default admin user:

email: admin@example.com

password: Admin123! (just for dev; mention that it must be changed on first login).

You can put this in run.py or a manage.py with a custom command.

12. Run instructions (for README.md)

Document basic steps:

Create virtualenv.

Install requirements.

Set FLASK_APP=run.py and FLASK_ENV=development.

Run flask db init, flask db migrate, flask db upgrade.

Run python run.py to start the app on http://127.0.0.1:5000.

End of prompt for Claude. Please now generate all the necessary Python files and templates according to this specification, focusing on correctness and security rather than UI fanciness.