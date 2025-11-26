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
        print("✓ Admin user created: admin@example.com / Admin123!")
    else:
        print("✓ Admin user already exists: admin@example.com")
    
    # Check if support agent exists
    support = User.query.filter_by(email="support@example.com").first()
    if not support:
        support = User(
            full_name="Support Agent",
            email="support@example.com",
            phone="555-2000",
            role="support",
            is_active=True
        )
        support.set_password("Support123!")
        db.session.add(support)
        print("✓ Support agent created: support@example.com / Support123!")
    else:
        print("✓ Support agent already exists: support@example.com")
    
    # Check if auditor exists
    auditor = User.query.filter_by(email="auditor@example.com").first()
    if not auditor:
        auditor = User(
            full_name="Auditor User",
            email="auditor@example.com",
            phone="555-3000",
            role="auditor",
            is_active=True
        )
        auditor.set_password("Auditor123!")
        db.session.add(auditor)
        print("✓ Auditor created: auditor@example.com / Auditor123!")
    else:
        print("✓ Auditor already exists: auditor@example.com")
    
    db.session.commit()
