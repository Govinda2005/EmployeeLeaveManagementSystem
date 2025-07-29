# ELMS/my_flask_app/models.py
from datetime import datetime
from my_flask_app.app import db, login_manager
from flask_login import UserMixin

# UserMixin provides default implementations for methods required by Flask-Login
# (is_authenticated, is_active, is_anonymous, get_id())

@login_manager.user_loader
def load_user(user_id):
    """
    Callback function to reload the user object from the user ID stored in the session.
    Required by Flask-Login.
    """
    return User.query.get(int(user_id))

class Role(db.Model):
    """
    Represents user roles in the system (Admin, Manager, Employee).
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='user_role', lazy=True) # Relationship to User model

    def __repr__(self):
        return f"Role('{self.name}')"

class User(db.Model, UserMixin):
    """
    Represents a user in the system (Employee, Manager, Admin).
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False) # Hashed password
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False, default=3) # Default to Employee (assuming ID 3)
    is_active = db.Column(db.Boolean, default=True) # For deactivating users
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    leave_requests = db.relationship('LeaveRequest', backref='applicant', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='actor', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', Role ID: {self.role_id})"

class LeaveRequest(db.Model):
    """
    Represents a leave application submitted by an employee.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending') # Pending, Approved, Rejected, Cancelled
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    manager_notes = db.Column(db.Text, nullable=True) # Notes from manager on approval/rejection

    def __repr__(self):
        return f"LeaveRequest('{self.applicant.username}', '{self.start_date}' to '{self.end_date}', Status: '{self.status}')"

class AuditLog(db.Model):
    """
    Tracks significant actions within the system for auditing purposes.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # User who performed the action
    action = db.Column(db.String(255), nullable=False) # Description of the action
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True) # Optional: IP address of the actor

    def __repr__(self):
        return f"AuditLog('{self.actor.username}', '{self.action}', '{self.timestamp}')"
