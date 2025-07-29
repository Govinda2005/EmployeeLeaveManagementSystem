# ELMS/add_roles.py
from my_flask_app.app import create_app, db
from my_flask_app.models import Role

app = create_app()

with app.app_context():
    # Create tables if they don't exist
    db.create_all()

    # Define roles
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

    # Optional: Verify roles
    print("\nCurrent Roles in DB:")
    for r in Role.query.all():
        print(f"ID: {r.id}, Name: {r.name}")
