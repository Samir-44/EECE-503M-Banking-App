from flask import Blueprint

audit_bp = Blueprint('audit', __name__, template_folder='templates')

from . import routes  # noqa: E402,F401
