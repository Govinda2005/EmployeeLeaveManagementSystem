# ELMS/my_flask_app/main/routes.py
from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    """Renders the home page."""
    return render_template('home.html', title='Home')

@main_bp.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html', title='About')

@main_bp.route('/dashboard')
@login_required # Only authenticated users can access their dashboard
def dashboard():
    """
    Renders a generic dashboard. This will be refined based on user roles.
    For now, it's a placeholder.
    """
    return render_template('dashboard.html', title='Dashboard') # We'll create dashboard.html later
