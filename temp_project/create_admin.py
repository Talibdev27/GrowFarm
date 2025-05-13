from datetime import datetime
from werkzeug.security import generate_password_hash
import sys
sys.path.append(".")  # Add current directory to path

from app import app, db
from models import User

def create_admin_user(username, email, password):
    """Create an admin user with the given credentials."""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"Error: User with username '{username}' or email '{email}' already exists.")
            return False
        
        # Create new admin user
        admin_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role="admin",
            is_admin=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Success: Admin user '{username}' created successfully.")
        return True

if __name__ == "__main__":
    # Default admin credentials
    username = "admin"
    email = "admin@growfarm.com"
    password = "Admin123!"
    
    # If command line arguments are provided, use them
    if len(sys.argv) == 4:
        username = sys.argv[1]
        email = sys.argv[2]
        password = sys.argv[3]
    
    create_admin_user(username, email, password)