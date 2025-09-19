from status_app import app, db
import os

# Remove existing database
db_path = os.path.join(os.path.dirname(__file__), 'status_app.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print("Removed existing database.")

# Create new database with updated schema
with app.app_context():
    db.create_all()
    print("Database tables created successfully.") 