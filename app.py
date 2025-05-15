import os
import logging
from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_babel import Babel

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
babel = Babel()

# Function to determine supported languages and select best match
def get_locale():
    # Check if user has explicitly set a language in the session
    if 'language' in session:
        selected_lang = session['language']
        print(f"Using language from session: {selected_lang}")
        return selected_lang
    
    # Otherwise try to detect from request header
    detected_lang = request.accept_languages.best_match(['en', 'ru', 'uz'])
    print(f"Detected language from headers: {detected_lang}")
    
    # If no language is detected, default to English
    if not detected_lang:
        print("No language detected, defaulting to English")
        return 'en'
        
    return detected_lang

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.config['WTF_CSRF_ENABLED'] = False  # Temporarily disable CSRF protection
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure Babel - Use absolute paths for reliability
translations_dir = os.path.join(os.getcwd(), 'translations')
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = translations_dir
app.config['LANGUAGES'] = {
    'en': 'English',
    'ru': 'Russian',
    'uz': 'Uzbek'
}

# Print directory for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Translation directory: {os.path.join(os.getcwd(), 'translations')}")
print(f"Available translations: {os.listdir('translations')}")

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
babel.init_app(app, locale_selector=get_locale)
print("Babel initialized with locale_selector function")

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
