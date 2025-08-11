import os
from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, LeaveRequest, AuditLog, UserRole, LeaveType, LeaveStatus
from datetime import date, datetime

app = create_app()
cli = FlaskGroup(app)

@cli.command("create-db")
def create_db():
    """Create database tables."""
    db.create_all()
    print("Database tables created!")

@cli.command("drop-db")
def drop_db():
    """Drop database tables."""
    db.drop_all()
    print("Database tables dropped!")

@cli.command("init-db")
def init_db():
    """Initialize database with sample data."""
    # Drop and create tables
    db.drop_all()
    db.create_all()
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@elms.com',
        first_name='System',
        last_name='Administrator',
        role=UserRole.ADMIN
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Commit all users
    db.session.commit()  
@cli.command("create-admin")
def create_admin():
    """Create an admin user."""
    username = input("Username: ")
    email = input("Email: ")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    password = input("Password: ")
    
    admin = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=UserRole.ADMIN
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    
    print(f"Admin user '{username}' created successfully!")

if __name__ == '__main__':
    cli()
