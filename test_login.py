import sys
sys.path.append('.')

from app import app, db
from models import User
from werkzeug.security import check_password_hash

def test_login(email, password):
    """Test login for a specific user"""
    with app.app_context():
        print(f"\nTesting login for email: {email}")
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"No user found with email: {email}")
            return False
        
        print(f"Found user: {user.username} (ID: {user.id}, Role: {user.role})")
        
        # Test password
        print(f"Testing password: {password}")
        # First test with direct hash checking 
        password_match = check_password_hash(user.password_hash, password)
        print(f"Direct password check result: {password_match}")
        
        # Then test with the User method
        model_password_match = user.check_password(password)
        print(f"Model password check result: {model_password_match}")
        
        return password_match

if __name__ == "__main__":
    # Test admin login
    test_login('admin@growfarm.com', 'Admin123!')
    
    # Test investor login
    test_login('test@example.com', 'Test123!')
    
    # Test farmer login
    test_login('farmer@example.com', 'Farmer123!')