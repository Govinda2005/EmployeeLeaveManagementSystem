# ELMS/run.py
from my_flask_app.app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        print("Database tables created or already exist.")

    app.run(debug=True)
