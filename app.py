import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database (using PostgreSQL)
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Handle potential postgres:// URLs (SQLAlchemy 1.4+ requires postgresql://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # Fallback for development (though we should always have DATABASE_URL)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///growfarm.db"
    print("WARNING: DATABASE_URL not set, using SQLite instead")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the extensions with the app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import routes and models after initializing extensions to avoid circular imports
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    from models import User, Farmer, Investor, Project, Investment, Message

    # Import and register routes
    from routes import register_routes
    register_routes(app)

    # Create database tables
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
