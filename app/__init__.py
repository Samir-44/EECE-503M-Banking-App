import os
from flask import Flask, redirect, url_for
from .config import Config
from .extensions import db, migrate, login_manager, csrf


def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    app.config.from_object(Config)

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # import blueprints
    from .auth.routes import auth_bp
    from .banking.routes import banking_bp
    from .support.routes import support_bp
    from .audit.routes import audit_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(banking_bp, url_prefix="/banking")
    app.register_blueprint(support_bp, url_prefix="/support")
    app.register_blueprint(audit_bp, url_prefix="/audit")

    @app.route("/")
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('banking.dashboard'))
        return redirect(url_for('auth.login'))

    return app
