#!/bin/bash

# Kill any existing processes
pkill -f "status_check.py"
pkill -f "flask run"

# Activate virtual environment
source venv/bin/activate

# Set Flask environment
export FLASK_APP=status_app.py

# Remove old database and create new one
rm -f status_app.db
python3 -c "from app import db; db.create_all()"

# Start status check script in background
python3 status_check.py &

# Start Flask server
flask run --host=0.0.0.0 --port=5000 