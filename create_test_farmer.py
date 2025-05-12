from app import app, db
from models import User, Farmer
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_farmer():
    with app.app_context():
        # Check if test farmer already exists
        test_farmer_email = "farmer@growfarm.com"
        existing_user = User.query.filter_by(email=test_farmer_email).first()
        
        if existing_user:
            print(f"Test farmer already exists with id: {existing_user.id}")
            
            # Check if farmer profile exists
            if existing_user.farmer:
                print(f"Farmer profile already exists with id: {existing_user.farmer.id}")
                return existing_user
            else:
                # Create farmer profile if it doesn't exist
                farmer = Farmer()
                farmer.user_id = existing_user.id
                farmer.farm_name = "Green Valley Farm"
                farmer.farm_location = "California, USA"
                farmer.description = "A sustainable farm focused on organic produce and sustainable farming methods."
                farmer.experience_years = 10
                farmer.specialization = "Organic Farming, Livestock"
                farmer.phone = "+1 (555) 123-4567"
                
                db.session.add(farmer)
                db.session.commit()
                print(f"Created farmer profile with id: {farmer.id}")
                return existing_user
        
        # Create new test farmer user
        user = User()
        user.username = "testfarmer"
        user.email = test_farmer_email
        user.password_hash = generate_password_hash("Farmer123!")
        user.role = "farmer"
        user.is_admin = False
        user.created_at = datetime.utcnow()
        
        db.session.add(user)
        db.session.commit()
        print(f"Created test farmer user with id: {user.id}")
        
        # Create farmer profile
        farmer = Farmer()
        farmer.user_id = user.id
        farmer.farm_name = "Green Valley Farm"
        farmer.farm_location = "California, USA"
        farmer.description = "A sustainable farm focused on organic produce and sustainable farming methods."
        farmer.experience_years = 10
        farmer.specialization = "Organic Farming, Livestock"
        farmer.phone = "+1 (555) 123-4567"
        
        db.session.add(farmer)
        db.session.commit()
        print(f"Created farmer profile with id: {farmer.id}")
        
        return user

if __name__ == "__main__":
    user = create_test_farmer()
    with app.app_context():
        user_id = user.id
        username = user.username
    print(f"Test farmer created successfully! ID: {user_id}, Username: {username}")