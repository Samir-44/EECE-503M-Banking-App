from flask import render_template, request
from flask_login import login_required
from . import audit_bp
from ..security import roles_required
from ..models import AuditLog


@audit_bp.route('/logs')
@login_required
@roles_required('auditor', 'admin')
def logs_list():
    q = AuditLog.query.order_by(AuditLog.timestamp.desc())
    # simple filters
    action = request.args.get('action')
    if action:
        q = q.filter(AuditLog.action == action)
    logs = q.limit(500).all()
    return render_template('audit/logs_list.html', logs=logs)
