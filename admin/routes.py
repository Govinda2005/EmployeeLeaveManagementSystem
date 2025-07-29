# ELMS/my_flask_app/admin/routes.py
from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_required, current_user
from my_flask_app.app import db, bcrypt
from my_flask_app.models import User, LeaveRequest, AuditLog, Role
from my_flask_app.forms import UserUpdateForm, PasswordResetForm, RegistrationForm
from my_flask_app.decorators import admin_required
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_dashboard')
@login_required
@admin_required # Only admins can access
def admin_dashboard():
    """Renders the admin dashboard with key metrics."""
    total_users = User.query.count()
    total_leaves = LeaveRequest.query.count()
    pending_leaves = LeaveRequest.query.filter_by(status='Pending').count()
    approved_leaves = LeaveRequest.query.filter_by(status='Approved').count()
    rejected_leaves = LeaveRequest.query.filter_by(status='Rejected').count()
    
    # Get recent audit logs
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()

    return render_template('admin_dashboard.html',
                           title='Admin Dashboard',
                           total_users=total_users,
                           total_leaves=total_leaves,
                           pending_leaves=pending_leaves,
                           approved_leaves=approved_leaves,
                           rejected_leaves=rejected_leaves,
                           recent_logs=recent_logs)

@admin_bp.route('/user_management')
@login_required
@admin_required
def user_management():
    """Displays a list of all users for admin to manage."""
    users = User.query.order_by(User.date_joined.asc()).all()
    return render_template('user_management.html', title='User Management', users=users)

@admin_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Allows admin to create new users."""
    form = RegistrationForm() # Reuse registration form for creating users
    # We might want a more specific form for admin user creation later, allowing role selection
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Default to Employee, admin can change later via edit_user
        employee_role = Role.query.filter_by(name='Employee').first()
        if not employee_role:
            flash('Error: Employee role not found. Please contact an administrator.', 'danger')
            return render_template('create_user.html', title='Create User', form=form)

        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password, role_id=employee_role.id)
        db.session.add(user)
        db.session.commit()

        audit_log = AuditLog(user_id=current_user.id,
                             action=f"Admin created new user: {user.username}",
                             ip_address=request.remote_addr)
        db.session.add(audit_log)
        db.session.commit()

        flash(f'User {form.username.data} created successfully!', 'success')
        return redirect(url_for('admin.user_management'))
    return render_template('create_user.html', title='Create User', form=form)


@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Allows admin to edit user details and assign roles."""
    user = User.query.get_or_404(user_id)
    form = UserUpdateForm(original_username=user.username, original_email=user.email)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data # Update role based on selection
        user.is_active = form.is_active.data
        db.session.commit()

        audit_log = AuditLog(user_id=current_user.id,
                             action=f"Admin updated user: {user.username} (ID: {user.id})",
                             ip_address=request.remote_addr)
        db.session.add(audit_log)
        db.session.commit()

        flash(f'User {user.username} has been updated!', 'success')
        return redirect(url_for('admin.user_management'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role_id # Pre-select current role
        form.is_active.data = user.is_active
    return render_template('edit_user.html', title='Edit User', form=form, user=user)

@admin_bp.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_password(user_id):
    """Allows admin to reset a user's password."""
    user = User.query.get_or_404(user_id)
    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        audit_log = AuditLog(user_id=current_user.id,
                             action=f"Admin reset password for user: {user.username} (ID: {user.id})",
                             ip_address=request.remote_addr)
        db.session.add(audit_log)
        db.session.commit()

        flash(f'Password for {user.username} has been reset!', 'success')
        return redirect(url_for('admin.user_management'))
    return render_template('reset_password.html', title='Reset Password', form=form, user=user)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Allows admin to delete a user."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.user_management'))

    # Delete associated leave requests and audit logs first (or set up CASCADE in models)
    LeaveRequest.query.filter_by(user_id=user.id).delete()
    AuditLog.query.filter_by(user_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()

    audit_log = AuditLog(user_id=current_user.id,
                         action=f"Admin deleted user: {user.username} (ID: {user.id})",
                         ip_address=request.remote_addr)
    db.session.add(audit_log)
    db.session.commit()

    flash(f'User {user.username} and associated data have been deleted.', 'success')
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/audit_logs')
@login_required
@admin_required
def audit_logs():
    """Displays all audit logs for admin review."""
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('audit_logs.html', title='Audit Logs', logs=logs)
