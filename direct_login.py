import sys
import os
import json
from datetime import timedelta
from flask import Flask, session

# Add current directory to path
sys.path.append('.')

from app import app, db
from models import User

def create_session_data(user_id):
    """Create a session file with login data"""
    with app.app_context():
        user = User.query.get(user_id)
        
        if not user:
            print(f"User with ID {user_id} not found")
            return False
        
        # Create session data
        session_data = {
            '_fresh': True,
            '_id': '1234567890abcdef',
            '_permanent': True,
            '_user_id': str(user.id),
            'user_id': user.id,
            'csrf_token': 'dummy_csrf_token',
            'language': 'en'
        }
        
        # Save to file
        with open('session_data.json', 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"Session data created for {user.username} (ID: {user.id})")
        print("Instructions:")
        print("1. Download 'session_data.json'")
        print("2. Use browser developer tools to inject this session data")
        print("3. Then refresh the page")
        
        return True

if __name__ == '__main__':
    # Get user_id from command line or use default (admin)
    user_id = 1  # Default admin ID
    
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
        except ValueError:
            print(f"Invalid user ID: {sys.argv[1]}")
            sys.exit(1)
    
    success = create_session_data(user_id)
    if not success:
        sys.exit(1)