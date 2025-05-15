from datetime import datetime
from werkzeug.security import generate_password_hash
import sys
sys.path.append(".")

from app import app, db
from models import User, Investor

def create_test_user():
    """Create a test user for login testing."""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username="test").first()
        
        if existing_user:
            print(f"Test user already exists (ID: {existing_user.id})")
            print(f"Email: test@example.com")
            print(f"Password: Test123!")
            return True
        
        # Create new test user
        test_user = User(
            username="test",
            email="test@example.com",
            password_hash=generate_password_hash("Test123!"),
            role="investor",
            is_admin=False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        # Create investor profile for the user
        investor = Investor(
            user_id=test_user.id,
            full_name="Test User",
            bio="Test investor account",
            investment_focus="Testing",
            min_investment=100.0,
            max_investment=1000.0,
            phone="555-123-4567"
        )
        
        db.session.add(investor)
        db.session.commit()
        
        print(f"Test user created (ID: {test_user.id})")
        print(f"Email: test@example.com")
        print(f"Password: Test123!")
        return True

if __name__ == "__main__":
    create_test_user()