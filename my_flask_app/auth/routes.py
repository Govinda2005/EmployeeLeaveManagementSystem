# ELMS/my_flask_app/auth/routes.py
from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from my_flask_app.app import db, bcrypt
from my_flask_app.models import User, Role, AuditLog
from my_flask_app.forms import RegistrationForm, LoginForm
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard')) # Redirect if already logged in

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Assign 'Employee' role by default (assuming Role ID 3 for 'Employee')
        # You should ensure 'Employee' role exists in your DB with ID 3 or fetch it dynamically
        employee_role = Role.query.filter_by(name='Employee').first()
        if not employee_role:
            flash('Error: Employee role not found. Please contact an administrator.', 'danger')
            return render_template('register.html', title='Register', form=form)

        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password, role_id=employee_role.id)
        db.session.add(user)
        db.session.commit()

        # Log the registration action
        audit_log = AuditLog(user_id=user.id, action=f"User registered: {user.username}",
                             ip_address=request.remote_addr)
        db.session.add(audit_log)
        db.session.commit()

        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard')) # Redirect if already logged in

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            # Log the login action
            audit_log = AuditLog(user_id=user.id, action=f"User logged in: {user.username}",
                                 ip_address=request.remote_addr)
            db.session.add(audit_log)
            db.session.commit()

            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Handles user logout."""
    if current_user.is_authenticated:
        # Log the logout action
        audit_log = AuditLog(user_id=current_user.id, action=f"User logged out: {current_user.username}",
                             ip_address=request.remote_addr)
        db.session.add(audit_log)
        db.session.commit()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

# Placeholder for account page - will be expanded later
@auth_bp.route('/account')
@login_required
def account():
    """Renders the user account page."""
    return render_template('account.html', title='Account')
