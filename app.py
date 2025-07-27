# app.py
# This is a basic Flask application setup with SQLAlchemy, Flask-Bcrypt, and Flask-
import os
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

# --- Initialize Flask app ---
app = Flask(__name__)

# --- Configure SECRET_KEY ---
# It's crucial for session management, CSRF protection, etc.
# Use os.environ.get for production, default for development.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your_super_secret_key_that_you_should_change'

# --- Database Configuration ---
# Set SQLALCHEMY_DATABASE_URI to sqlite:///site.db for simplicity during development.
# The 'site.db' file will be created in the root directory of your project.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Suppresses a warning

# --- Initialize SQLAlchemy and Flask-Login ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Route name for the login page
login_manager.login_message_category = 'info' # Bootstrap class for flash messages

# --- Define login_manager.user_loader ---
# This is required by Flask-Login. It loads a user from the database
# given their ID.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Database Model (for a simple User) ---
# This defines your User table structure. For simplicity, we put it here.
# For larger apps, this would go in a separate `models.py` file.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False) # Hashed password

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# --- Include a basic "Hello World" route (/) ---
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home') # We'll create home.html soon

@app.route("/about")
def about():
    return render_template('about.html', title='About') # We'll create about.html soon

# Example for a simple registration route (just for testing the model/DB)
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register') # Create this template later

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True) # remember=True for persistent session
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login') # Create this template later

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# --- Add db.create_all() within app.app_context() ---
# This block ensures that the Flask application context is active when
# db.create_all() is called, which is necessary for SQLAlchemy to
# connect to the database and create tables.
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates tables based on your models
    app.run(debug=True) # Run the Flask development server