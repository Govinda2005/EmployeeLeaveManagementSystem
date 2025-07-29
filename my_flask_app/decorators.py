# ELMS/my_flask_app/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user
from my_flask_app.models import Role # Import Role model

def role_required(role_names):
    """
    Custom decorator to restrict access to routes based on user roles.
    Takes a list of role names (e.g., ['Admin', 'Manager']).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403) # Forbidden if not logged in
            
            # Fetch the role object from the database using the role_id
            user_role = Role.query.get(current_user.role_id)

            if user_role and user_role.name in role_names:
                return f(*args, **kwargs)
            else:
                abort(403) # Forbidden if role doesn't match
        return decorated_function
    return decorator

# Specific role decorators for convenience
admin_required = role_required(['Admin'])
manager_required = role_required(['Manager', 'Admin']) # Managers can access manager routes, admins can too
employee_required = role_required(['Employee', 'Manager', 'Admin']) # All authenticated users can access employee routes
