from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])  # Removed strict Email validator for flexibility
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        # Add debugging print
        print(f"LoginForm initialized with: {args}, {kwargs}")

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('I am a', choices=[('investor', 'Investor'), ('farmer', 'Farmer')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one or login.')

class FarmerProfileForm(FlaskForm):
    farm_name = StringField('Farm Name', validators=[DataRequired(), Length(max=100)])
    farm_location = StringField('Farm Location', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Farm Description', validators=[DataRequired()])
    experience_years = IntegerField('Years of Experience', validators=[DataRequired(), NumberRange(min=0, max=100)])
    specialization = StringField('Specialization', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Save Profile')

class InvestorProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    bio = TextAreaField('Bio', validators=[Optional()])
    investment_focus = StringField('Investment Focus', validators=[Optional(), Length(max=200)])
    min_investment = FloatField('Minimum Investment ($)', validators=[Optional(), NumberRange(min=0)])
    max_investment = FloatField('Maximum Investment ($)', validators=[Optional(), NumberRange(min=0)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Save Profile')

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Project Description', validators=[DataRequired()])
    funding_goal = FloatField('Funding Goal ($)', validators=[DataRequired(), NumberRange(min=1)])
    duration_months = IntegerField('Project Duration (months)', validators=[DataRequired(), NumberRange(min=1, max=60)])
    expected_roi = FloatField('Expected ROI (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    risk_level = SelectField('Risk Level', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Crops', 'Crops'), 
        ('Livestock', 'Livestock'), 
        ('Dairy', 'Dairy'),
        ('Organic', 'Organic'),
        ('Sustainable', 'Sustainable'),
        ('Agroforestry', 'Agroforestry'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    submit = SubmitField('Submit Project')

class InvestmentForm(FlaskForm):
    amount = FloatField('Investment Amount ($)', validators=[DataRequired(), NumberRange(min=1)])
    project_id = HiddenField('Project ID', validators=[DataRequired()])
    submit = SubmitField('Invest Now')

class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Your Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=120)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class MessageForm(FlaskForm):
    recipient_id = HiddenField('Recipient ID', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=120)])
    body = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')
