import subprocess
import socket
import platform
from app import db, pc_names, app
from app.models import Status
import time
from datetime import datetime

def ping_host(host):
    """Ping a host and return True if it responds, False otherwise."""
    try:
        system = platform.system().lower()
        if system == "windows":
            ping_cmd = ['ping', '-n', '1', '-w', '2000', host]
        elif system == "darwin":  # macOS
            ping_cmd = ['ping', '-c', '1', '-t', '2', host]
        else:  # Linux
            ping_cmd = ['ping', '-c', '1', '-W', '2', host]
        
        result = subprocess.run(
            ping_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=3)
        return result.returncode == 0
    except Exception as e:
        print(f"Ping error: {e}")
        return False

def check_pc_in_use(name, ip):
    """Check if a PC is in use by trying multiple connection attempts.
    Returns (is_in_use, client_info)
    """
    # Try multiple connection attempts to be sure
    for attempt in range(3):
        try:
            # Create a new socket for each attempt
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)  # Very short timeout for quick checks
            
            try:
                # Try to connect to RDP port
                result = sock.connect_ex((ip, 3389))
                sock.close()
                
                if result != 0:
                    print(f"Attempt {attempt + 1}: Could not connect to RDP port on {ip} (result={result})")
                    # If we can't connect, the PC is likely in use
                    # No need to try more attempts
                    return True, "RDP session active"
                else:
                    print(f"Attempt {attempt + 1}: Successfully connected to RDP port on {ip}")
                    # Even if we can connect, try additional attempts to be sure
                    time.sleep(0.1)  # Short delay between attempts
                    
            except socket.error as e:
                sock.close()
                print(f"Attempt {attempt + 1}: Socket error on {ip}: {e}")
                # Socket error usually means the port is in use
                return True, "RDP port in use"
                
        except Exception as e:
            print(f"Attempt {attempt + 1}: General error checking {ip}: {e}")
            continue
    
    # If we get here, we were able to connect multiple times
    # This means the PC is likely available
    return False, None

def status_check():
    print(f"\nStarting status check at {datetime.now()}")
    
    with app.app_context():
        # First, clean up old records
        try:
            db.session.query(Status).delete()
            db.session.commit()
        except Exception as e:
            print(f"Error cleaning old records: {e}")
            db.session.rollback()

        for name in pc_names.keys():
            print(f"\nChecking {name}...")
            ip = pc_names[name]
            print(f"Pinging {name} ({ip})...")
            
            # Try to ping both hostname and IP
            host_up = ping_host(name)
            ip_up = ping_host(ip)
            print(f"Host ping: {'Success' if host_up else 'Failed'}")
            print(f"IP ping: {'Success' if ip_up else 'Failed'}")

            if not (host_up or ip_up):
                print(f"{name} is down")
                state = "System Down"
                extra_info = "Not responding to ping"
            else:
                # Check if the system is in use
                in_use, client_info = check_pc_in_use(name, ip)
                
                if in_use:
                    print(f"{name} is in use ({client_info})")
                    state = "In Use"
                    extra_info = client_info
                else:
                    print(f"{name} is available")
                    state = "Available"
                    extra_info = ""

            # Create status record
            stat = Status(
                domain_name=name,
                ip_address=ip,
                state=state,
                username='Remote User' if state == "In Use" else '',
                session_name=extra_info if state == "In Use" else '',
                session_id='1' if state == "In Use" else '',
                idle_time='0' if state == "In Use" else '',
                logon_time=datetime.now().strftime('%I:%M:%S %p') if state == "In Use" else '',
                last_update=datetime.now())

            try:
                db.session.add(stat)
                db.session.commit()
                print(f"Updated status for {name} in database")
            except Exception as e:
                print(f"Error updating database for {name}: {e}")
                db.session.rollback()

if __name__ == '__main__':
    i = 1
    while True:
        print(f'\n--> Check No. {i}')
        try:
            status_check()
        except Exception as e:
            print(f"Error during status check: {e}")
        print(f"\nCompleted check {i}. Waiting 30 seconds...")
        i += 1
        time.sleep(30)
