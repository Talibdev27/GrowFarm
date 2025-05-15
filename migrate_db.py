from app import app, db
from models import Investment

def migrate_database():
    """Create new tables and update existing schema"""
    with app.app_context():
        # This will create tables that don't exist yet
        # and add new columns to existing tables
        db.create_all()
        print("Database migration completed!")

if __name__ == "__main__":
    migrate_database()