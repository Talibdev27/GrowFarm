from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
from app import db
from models import User, Farmer, Investor, Project, Investment, Message
from forms import (LoginForm, RegistrationForm, FarmerProfileForm, InvestorProfileForm, 
                   ProjectForm, InvestmentForm, ContactForm, MessageForm)

def register_routes(app):
    
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
