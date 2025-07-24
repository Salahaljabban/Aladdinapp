from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import traceback
import os
from config import config

# Create Flask app instance (will be configured in create_app)
app = Flask(__name__)

# Initialize database
db = SQLAlchemy()

# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'login'  # Specify the login view

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')  # Add role attribute
    profile = db.relationship('Profile', backref='user', uselist=False) # One to one relationship

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"


# Define Profile model
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)

    def __repr__(self):
        return f"Profile('{self.first_name}', '{self.last_name}')"

# Define Risk model
class Risk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    likelihood = db.Column(db.String(50))
    impact = db.Column(db.String(50))
    risk_owner = db.Column(db.String(100))
    mitigation_plan = db.Column(db.Text)
    status = db.Column(db.String(50), default='Open')
    date_identified = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Risk('{self.title}', '{self.risk_owner}', '{self.status}')"

# Define Control model
class Control(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    owner = db.Column(db.String(100))
    status = db.Column(db.String(50), default='Active')
    date_implemented = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Control('{self.name}', '{self.owner}', '{self.status}')"

# Define Incident model
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_occurred = db.Column(db.DateTime, default=datetime.utcnow)
    reported_by = db.Column(db.String(100))
    status = db.Column(db.String(50), default='Open')
    impact = db.Column(db.Text)
    corrective_action = db.Column(db.Text)

    def __repr__(self):
        return f"Incident('{self.title}', '{self.reported_by}', '{self.status}')"

# Flask route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# Flask route for register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Check if the username or email already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists. Please use a different one.', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password, method='scrypt')

        # Create a new user
        new_user = User(username=username, password=hashed_password, email=email)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Flask route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the user exists
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # Log in the user
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Flask route for dashboard page
@app.route('/dashboard')
@login_required
def dashboard():
    # Get dashboard statistics
    total_risks = Risk.query.count()
    active_controls = Control.query.filter_by(status='Active').count()
    open_incidents = Incident.query.filter_by(status='Open').count()
    
    # Get recent data
    recent_risks = Risk.query.order_by(Risk.date_identified.desc()).limit(5).all()
    recent_incidents = Incident.query.order_by(Incident.date_occurred.desc()).limit(5).all()
    
    # Calculate risk distribution
    high_risks = Risk.query.filter_by(impact='High').count()
    medium_risks = Risk.query.filter_by(impact='Medium').count()
    low_risks = Risk.query.filter_by(impact='Low').count()
    
    return render_template('dash.html', 
                         role=current_user.role,
                         total_risks=total_risks,
                         active_controls=active_controls,
                         open_incidents=open_incidents,
                         recent_risks=recent_risks,
                         recent_incidents=recent_incidents,
                         high_risks=high_risks,
                         medium_risks=medium_risks,
                         low_risks=low_risks)

# Flask route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

# Flask route for profile page
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(current_user.id)
    if not user.profile:
        profile = Profile(user_id = current_user.id)
        db.session.add(profile)
        db.session.commit()
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        profile.first_name = request.form.get('first_name')
        profile.last_name = request.form.get('last_name')
        profile.date_of_birth = request.form.get('date_of_birth')
        profile.address = request.form.get('address')
        profile.phone_number = request.form.get('phone_number')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', profile=profile)

# Flask route for risks page
@app.route('/risks')
@login_required
def risks():
    risks = Risk.query.all()
    return render_template('risks.html', risks=risks)

# Flask route for adding a new risk
@app.route('/risks/new', methods=['GET', 'POST'])
@login_required
def new_risk():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        likelihood = request.form.get('likelihood')
        impact = request.form.get('impact')
        risk_owner = request.form.get('risk_owner')
        mitigation_plan = request.form.get('mitigation_plan')

        new_risk = Risk(title=title, description=description, category=category,
                        likelihood=likelihood, impact=impact, risk_owner=risk_owner,
                        mitigation_plan=mitigation_plan)

        db.session.add(new_risk)
        db.session.commit()

        flash('Risk added successfully!', 'success')
        return redirect(url_for('risks'))

    return render_template('new_risk.html')

# Flask route for editing a risk
@app.route('/risks/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_risk(id):
    risk = Risk.query.get_or_404(id)

    if request.method == 'POST':
        risk.title = request.form.get('title')
        risk.description = request.form.get('description')
        risk.category = request.form.get('category')
        risk.likelihood = request.form.get('likelihood')
        risk.impact = request.form.get('impact')
        risk.risk_owner = request.form.get('risk_owner')
        risk.mitigation_plan = request.form.get('mitigation_plan')
        risk.status = request.form.get('status')

        db.session.commit()

        flash('Risk updated successfully!', 'success')
        return redirect(url_for('risks'))

    return render_template('edit_risk.html', risk=risk)

# Flask route for deleting a risk
@app.route('/risks/delete/<int:id>', methods=['POST'])
@login_required
def delete_risk(id):
    risk = Risk.query.get_or_404(id)
    db.session.delete(risk)
    db.session.commit()

    flash('Risk deleted successfully!', 'success')
    return redirect(url_for('risks'))

# Flask route for controls page
@app.route('/controls')
@login_required
def controls():
    controls = Control.query.all()
    return render_template('controls.html', controls=controls)

# Flask route for adding a new control
@app.route('/controls/new', methods=['GET', 'POST'])
@login_required
def new_control():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        type = request.form.get('type')
        frequency = request.form.get('frequency')
        owner = request.form.get('owner')

        new_control = Control(name=name, description=description, type=type,
                              frequency=frequency, owner=owner)

        db.session.add(new_control)
        db.session.commit()

        flash('Control added successfully!', 'success')
        return redirect(url_for('controls'))

    return render_template('new_control.html')

# Flask route for editing a control
@app.route('/controls/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_control(id):
    control = Control.query.get_or_404(id)

    if request.method == 'POST':
        control.name = request.form.get('name')
        control.description = request.form.get('description')
        control.type = request.form.get('type')
        control.frequency = request.form.get('frequency')
        control.owner = request.form.get('owner')
        control.status = request.form.get('status')

        db.session.commit()

        flash('Control updated successfully!', 'success')
        return redirect(url_for('controls'))

    return render_template('edit_control.html', control=control)

# Flask route for deleting a control
@app.route('/controls/delete/<int:id>', methods=['POST'])
@login_required
def delete_control(id):
    control = Control.query.get_or_404(id)
    db.session.delete(control)
    db.session.commit()

    flash('Control deleted successfully!', 'success')
    return redirect(url_for('controls'))

# Flask route for incidents page
@app.route('/incidents')
@login_required
def incidents():
    incidents = Incident.query.all()
    return render_template('incidents.html', incidents=incidents)

# Flask route for adding a new incident
@app.route('/incidents/new', methods=['GET', 'POST'])
@login_required
def new_incident():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_occurred = request.form.get('date_occurred')
        reported_by = request.form.get('reported_by')
        impact = request.form.get('impact')
        corrective_action = request.form.get('corrective_action')

        new_incident = Incident(title=title, description=description,
                                date_occurred=date_occurred, reported_by=reported_by,
                                impact=impact, corrective_action=corrective_action)

        db.session.add(new_incident)
        db.session.commit()

        flash('Incident added successfully!', 'success')
        return redirect(url_for('incidents'))

    return render_template('new_incident.html')

# Flask route for editing an incident
@app.route('/incidents/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_incident(id):
    incident = Incident.query.get_or_404(id)

    if request.method == 'POST':
        incident.title = request.form.get('title')
        incident.description = request.form.get('description')
        incident.date_occurred = request.form.get('date_occurred')
        incident.reported_by = request.form.get('reported_by')
        incident.status = request.form.get('status')
        incident.impact = request.form.get('impact')
        incident.corrective_action = request.form.get('corrective_action')

        db.session.commit()

        flash('Incident updated successfully!', 'success')
        return redirect(url_for('incidents'))

    return render_template('edit_incident.html', incident=incident)

# Flask route for deleting an incident
@app.route('/incidents/delete/<int:id>', methods=['POST'])
@login_required
def delete_incident(id):
    incident = Incident.query.get_or_404(id)
    db.session.delete(incident)
    db.session.commit()

    flash('Incident deleted successfully!', 'success')
    return redirect(url_for('incidents'))

# Flask route for compliance page
@app.route('/compliance')
@login_required
def compliance():
    return render_template('compliance/index.html')

# Flask route for policies page
@app.route('/policies')
@login_required
def policies():
    return render_template('policies/index.html')

def init_database():
    db.create_all()

    # Check if the admin user exists
    admin_user = User.query.filter_by(username='admin').first()

    if not admin_user:
        # Create the admin user with a default password
        hashed_password = generate_password_hash('admin', method='scrypt')
        admin_user = User(username='admin', password=hashed_password, email='admin@example.com', role='admin')
        db.session.add(admin_user)
        db.session.commit()
        print('Admin user created successfully!')
    else:
        print('Admin user already exists.')

def create_app(config_name=None):
    """Application factory function"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        init_database()

    return app

# This allows the app to be imported without running
if __name__ == '__main__':
    # If run directly, start the development server
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)