from flask import render_template, redirect, url_for, flash, request, abort, jsonify, send_file, session
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import func, desc
import io
import csv
from flask_babel import _, get_locale
from app import app, db
from models import User, Farmer, Investor, Project, Investment, Message
from forms import (LoginForm, RegistrationForm, FarmerProfileForm, InvestorProfileForm, 
                   ProjectForm, InvestmentForm, ContactForm, MessageForm)

# Custom Jinja2 filter to add months to a date
def monthsdelta(months):
    return timedelta(days=30 * months)
    
# Register custom filters
app.jinja_env.filters['monthsdelta'] = monthsdelta

def register_routes(app):
    
    @app.context_processor
    def inject_languages():
        """Inject language info into all templates"""
        return dict(
            available_languages=app.config['LANGUAGES'],
            current_locale=get_locale()
        )
    
    @app.route('/change_language/<lang_code>')
    def change_language(lang_code):
        """Route to change the language"""
        if lang_code in app.config['LANGUAGES']:
            session['language'] = lang_code
            # Get the referrer so we can redirect back to the same page
            referrer = request.referrer or url_for('index')
            return redirect(referrer)
        flash('Language not supported.', 'danger')
        return redirect(url_for('index'))
    
    # Admin access decorator
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin:
                flash(_('You do not have permission to access this page.'), 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/')
    def index():
        featured_projects = Project.query.filter_by(status='Open').order_by(Project.created_at.desc()).limit(3).all()
        return render_template('index.html', featured_projects=featured_projects)
    
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Login unsuccessful. Please check email and password', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            if user.role == 'farmer':
                farmer = Farmer(user_id=user.id, farm_name="", farm_location="", description="")
                db.session.add(farmer)
            else:  # investor
                investor = Investor(user_id=user.id, full_name="")
                db.session.add(investor)
            
            db.session.commit()
            
            flash('Your account has been created! Please complete your profile.', 'success')
            login_user(user)
            return redirect(url_for('profile'))
        
        return render_template('register.html', form=form)
    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.role == 'farmer':
            if not current_user.farmer or not current_user.farmer.farm_name:
                flash('Please complete your profile first', 'warning')
                return redirect(url_for('profile'))
            
            projects = Project.query.filter_by(farmer_id=current_user.farmer.id).order_by(Project.created_at.desc()).all()
            total_funding = sum(project.current_funding for project in projects)
            active_projects = sum(1 for project in projects if project.status == 'Open')
            
            return render_template('dashboard.html', 
                                  projects=projects, 
                                  total_funding=total_funding, 
                                  active_projects=active_projects)
        else:  # investor
            if not current_user.investor or not current_user.investor.full_name:
                flash('Please complete your profile first', 'warning')
                return redirect(url_for('profile'))
            
            investments = Investment.query.filter_by(investor_id=current_user.investor.id).all()
            total_invested = sum(investment.amount for investment in investments)
            projects_funded = len(set(investment.project_id for investment in investments))
            recommended_projects = Project.query.filter_by(status='Open').order_by(Project.created_at.desc()).limit(3).all()
            
            return render_template('dashboard.html', 
                                  investments=investments, 
                                  total_invested=total_invested, 
                                  projects_funded=projects_funded,
                                  recommended_projects=recommended_projects)
    
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        if current_user.role == 'farmer':
            form = FarmerProfileForm()
            
            if request.method == 'GET':
                if current_user.farmer:
                    form.farm_name.data = current_user.farmer.farm_name
                    form.farm_location.data = current_user.farmer.farm_location
                    form.description.data = current_user.farmer.description
                    form.experience_years.data = current_user.farmer.experience_years
                    form.specialization.data = current_user.farmer.specialization
                    form.phone.data = current_user.farmer.phone
            
            if form.validate_on_submit():
                if not current_user.farmer:
                    farmer = Farmer(
                        user_id=current_user.id,
                        farm_name=form.farm_name.data,
                        farm_location=form.farm_location.data,
                        description=form.description.data,
                        experience_years=form.experience_years.data,
                        specialization=form.specialization.data,
                        phone=form.phone.data
                    )
                    db.session.add(farmer)
                else:
                    current_user.farmer.farm_name = form.farm_name.data
                    current_user.farmer.farm_location = form.farm_location.data
                    current_user.farmer.description = form.description.data
                    current_user.farmer.experience_years = form.experience_years.data
                    current_user.farmer.specialization = form.specialization.data
                    current_user.farmer.phone = form.phone.data
                
                db.session.commit()
                flash('Your profile has been updated!', 'success')
                return redirect(url_for('dashboard'))
            
            return render_template('farmer_profile.html', form=form)
        
        else:  # investor
            form = InvestorProfileForm()
            
            if request.method == 'GET':
                if current_user.investor:
                    form.full_name.data = current_user.investor.full_name
                    form.bio.data = current_user.investor.bio
                    form.investment_focus.data = current_user.investor.investment_focus
                    form.min_investment.data = current_user.investor.min_investment
                    form.max_investment.data = current_user.investor.max_investment
                    form.phone.data = current_user.investor.phone
            
            if form.validate_on_submit():
                if not current_user.investor:
                    investor = Investor(
                        user_id=current_user.id,
                        full_name=form.full_name.data,
                        bio=form.bio.data,
                        investment_focus=form.investment_focus.data,
                        min_investment=form.min_investment.data,
                        max_investment=form.max_investment.data,
                        phone=form.phone.data
                    )
                    db.session.add(investor)
                else:
                    current_user.investor.full_name = form.full_name.data
                    current_user.investor.bio = form.bio.data
                    current_user.investor.investment_focus = form.investment_focus.data
                    current_user.investor.min_investment = form.min_investment.data
                    current_user.investor.max_investment = form.max_investment.data
                    current_user.investor.phone = form.phone.data
                
                db.session.commit()
                flash('Your profile has been updated!', 'success')
                return redirect(url_for('dashboard'))
            
            return render_template('investor_profile.html', form=form)
    
    @app.route('/projects')
    def projects():
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category', None)
        risk = request.args.get('risk', None)
        
        query = Project.query.filter_by(status='Open')
        
        if category:
            query = query.filter_by(category=category)
        if risk:
            query = query.filter_by(risk_level=risk)
            
        projects = query.order_by(Project.created_at.desc()).paginate(page=page, per_page=6)
        
        categories = db.session.query(Project.category).distinct().all()
        categories = [c[0] for c in categories]
        
        return render_template('projects.html', 
                              projects=projects, 
                              categories=categories, 
                              selected_category=category,
                              selected_risk=risk)
    
    @app.route('/project/<int:project_id>')
    def project_details(project_id):
        project = Project.query.get_or_404(project_id)
        farmer = Farmer.query.get(project.farmer_id)
        investment_form = None
        
        if current_user.is_authenticated and current_user.role == 'investor':
            investment_form = InvestmentForm()
            investment_form.project_id.data = project.id
        
        return render_template('project_details.html', 
                              project=project, 
                              farmer=farmer,
                              investment_form=investment_form)
    
    @app.route('/create_project', methods=['GET', 'POST'])
    @login_required
    def create_project():
        if current_user.role != 'farmer':
            flash('Only farmers can create projects', 'danger')
            return redirect(url_for('dashboard'))
        
        if not current_user.farmer or not current_user.farmer.farm_name:
            flash('Please complete your profile first', 'warning')
            return redirect(url_for('profile'))
        
        form = ProjectForm()
        
        if form.validate_on_submit():
            end_date = datetime.utcnow() + timedelta(days=30 * form.duration_months.data)
            
            project = Project(
                farmer_id=current_user.farmer.id,
                title=form.title.data,
                description=form.description.data,
                funding_goal=form.funding_goal.data,
                duration_months=form.duration_months.data,
                expected_roi=form.expected_roi.data,
                risk_level=form.risk_level.data,
                category=form.category.data,
                end_date=end_date,
                status='Open'
            )
            
            db.session.add(project)
            db.session.commit()
            
            flash('Your project has been created!', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('create_project.html', form=form)
    
    @app.route('/invest', methods=['POST'])
    @login_required
    def invest():
        if current_user.role != 'investor':
            flash('Only investors can make investments', 'danger')
            return redirect(url_for('dashboard'))
        
        form = InvestmentForm()
        
        if form.validate_on_submit():
            project = Project.query.get_or_404(form.project_id.data)
            
            if project.status != 'Open':
                flash('This project is not open for investment', 'danger')
                return redirect(url_for('project_details', project_id=project.id))
            
            investment = Investment(
                investor_id=current_user.investor.id,
                project_id=project.id,
                amount=form.amount.data,
                status='Confirmed'
            )
            
            project.current_funding += form.amount.data
            
            if project.current_funding >= project.funding_goal:
                project.status = 'Funded'
            
            db.session.add(investment)
            db.session.commit()
            
            # Send message to the farmer
            message = Message(
                sender_id=current_user.id,
                recipient_id=project.farmer.user.id,
                subject=f"New Investment in {project.title}",
                body=f"Hello! I have invested ${form.amount.data} in your project '{project.title}'. Looking forward to its success!"
            )
            db.session.add(message)
            db.session.commit()
            
            flash(f'Successfully invested ${form.amount.data} in {project.title}', 'success')
            return redirect(url_for('dashboard'))
        
        flash('There was an error processing your investment', 'danger')
        return redirect(url_for('projects'))
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        form = ContactForm()
        
        if form.validate_on_submit():
            # For now, we'll just show a success message
            # In a real application, you would send an email or store the message
            flash('Your message has been sent! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
        
        return render_template('contact.html', form=form)
    
    @app.route('/messages')
    @login_required
    def messages():
        received_messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
        sent_messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.timestamp.desc()).all()
        
        return render_template('messages.html', 
                              received_messages=received_messages, 
                              sent_messages=sent_messages)
    
    @app.route('/send_message/<int:recipient_id>', methods=['GET', 'POST'])
    @login_required
    def send_message(recipient_id):
        recipient = User.query.get_or_404(recipient_id)
        form = MessageForm()
        
        if form.validate_on_submit():
            message = Message(
                sender_id=current_user.id,
                recipient_id=recipient_id,
                subject=form.subject.data,
                body=form.body.data
            )
            db.session.add(message)
            db.session.commit()
            
            flash('Your message has been sent!', 'success')
            return redirect(url_for('messages'))
        
        form.recipient_id.data = recipient_id
        
        return render_template('send_message.html', form=form, recipient=recipient)
    
    @app.route('/mark_read/<int:message_id>')
    @login_required
    def mark_read(message_id):
        message = Message.query.get_or_404(message_id)
        
        if message.recipient_id != current_user.id:
            abort(403)
        
        message.read = True
        db.session.commit()
        
        return redirect(url_for('messages'))
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_code=404, error_message="Page Not Found"), 404
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', error_code=403, error_message="Forbidden"), 403
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', error_code=500, error_message="Server Error"), 500
        
    # Admin Routes
    @app.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        # Get statistics for dashboard
        stats = {
            'users': User.query.count(),
            'farmers': Farmer.query.count(),
            'investors': Investor.query.count(),
            'projects': Project.query.count(),
            'funded_projects': Project.query.filter_by(status='Funded').count(),
            'total_investment': Investment.query.with_entities(func.sum(Investment.amount)).scalar() or 0,
            'avg_investment': db.session.query(func.avg(Investment.amount)).scalar() or 0
        }
        
        # Recent activities (placeholder - would be replaced with actual activity tracking)
        recent_activities = [
            {
                'timestamp': datetime.utcnow() - timedelta(hours=i),
                'username': f"User{i}",
                'action': action,
                'details': f"Details about {action.lower()}"
            } 
            for i, action in enumerate([
                'New Registration', 
                'Project Created', 
                'Investment Made', 
                'Profile Updated', 
                'Message Sent'
            ], 1)
        ]
        
        # Get recent users and projects
        new_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
        
        return render_template('admin/dashboard.html', 
                              stats=stats, 
                              recent_activities=recent_activities,
                              new_users=new_users,
                              recent_projects=recent_projects)
    
    @app.route('/admin/users')
    @login_required
    @admin_required
    def admin_users():
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Apply filters
        query = User.query
        
        role = request.args.get('role')
        if role:
            query = query.filter(User.role == role)
            
        search = request.args.get('search')
        if search:
            query = query.filter(
                (User.username.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%'))
            )
        
        # Get paginated results
        users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
        
        return render_template('admin/users.html', users=users.items, pagination=users)
    
    @app.route('/admin/user/<int:user_id>')
    @login_required
    @admin_required
    def admin_user_details(user_id):
        user = User.query.get_or_404(user_id)
        return render_template('admin/user_details.html', user=user)
    
    @app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_edit_user(user_id):
        user = User.query.get_or_404(user_id)
        
        if request.method == 'POST':
            user.username = request.form.get('username')
            user.email = request.form.get('email')
            user.role = request.form.get('role')
            user.is_admin = 'is_admin' in request.form
            
            if request.form.get('password'):
                user.set_password(request.form.get('password'))
                
            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('admin_users'))
            
        return render_template('admin/edit_user.html', user=user)
    
    @app.route('/admin/user/add', methods=['POST'])
    @login_required
    @admin_required
    def admin_add_user():
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        is_admin = 'is_admin' in request.form
        
        # Check if user already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists', 'danger')
            return redirect(url_for('admin_users'))
        
        user = User(
            username=username,
            email=email,
            role=role,
            is_admin=is_admin,
            created_at=datetime.utcnow()
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create related profile
        if role == 'farmer':
            farmer = Farmer(user_id=user.id, farm_name="New Farm", farm_location="Location")
            db.session.add(farmer)
        elif role == 'investor':
            investor = Investor(user_id=user.id, full_name=username)
            db.session.add(investor)
            
        db.session.commit()
        flash('User added successfully', 'success')
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
    @login_required
    @admin_required
    def admin_delete_user(user_id):
        user = User.query.get_or_404(user_id)
        
        if user.id == current_user.id:
            flash('You cannot delete your own account', 'danger')
            return redirect(url_for('admin_users'))
            
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/projects')
    @login_required
    @admin_required
    def admin_projects():
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Apply filters
        query = Project.query
        
        status = request.args.get('status')
        if status:
            query = query.filter(Project.status == status)
            
        category = request.args.get('category')
        if category:
            query = query.filter(Project.category == category)
            
        search = request.args.get('search')
        if search:
            query = query.filter(
                (Project.title.ilike(f'%{search}%')) |
                (Project.description.ilike(f'%{search}%'))
            )
        
        # Get paginated results
        projects = query.order_by(Project.created_at.desc()).paginate(page=page, per_page=per_page)
        
        return render_template('admin/projects.html', projects=projects.items, pagination=projects)
    
    @app.route('/admin/project/<int:project_id>')
    @login_required
    @admin_required
    def admin_project_details(project_id):
        project = Project.query.get_or_404(project_id)
        return render_template('admin/project_details.html', project=project)
        
    @app.route('/admin/project/create', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_create_project():
        farmers = Farmer.query.all()
        
        if request.method == 'POST':
            # Get form data
            farmer_id = request.form.get('farmer_id')
            title = request.form.get('title')
            description = request.form.get('description')
            location = request.form.get('location')
            funding_goal = float(request.form.get('funding_goal'))
            current_funding = float(request.form.get('current_funding', 0))
            duration_months = int(request.form.get('duration_months'))
            expected_roi = float(request.form.get('expected_roi'))
            risk_level = request.form.get('risk_level')
            category = request.form.get('category')
            status = request.form.get('status')
            
            # Create new project
            project = Project()
            project.farmer_id = farmer_id
            project.title = title
            project.description = description
            project.location = location
            project.funding_goal = funding_goal
            project.current_funding = current_funding
            project.duration_months = duration_months
            project.expected_roi = expected_roi
            project.risk_level = risk_level
            project.category = category
            project.status = status
            
            # Additional info
            project.image_url = request.form.get('image_url')
            project.tags = request.form.get('tags')
            project.overview = request.form.get('overview')
            project.regional_significance = request.form.get('regional_significance')
            project.why_investment = request.form.get('why_investment')
            project.documents = request.form.get('documents')
            
            # Financial details
            min_investment = request.form.get('min_investment')
            if min_investment:
                project.min_investment = float(min_investment)
                
            price_per_unit = request.form.get('price_per_unit')
            if price_per_unit:
                project.price_per_unit = float(price_per_unit)
            
            # Land details
            total_acres = request.form.get('total_acres')
            if total_acres:
                project.total_acres = float(total_acres)
                
            estimated_ownership_duration = request.form.get('estimated_ownership_duration')
            if estimated_ownership_duration:
                project.estimated_ownership_duration = int(estimated_ownership_duration)
                
            project.investment_type = request.form.get('investment_type')
            
            # Set dates
            project.start_date = datetime.utcnow()
            # Calculate end date based on duration
            if project.duration_months:
                end_date = project.start_date + timedelta(days=30 * project.duration_months)
                project.end_date = end_date
            
            db.session.add(project)
            db.session.commit()
            flash('Project created successfully', 'success')
            return redirect(url_for('admin_projects'))
            
        return render_template('admin/create_project.html', farmers=farmers)
    
    @app.route('/admin/project/<int:project_id>/edit', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_edit_project(project_id):
        project = Project.query.get_or_404(project_id)
        
        if request.method == 'POST':
            # Basic info
            project.title = request.form.get('title')
            project.description = request.form.get('description')
            project.location = request.form.get('location')
            project.funding_goal = float(request.form.get('funding_goal'))
            project.current_funding = float(request.form.get('current_funding', 0))
            project.duration_months = int(request.form.get('duration_months'))
            project.expected_roi = float(request.form.get('expected_roi'))
            project.risk_level = request.form.get('risk_level')
            project.category = request.form.get('category')
            project.status = request.form.get('status')
            
            # Additional info
            image_url = request.form.get('image_url')
            # Only update image URL if it's been changed
            if image_url != project.image_url:
                project.image_url = image_url
                
            project.tags = request.form.get('tags')
            project.overview = request.form.get('overview')
            project.regional_significance = request.form.get('regional_significance')
            project.why_investment = request.form.get('why_investment')
            project.documents = request.form.get('documents')
            
            # Financial details
            if request.form.get('min_investment'):
                project.min_investment = float(request.form.get('min_investment'))
            if request.form.get('price_per_unit'):
                project.price_per_unit = float(request.form.get('price_per_unit'))
            
            # Land details
            if request.form.get('total_acres'):
                project.total_acres = float(request.form.get('total_acres'))
            if request.form.get('estimated_ownership_duration'):
                project.estimated_ownership_duration = int(request.form.get('estimated_ownership_duration'))
                
            project.investment_type = request.form.get('investment_type')
            
            db.session.commit()
            flash('Project updated successfully', 'success')
            return redirect(url_for('admin_projects'))
            
        return render_template('admin/edit_project.html', project=project)
    
    @app.route('/admin/project/<int:project_id>/delete', methods=['POST'])
    @login_required
    @admin_required
    def admin_delete_project(project_id):
        try:
            project = Project.query.get_or_404(project_id)
            project_title = project.title  # Save for flash message
            
            # First, explicitly delete all investments associated with this project
            try:
                investments = Investment.query.filter_by(project_id=project_id).all()
                if investments:
                    for investment in investments:
                        db.session.delete(investment)
                    db.session.commit()
                    print(f"Successfully deleted {len(investments)} investments for project {project_id}")
                else:
                    print(f"No investments found for project {project_id}")
            except Exception as investment_error:
                db.session.rollback()
                # Log the error but continue with trying to delete the project
                print(f"Error deleting investments: {str(investment_error)}")
                app.logger.error(f"Error deleting investments for project {project_id}: {str(investment_error)}")
            
            # Now delete the project itself
            try:
                db.session.delete(project)
                db.session.commit()
                flash(f'Project "{project_title}" deleted successfully', 'success')
                print(f"Successfully deleted project {project_id}")
                return redirect(url_for('admin_projects'))
            except Exception as project_error:
                db.session.rollback()
                app.logger.error(f"Error deleting project {project_id}: {str(project_error)}")
                flash(f'Error deleting project: {str(project_error)}', 'danger')
                
        except Exception as e:
            app.logger.error(f"Error finding project {project_id}: {str(e)}")
            flash(f'Error finding project: {str(e)}', 'danger')
        
        return redirect(url_for('admin_projects'))
    
    @app.route('/admin/investments')
    @login_required
    @admin_required
    def admin_investments():
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Apply filters
        query = Investment.query
        
        status = request.args.get('status')
        if status:
            query = query.filter(Investment.status == status)
            
        min_amount = request.args.get('min_amount', type=float)
        if min_amount:
            query = query.filter(Investment.amount >= min_amount)
            
        max_amount = request.args.get('max_amount', type=float)
        if max_amount:
            query = query.filter(Investment.amount <= max_amount)
            
        search = request.args.get('search')
        if search:
            query = query.join(Investor).join(User, Investor.user_id == User.id).join(Project).filter(
                (User.username.ilike(f'%{search}%')) |
                (Project.title.ilike(f'%{search}%'))
            )
        
        # Get paginated results
        investments = query.order_by(Investment.date.desc()).paginate(page=page, per_page=per_page)
        
        return render_template('admin/investments.html', investments=investments.items, pagination=investments)
    
    @app.route('/admin/investment/<int:investment_id>')
    @login_required
    @admin_required
    def admin_investment_details(investment_id):
        investment = Investment.query.get_or_404(investment_id)
        return render_template('admin/investment_details.html', investment=investment)
    
    @app.route('/admin/investment/<int:investment_id>/update', methods=['POST'])
    @login_required
    @admin_required
    def admin_update_investment_status(investment_id):
        investment = Investment.query.get_or_404(investment_id)
        
        status = request.form.get('status')
        investment.status = status
        
        db.session.commit()
        flash('Investment status updated successfully', 'success')
        return redirect(url_for('admin_investments'))
        
    @app.route('/admin/investment/<int:investment_id>/delete', methods=['POST'])
    @login_required
    @admin_required
    def admin_delete_investment(investment_id):
        investment = Investment.query.get_or_404(investment_id)
        
        # Update the project's current funding
        project = investment.project
        project.current_funding -= investment.amount
        if project.current_funding < 0:
            project.current_funding = 0
            
        # Delete the investment
        db.session.delete(investment)
        db.session.commit()
        
        flash('Investment deleted successfully', 'success')
        return redirect(url_for('admin_investments'))
        
    @app.route('/admin/project/<int:project_id>/update-status', methods=['POST'])
    @login_required
    @admin_required
    def admin_update_project_status(project_id):
        project = Project.query.get_or_404(project_id)
        
        status = request.form.get('status')
        project.status = status
        
        # If project is marked as completed, set end date
        if status == 'Completed' and not project.end_date:
            project.end_date = datetime.utcnow()
            
        db.session.commit()
        flash('Project status updated successfully', 'success')
        return redirect(url_for('admin_project_details', project_id=project.id))
        
    @app.route('/admin/user/<int:user_id>/edit-farmer-profile', methods=['POST'])
    @login_required
    @admin_required
    def admin_edit_farmer_profile(user_id):
        user = User.query.get_or_404(user_id)
        
        if not user.farmer:
            flash('User does not have a farmer profile', 'danger')
            return redirect(url_for('admin_edit_user', user_id=user.id))
            
        farmer = user.farmer
        farmer.farm_name = request.form.get('farm_name')
        farmer.farm_location = request.form.get('farm_location')
        farmer.description = request.form.get('description')
        farmer.experience_years = request.form.get('experience_years')
        farmer.specialization = request.form.get('specialization')
        farmer.phone = request.form.get('phone')
        
        db.session.commit()
        flash('Farmer profile updated successfully', 'success')
        return redirect(url_for('admin_edit_user', user_id=user.id))
        
    @app.route('/admin/user/<int:user_id>/edit-investor-profile', methods=['POST'])
    @login_required
    @admin_required
    def admin_edit_investor_profile(user_id):
        user = User.query.get_or_404(user_id)
        
        if not user.investor:
            flash('User does not have an investor profile', 'danger')
            return redirect(url_for('admin_edit_user', user_id=user.id))
            
        investor = user.investor
        investor.full_name = request.form.get('full_name')
        investor.bio = request.form.get('bio')
        investor.investment_focus = request.form.get('investment_focus')
        investor.min_investment = request.form.get('min_investment')
        investor.max_investment = request.form.get('max_investment')
        investor.phone = request.form.get('phone')
        
        db.session.commit()
        flash('Investor profile updated successfully', 'success')
        return redirect(url_for('admin_edit_user', user_id=user.id))
    
    @app.route('/admin/reports')
    @login_required
    @admin_required
    def admin_reports():
        # Get date range for filtering
        end_date = request.args.get('end_date')
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.utcnow()
        
        start_date = request.args.get('start_date')
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else end_date - timedelta(days=30)
        
        # User growth data (last 6 months)
        months = 6
        labels = []
        farmer_data = []
        investor_data = []
        
        for i in range(months, 0, -1):
            month_date = datetime.utcnow() - timedelta(days=30*i)
            month_label = month_date.strftime('%b %Y')
            labels.append(month_label)
            
            farmer_count = Farmer.query.join(User).filter(
                User.created_at < month_date
            ).count()
            farmer_data.append(farmer_count)
            
            investor_count = Investor.query.join(User).filter(
                User.created_at < month_date
            ).count()
            investor_data.append(investor_count)
            
        # Investment distribution by category
        investment_categories = []
        investment_distribution = []
        
        category_totals = db.session.query(
            Project.category, 
            func.sum(Investment.amount).label('total')
        ).join(Investment).group_by(Project.category).order_by(desc('total')).all()
        
        for category, total in category_totals:
            investment_categories.append(category)
            investment_distribution.append(float(total))
            
        # Project distribution by category
        project_categories = []
        project_distribution = []
        
        project_counts = db.session.query(
            Project.category, 
            func.count(Project.id).label('count')
        ).group_by(Project.category).order_by(desc('count')).all()
        
        for category, count in project_counts:
            project_categories.append(category)
            project_distribution.append(count)
            
        # Monthly investment trends (last 12 months)
        monthly_labels = []
        monthly_investments = []
        
        for i in range(12, 0, -1):
            month_date = datetime.utcnow() - timedelta(days=30*i)
            next_month = month_date + timedelta(days=30)
            month_label = month_date.strftime('%b %Y')
            monthly_labels.append(month_label)
            
            monthly_total = db.session.query(
                func.sum(Investment.amount)
            ).filter(
                Investment.date >= month_date,
                Investment.date < next_month
            ).scalar() or 0
            
            monthly_investments.append(float(monthly_total))
        
        return render_template(
            'admin/reports.html',
            user_growth_labels=labels,
            farmer_growth_data=farmer_data,
            investor_growth_data=investor_data,
            investment_categories=investment_categories,
            investment_distribution=investment_distribution,
            project_categories=project_categories,
            project_distribution=project_distribution,
            monthly_labels=monthly_labels,
            monthly_investments=monthly_investments
        )
    
    @app.route('/admin/reports/download/<report_type>')
    @login_required
    @admin_required
    def admin_download_report(report_type):
        # Create a CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        if report_type == 'users':
            writer.writerow(['ID', 'Username', 'Email', 'Role', 'Is Admin', 'Created At'])
            users = User.query.all()
            for user in users:
                writer.writerow([
                    user.id,
                    user.username,
                    user.email,
                    user.role,
                    user.is_admin,
                    user.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            filename = 'users_report.csv'
            
        elif report_type == 'projects':
            writer.writerow([
                'ID', 'Title', 'Farmer', 'Funding Goal', 'Current Funding', 
                'Duration (months)', 'Expected ROI', 'Risk Level', 'Category',
                'Status', 'Created At'
            ])
            projects = Project.query.all()
            for project in projects:
                writer.writerow([
                    project.id,
                    project.title,
                    project.farmer.farm_name,
                    project.funding_goal,
                    project.current_funding,
                    project.duration_months,
                    project.expected_roi,
                    project.risk_level,
                    project.category,
                    project.status,
                    project.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            filename = 'projects_report.csv'
            
        elif report_type == 'investments':
            writer.writerow([
                'ID', 'Investor', 'Project', 'Amount', 'Date', 'Status'
            ])
            investments = Investment.query.all()
            for investment in investments:
                writer.writerow([
                    investment.id,
                    investment.investor.full_name,
                    investment.project.title,
                    investment.amount,
                    investment.date.strftime('%Y-%m-%d %H:%M:%S'),
                    investment.status
                ])
            filename = 'investments_report.csv'
            
        elif report_type == 'financial':
            writer.writerow([
                'Category', 'Total Investment', 'Project Count', 'Average Investment'
            ])
            categories = db.session.query(Project.category).distinct().all()
            for (category,) in categories:
                projects_count = Project.query.filter_by(category=category).count()
                total_investment = db.session.query(
                    func.sum(Investment.amount)
                ).join(Project).filter(Project.category == category).scalar() or 0
                avg = total_investment / projects_count if projects_count > 0 else 0
                
                writer.writerow([
                    category,
                    total_investment,
                    projects_count,
                    avg
                ])
            filename = 'financial_report.csv'
        else:
            abort(404)
            
        # Move to the beginning of the StringIO
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
