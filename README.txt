QUICK START GUIDE FOR PC STATUS MONITOR
=====================================

WINDOWS USERS:
-------------
1. Install Python 3.x from python.org if not already installed

2. Open Command Prompt and run these commands:
   cd path\to\downloaded\folder
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   set FLASK_APP=status_app.py
   python -c "from app import db; db.create_all()"

3. Open TWO Command Prompt windows:
   In first window:
   - venv\Scripts\activate
   - python status_check.py

   In second window:
   - venv\Scripts\activate
   - python -m flask run --host=0.0.0.0 --port=5000

4. Open web browser and go to: http://localhost:5000


LINUX/MAC USERS:
---------------
1. Open terminal and run:
   chmod +x start.sh
   ./start.sh

   OR follow these steps:

2. Manual setup:
   cd path/to/downloaded/folder
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   export FLASK_APP=status_app.py
   python3 -c "from app import db; db.create_all()"

3. Open TWO terminal windows:
   In first terminal:
   - source venv/bin/activate
   - python3 status_check.py

   In second terminal:
   - source venv/bin/activate
   - python3 -m flask run --host=0.0.0.0 --port=5000

4. Open web browser and go to: http://localhost:5000


TROUBLESHOOTING:
---------------
1. If port 5000 is in use:
   - Try port 5002 instead (change 5000 to 5002 in the flask run command)

2. If no data shows up:
   - Make sure both status_check.py and flask are running
   - Check if status_app.db exists in the folder
   - Look for error messages in the terminals

3. To stop everything:
   Windows: Close both Command Prompt windows
   Linux/Mac: Press Ctrl+C in both terminals

4. To start fresh:
   - Delete status_app.db
   - Kill any running python processes
   - Start again from step 2 