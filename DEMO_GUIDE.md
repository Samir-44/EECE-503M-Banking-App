# Demo Guide for Professor

## Quick Setup Verification

The app is running at: **http://127.0.0.1:5000**

**Default Admin Credentials**:
- Email: `admin@example.com`
- Password: `Admin123!`

---

## Demo Flow (15-20 minutes)

### Part 1: Authentication & Security (3-5 min)

#### 1.1 Registration & Password Security
1. Go to **Register** page
2. Create a new customer account:
   - Full Name: `John Customer`
   - Email: `john@example.com`
   - Phone: `555-1234`
   - Password: `SecurePass123!`
3. **Show**: Password is hashed in database (not visible)

#### 1.2 Login Throttling
1. Try logging in with wrong password 3-4 times
2. **Show**: System logs each failed attempt
3. After 5 failed attempts, account gets temporarily locked
4. **Demonstrate**: "Too many failed attempts" message appears

#### 1.3 CSRF Protection
1. Log in as customer
2. **Show**: Inspect any form and point out CSRF token in HTML
3. **Explain**: All forms include `{{ form.hidden_tag() }}` for CSRF protection

---

### Part 2: Customer Banking Operations (5-7 min)

Log in as: `john@example.com` / `SecurePass123!`

#### 2.1 Open Accounts
1. Click **Open Account**
2. Create a **Checking** account with opening balance: `$5000`
3. Create a **Savings** account with opening balance: `$10000`
4. **Show**: Dashboard displays both accounts with unique account numbers
5. **Security Note**: Account numbers are randomly generated and unique

#### 2.2 Internal Transfer with Validation
1. Click **Internal Transfer**
2. Try transferring `$6000` from Checking (only has $5000)
3. **Show**: "Insufficient funds" error (server-side validation)
4. Transfer `$2000` from Checking to Savings successfully
5. **Show**: 
   - Balances updated correctly
   - Two transaction records created (debit + credit)
   - Audit log entries for the transfer

#### 2.3 Transaction History
1. Click **View Transactions**
2. **Show**: All transactions with timestamps
3. **Security Note**: Customers only see their own transactions

#### 2.4 Support Ticket
1. Navigate to **Support** → **Create Ticket**
2. Create a ticket:
   - Subject: `Question about transfer limits`
   - Description: `What is the daily transfer limit?`
3. **Show**: Ticket created with "open" status

---

### Part 3: Role-Based Access Control (RBAC) (4-6 min)

#### 3.1 Admin Role
1. **Logout** and login as admin: `admin@example.com` / `Admin123!`
2. Navigate to different sections to show admin access

#### 3.2 User Management (Admin Only)
1. Go to **Banking** → **Admin** → **Users** (or via URL: `/banking/admin/users`)
2. **Show**: List of all users with their roles
3. Click **Edit** on John Customer
4. Try changing role from `customer` to `support`
5. **Security Note**: Cannot change own admin role (prevents lockout)

#### 3.3 Account Freezing (Admin Only)
1. Go to **Banking** → **Admin** → **Accounts** (or via URL: `/banking/admin/accounts`)
2. **Show**: All accounts in the system
3. **Freeze** John's checking account
4. **Show**: Audit log entry "ACCOUNT_FROZEN"
5. **Demonstrate**: If John tries to transfer from frozen account, it will fail

#### 3.4 Support Role
1. Stay logged in as admin (or change John to support role)
2. Navigate to **Support** → **Tickets** (URL: `/support/tickets`)
3. **Show**: All support tickets from all customers
4. **Security Note**: Regular customers cannot access this view

#### 3.5 Auditor Role
1. Navigate to **Audit** → **Logs** (URL: `/audit/logs`)
2. **Show**: Complete audit trail:
   - All login attempts (success/failure)
   - Account creation
   - Transfers
   - Role changes
   - Account freeze/unfreeze
3. **Filter** by action type if needed
4. **Security Note**: Logs are append-only, cannot be deleted

---

### Part 4: Security Demonstrations (3-5 min)

#### 4.1 Authorization Checks
1. Log out from admin
2. Log in as `john@example.com`
3. Try to access admin URL directly: `http://127.0.0.1:5000/banking/admin/users`
4. **Show**: 403 Forbidden error (RBAC protection)

#### 4.2 Business Logic Validation
1. As John (customer), try to transfer to another user's account
2. **Show**: Cannot select accounts you don't own
3. **Explain**: Server-side validation prevents:
   - Transferring from accounts you don't own
   - Insufficient balance
   - Transfers involving frozen accounts
   - Invalid account numbers

#### 4.3 Suspicious Activity Detection
1. Make a large transfer (≥ $10,000)
2. Go to audit logs
3. **Show**: System automatically flagged it as "SUSPICIOUS_TRANSFER"

#### 4.4 SQL Injection Prevention
1. **Explain**: All database queries use SQLAlchemy ORM
2. **Show code example** from `banking/routes.py`:
   ```python
   # Safe query - no string concatenation
   user = User.query.filter_by(email=form.email.data).first()
   ```
3. No raw SQL queries with user input

---

## Key Security Features Checklist

Present this checklist to show compliance:

- ✅ **Authentication**:
  - Password hashing (PBKDF2)
  - Generic error messages
  - Login throttling (5 attempts/10 min)
  
- ✅ **Authorization**:
  - Role-based access control (4 roles)
  - `@roles_required` decorator on sensitive routes
  - HTTP 403 for unauthorized access

- ✅ **Input Validation**:
  - WTForms validation
  - Server-side checks
  - No SQL injection (ORM only)

- ✅ **Session Security**:
  - CSRF protection on all forms
  - HTTPOnly cookies
  - Session configuration

- ✅ **Audit Trail**:
  - All critical actions logged
  - Append-only logs
  - IP address tracking
  - User attribution

- ✅ **Business Logic**:
  - Account ownership validation
  - Balance verification
  - Account status checks
  - Atomic transactions

---

## Quick Test Scenarios

### Scenario 1: Unauthorized Access Attempt
1. Customer tries to access `/audit/logs` → **403 Forbidden**
2. Customer tries to freeze account → **403 Forbidden**

### Scenario 2: Transfer Validation
1. Try transfer with insufficient funds → **Blocked**
2. Try transfer from frozen account → **Blocked**
3. Valid transfer → **Success + Audit Log**

### Scenario 3: Audit Trail
1. Show login failures in audit log
2. Show successful transfers with details
3. Show role changes and who made them

---

## Additional Demo URLs

Direct access URLs for quick navigation:

- Dashboard: `http://127.0.0.1:5000/banking/dashboard`
- Open Account: `http://127.0.0.1:5000/banking/open-account`
- Internal Transfer: `http://127.0.0.1:5000/banking/transfer/internal`
- Transactions: `http://127.0.0.1:5000/banking/transactions`
- Create Ticket: `http://127.0.0.1:5000/support/create`
- Support Tickets (Staff): `http://127.0.0.1:5000/support/tickets`
- Audit Logs: `http://127.0.0.1:5000/audit/logs`
- Admin Users: `http://127.0.0.1:5000/banking/admin/users`
- Admin Accounts: `http://127.0.0.1:5000/banking/admin/accounts`

---

## Code Highlights to Show Professor

If professor wants to see code:

1. **RBAC Decorator** (`app/security.py`):
   ```python
   @roles_required('admin', 'auditor')
   def logs_list():
   ```

2. **Audit Logging** (`app/security.py`):
   ```python
   log_event('TRANSFER_CREATED', f'from={src} to={dst}')
   ```

3. **Transfer Validation** (`app/banking/routes.py`):
   ```python
   if src.owner_id != current_user.id:
       flash('Accounts must belong to you', 'danger')
   if src.balance < amount:
       flash('Insufficient funds', 'danger')
   ```

4. **Password Hashing** (`app/models.py`):
   ```python
   def set_password(self, raw_password):
       self.password_hash = generate_password_hash(raw_password)
   ```

---

## Questions Professor Might Ask

**Q: How do you prevent SQL injection?**
A: We use SQLAlchemy ORM exclusively. No raw SQL queries with string concatenation.

**Q: How is CSRF protection implemented?**
A: Flask-WTF's CSRFProtect is initialized globally. All forms include `{{ form.hidden_tag() }}`.

**Q: What happens if someone tries to access admin features?**
A: The `@roles_required` decorator checks the user's role and returns HTTP 403 if unauthorized.

**Q: How do you handle failed login attempts?**
A: In-memory throttling tracks failed attempts by email/IP. After 5 failures in 10 minutes, login is blocked. All attempts are logged.

**Q: Can audit logs be modified or deleted?**
A: No. There are no routes that allow editing or deleting audit logs. They are append-only.

**Q: How do you ensure business logic integrity?**
A: All validations are server-side. We check account ownership, status, and balance before any operation. Database transactions ensure atomicity.

---

## Quick Setup Reminder

If you need to restart the demo:

```powershell
# Navigate to project
cd "c:\Users\Samir Yaghi\Desktop\503M-project-test-2"

# Run the app
& "C:/Users/Samir Yaghi/Desktop/503M-project-test-2/.venv/Scripts/python.exe" run.py
```

Open browser: `http://127.0.0.1:5000`

---

Good luck with your demo! 🎓
