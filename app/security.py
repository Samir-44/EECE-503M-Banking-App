from functools import wraps
from flask import abort, request
from flask_login import current_user
from .extensions import db
from .models import AuditLog
from datetime import datetime, timedelta
import time

# Simple in-memory failed attempts tracker for dev. Keyed by (email or ip).
FAILED_LOGIN_ATTEMPTS = {}
LOCKOUT_THRESHOLD = 5
LOCKOUT_WINDOW = 600  # seconds


def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return decorator


def log_event(action, details=""):
    try:
        ip = request.remote_addr
    except Exception:
        ip = None
    entry = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        details=details,
        ip_address=ip,
        timestamp=datetime.utcnow(),
    )
    db.session.add(entry)
    db.session.commit()


def record_failed_login(key):
    now = time.time()
    attempts = FAILED_LOGIN_ATTEMPTS.get(key, [])
    attempts = [t for t in attempts if now - t < LOCKOUT_WINDOW]
    attempts.append(now)
    FAILED_LOGIN_ATTEMPTS[key] = attempts
    return len(attempts)


def is_locked_out(key):
    attempts = FAILED_LOGIN_ATTEMPTS.get(key, [])
    now = time.time()
    attempts = [t for t in attempts if now - t < LOCKOUT_WINDOW]
    FAILED_LOGIN_ATTEMPTS[key] = attempts
    return len(attempts) >= LOCKOUT_THRESHOLD
