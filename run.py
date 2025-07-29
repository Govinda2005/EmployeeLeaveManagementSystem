# ELMS/run.py
from my_flask_app.app import create_app, db
from my_flask_app.models import Role # Import the Role model

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        print("Database tables created or already exist.")

        # --- Initialize default roles if they don't exist ---
        roles_to_add = ['Admin', 'Manager', 'Employee']
        for role_name in roles_to_add:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                new_role = Role(name=role_name)
                db.session.add(new_role)
                print(f"Added role: {role_name}")
            else:
                print(f"Role '{role_name}' already exists.")
        db.session.commit()
        print("Role initialization complete.")
        # --- End Role Initialization ---

    app.run(debug=True)
