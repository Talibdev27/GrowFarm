from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import sys
sys.path.append(".")

from app import app, db
from models import User, Farmer, Project

def create_test_farmer_and_project():
    """Create a test farmer user and a test project."""
    with app.app_context():
        # 1. Create a farmer user if not exists
        farmer_user = User.query.filter_by(username="farmer").first()
        
        if not farmer_user:
            farmer_user = User(
                username="farmer",
                email="farmer@example.com",
                password_hash=generate_password_hash("Farmer123!"),
                role="farmer",
                is_admin=False,
                created_at=datetime.utcnow()
            )
            
            db.session.add(farmer_user)
            db.session.commit()
            
            print(f"Created farmer user (ID: {farmer_user.id})")
            print(f"Email: farmer@example.com")
            print(f"Password: Farmer123!")
        else:
            print(f"Farmer user already exists (ID: {farmer_user.id})")
        
        # 2. Create a farmer profile if not exists
        farmer_profile = Farmer.query.filter_by(user_id=farmer_user.id).first()
        
        if not farmer_profile:
            farmer_profile = Farmer(
                user_id=farmer_user.id,
                farm_name="Test Farm",
                farm_location="Test Location",
                description="A test farm for demonstration purposes.",
                experience_years=5,
                specialization="Organic Farming",
                phone="555-987-6543"
            )
            
            db.session.add(farmer_profile)
            db.session.commit()
            print(f"Created farmer profile (ID: {farmer_profile.id})")
        else:
            print(f"Farmer profile already exists (ID: {farmer_profile.id})")
        
        # 3. Create a test project
        project = Project.query.filter_by(title="Test Organic Farm Project").first()
        
        if not project:
            end_date = datetime.utcnow() + timedelta(days=90)
            
            project = Project(
                farmer_id=farmer_profile.id,
                title="Test Organic Farm Project",
                description="A test project for demonstrating the investment flow in GrowFarm. This organic farm project aims to produce sustainable crops using eco-friendly methods.",
                funding_goal=10000.0,
                current_funding=0.0,
                duration_months=3,
                expected_roi=15.0,
                risk_level="Medium",
                category="Organic",
                start_date=datetime.utcnow(),
                end_date=end_date,
                status="Open",
                created_at=datetime.utcnow(),
                location="Test City, Test Country",
                image_url="/static/img/projects/organic-farm.jpg",
                tags="organic,sustainable,test",
                overview="This is a test project for the GrowFarm platform.",
                regional_significance="Demonstrates local sustainable farming practices.",
                why_investment="Great opportunity to support organic farming.",
                min_investment=100.0,
                price_per_unit=10.0,
                total_acres=5.0,
                estimated_ownership_duration=12,
                investment_type="Equity"
            )
            
            db.session.add(project)
            db.session.commit()
            print(f"Created test project (ID: {project.id})")
        else:
            print(f"Test project already exists (ID: {project.id})")
        
        print("\nTest setup complete!")
        print("Try logging in with either:")
        print("1. Test investor: test@example.com / Test123!")
        print("2. Test farmer: farmer@example.com / Farmer123!")
        print("3. Admin: admin@growfarm.com / Admin123!")

if __name__ == "__main__":
    create_test_farmer_and_project()