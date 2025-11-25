from flask import Blueprint

support_bp = Blueprint('support', __name__, template_folder='templates')

from . import routes  # noqa: E402,F401
