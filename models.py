from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'investor', 'farmer', or 'admin'
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    farmer = db.relationship('Farmer', backref='user', uselist=False, cascade="all, delete-orphan")
    investor = db.relationship('Investor', backref='user', uselist=False, cascade="all, delete-orphan")
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    farm_name = db.Column(db.String(100), nullable=False)
    farm_location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    # Relationships
    projects = db.relationship('Project', backref='farmer', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Farmer {self.farm_name}>'


class Investor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    investment_focus = db.Column(db.String(200))
    min_investment = db.Column(db.Float)
    max_investment = db.Column(db.Float)
    phone = db.Column(db.String(20))
    
    # Relationships
    investments = db.relationship('Investment', backref='investor', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Investor {self.full_name}>'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    funding_goal = db.Column(db.Float, nullable=False)
    current_funding = db.Column(db.Float, default=0.0)
    duration_months = db.Column(db.Integer, nullable=False)
    expected_roi = db.Column(db.Float, nullable=False)  # Return on Investment (%)
    risk_level = db.Column(db.String(20), nullable=False)  # 'Low', 'Medium', 'High'
    category = db.Column(db.String(50), nullable=False)  # e.g., 'Crops', 'Livestock', 'Dairy', etc.
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Open')  # 'Open', 'Funded', 'Completed', 'Cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    investments = db.relationship('Investment', backref='project', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Project {self.title}>'

    def calculate_progress(self):
        """Calculate the funding progress as a percentage."""
        if self.funding_goal <= 0:
            return 0
        return min(100, (self.current_funding / self.funding_goal) * 100)


class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.Integer, db.ForeignKey('investor.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Confirmed', 'Completed', 'Cancelled'

    def __repr__(self):
        return f'<Investment ${self.amount} in Project {self.project_id}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Message {self.subject}>'
