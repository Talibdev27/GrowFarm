from datetime import datetime
from werkzeug.security import generate_password_hash
import sys
sys.path.append(".")

from app import app, db
from models import User

def reset_admin_password():
    """Reset the admin user password or create if not exists."""
    with app.app_context():
        # Look for admin user
        admin_user = User.query.filter_by(username="admin").first()
        
        if admin_user:
            # Reset password
            admin_user.password_hash = generate_password_hash("Admin123!")
            db.session.commit()
            print(f"Admin password has been reset to 'Admin123!'")
            return True
        else:
            # Create new admin user
            admin_user = User(
                username="admin",
                email="admin@growfarm.com",
                password_hash=generate_password_hash("Admin123!"),
                role="admin",
                is_admin=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"New admin user created with password 'Admin123!'")
            return True

if __name__ == "__main__":
    reset_admin_password()