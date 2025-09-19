@echo off
REM Kill any existing processes
taskkill /F /IM python.exe /FI "WINDOWTITLE eq status_check.py" 2>NUL
taskkill /F /IM python.exe /FI "WINDOWTITLE eq flask" 2>NUL

REM Create and activate virtual environment if it doesn't exist
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Set Flask environment
set FLASK_APP=status_app.py

REM Remove old database and create new one
del /F /Q status_app.db 2>NUL
python -c "from app import db; db.create_all()"

echo Setup complete! Now run Step2A.bat and Step2B.bat
pause