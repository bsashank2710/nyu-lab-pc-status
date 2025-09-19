PC Status Monitor - Setup Instructions
====================================

Follow these steps to set up and run the application:

1. Initial Setup (do this only once):
   - Open a terminal/command prompt in this folder
   - Create a virtual environment:
     * On Windows: python -m venv venv
     * On Linux/Mac: python3 -m venv venv
   
   - Activate the virtual environment:
     * On Windows: venv\Scripts\activate
     * On Linux: source venv/bin/activate
     * On macOS: source venv/bin/activate
   
   - Install dependencies:
     pip install -r requirements.txt

2. Running the Application:
   - Make sure you're in the virtual environment (see activation commands above)
   - On Windows:
     * Double-click Step1.bat
     * Double-click Step2A.bat
     * Double-click Step2B.bat
   
   - On Linux/macOS:
     * Make the start script executable: chmod +x start.sh
     * Run: ./start.sh

3. Accessing the Application:
   - Open a web browser
   - Go to: http://localhost:5000
   - You should see the PC status dashboard

4. Troubleshooting:
   - If port 5000 is in use:
     * On Windows: netstat -ano | findstr :5000
     * On Linux: sudo lsof -i :5000
     * On macOS: sudo lsof -i :5000
     Then kill the process using that port
   
   - If no data appears:
     * Make sure both the Flask server and status_check.py are running
     * Check if status_app.db exists (it's created automatically)
     * Wait 30 seconds for the first status check to complete
   
   - On macOS, if you get permission errors:
     * Run: chmod +x start.sh
     * If asked for network access, click "Allow"
     * If asked for Python network access, also click "Allow"

5. Important Notes:
   - The application creates a local database (status_app.db)
   - Each installation has its own database
   - Status updates happen every 30 seconds
   - Both the web server and status check script must be running
   - On macOS, you might need to allow Python through the firewall

For any issues, please check the terminal output for error messages. 