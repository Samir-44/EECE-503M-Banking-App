from flask import Blueprint

banking_bp = Blueprint('banking', __name__, template_folder='templates')

from . import routes  # noqa: E402,F401
