# ELMS/app.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions outside of create_app for global access
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # --- Configure SECRET_KEY ---
    # It's crucial for session management, CSRF protection, etc.
    # Use os.environ.get for production, default for development.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'a_default_secret_key_if_env_not_set'

    # --- Database Configuration ---
    # Set SQLALCHEMY_DATABASE_URI to sqlite:///site.db for simplicity during development.
    # The 'site.db' file will be created in the root directory of your project.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Suppresses a warning

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login' # Route name for the login page
    login_manager.login_message_category = 'info' # Bootstrap class for flash messages

    # Import models and forms inside create_app to avoid circular imports
    # This is a common Flask pattern when using blueprints or larger apps
    from .models import User, LeaveRequest, AuditLog, Role # Import all models
    from .forms import RegistrationForm, LoginForm, LeaveApplicationForm, UserUpdateForm, PasswordResetForm # Import all forms

    # Define login_manager.user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register blueprints (we'll create these later)
    from .routes import main_bp, auth_bp, employee_bp, manager_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(admin_bp)

    return app

# This block is typically in a run.py file, but for initial setup, it's here.
# We will move it to run.py later.
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all() # Creates tables based on your models
    app.run(debug=True) # Run the Flask development server
