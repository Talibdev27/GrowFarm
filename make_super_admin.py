from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='Talibdev', email='Mukhammadaminkhonesaev@gmail.com').first()
    if user:
        user.role = 'superadmin'
        user.is_admin = True
        db.session.commit()
        print(f"User {user.username} promoted to super admin.")
    else:
        print("User not found.") 