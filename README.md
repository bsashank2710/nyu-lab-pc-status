# PC Status Monitor

This application monitors the status of lab PCs, showing whether they are Available, In Use, or Down.

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd cue-pc-status
```

2. Create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. First, make sure you're in the project directory and your virtual environment is activated:
```bash
cd cue-pc-status
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Set the Flask application:
```bash
export FLASK_APP=status_app.py  # On Windows: set FLASK_APP=status_app.py
```

3. Initialize the database:
```bash
# Remove old database if it exists
rm -f status_app.db  # On Windows: del status_app.db
# Create new database
python3 -c "from app import db; db.create_all()"
```

4. Start the status check script (in a separate terminal or in background):
```bash
python3 status_check.py &  # On Windows: start python status_check.py
```

5. Start the Flask server:
```bash
flask run --host=0.0.0.0 --port=5000
```

The application will be accessible at `http://localhost:5000`

## Troubleshooting

1. If port 5000 is in use, try a different port:
```bash
flask run --host=0.0.0.0 --port=5002
```

2. If the application isn't showing any data:
- Make sure both the status check script and Flask server are running
- Check if the database file (status_app.db) exists and has permissions
- Look for any error messages in the terminal running the status check script

3. To stop all running processes:
```bash
pkill -f "status_check.py"
pkill -f "flask run"
```

## Features

- Real-time PC status monitoring
- Color-coded status indicators:
  - Green: Available
  - Amber: In Use
  - Red: System Down
- RDP file download for quick connection
- Auto-refresh status updates

## Important Notes

- The application needs to run with sufficient permissions to ping PCs and check RDP ports
- Both the status check script and Flask server must be running for the application to work
- The database is recreated each time the application starts to ensure fresh status data
