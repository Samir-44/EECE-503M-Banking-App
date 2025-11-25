from app import create_app
from app.extensions import db
from app.models import User

app = create_app()
with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email="admin@example.com").first()
    if not admin:
        admin = User(
            full_name="Admin User",
            email="admin@example.com",
            phone="",
            role="admin",
            is_active=True
        )
        admin.set_password("Admin123!")
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created: admin@example.com / Admin123!")
    else:
        print("✓ Admin user already exists: admin@example.com")
