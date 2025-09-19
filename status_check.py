import subprocess
import socket
import platform
from app import db, pc_names, app
from app.models import Status
import time
from datetime import datetime, timedelta

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
    # First check if we have a recent heartbeat
    recent_cut = datetime.utcnow() - timedelta(seconds=90)
    status = Status.query.filter_by(domain_name=name).first()
    if status and status.username and status.last_heartbeat and status.last_heartbeat >= recent_cut:
        print(f"{name} is in use (active heartbeat from {status.username})")
        return True, f"Active user: {status.username}", status.username, status.last_heartbeat
    
    # If no recent heartbeat, try RDP check
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, 3389))
        sock.close()
        
        if result != 0:
            print(f"RDP port closed on {ip} - likely in use")
            return True, "RDP port in use", None, None
        
        print(f"RDP port available on {ip}")
        return False, None, None, None
            
    except Exception as e:
        print(f"Error checking RDP: {e}")
        return False, None, None, None

def status_check():
    print(f"\nStarting status check at {datetime.now()}")
    
    with app.app_context():
        for name in pc_names.keys():
            print(f"\nChecking {name}...")
            ip = pc_names[name]
            print(f"Pinging {name} ({ip})...")
            
            # Try to ping both hostname and IP
            host_up = ping_host(name)
            ip_up = ping_host(ip)
            print(f"Host ping: {'Success' if host_up else 'Failed'}")
            print(f"IP ping: {'Success' if ip_up else 'Failed'}")

            # Get or create status record
            try:
                status = Status.query.filter_by(domain_name=name).first()
                if not status:
                    status = Status(domain_name=name)
                    db.session.add(status)
                
                # Update basic info
                status.ip_address = ip
                status.last_update = datetime.now()

                if not (host_up or ip_up):
                    print(f"{name} is down")
                    status.state = "System Down"
                    status.username = ""
                    status.session_name = "Not responding to ping"
                    status.last_heartbeat = None
                else:
                    # Check if the system is in use
                    in_use, client_info, username, last_heartbeat = check_pc_in_use(name, ip)
                    
                    if in_use:
                        print(f"{name} is in use ({client_info})")
                        status.state = "In Use"
                        status.session_name = client_info
                        
                        # Only update user info if we have new info
                        if username is not None:
                            status.username = username
                        if last_heartbeat is not None:
                            status.last_heartbeat = last_heartbeat
                            
                        # Set other fields for in-use state
                        status.session_id = '1'
                        status.idle_time = '0'
                        status.logon_time = datetime.now().strftime('%I:%M:%S %p')
                    else:
                        print(f"{name} is available")
                        status.state = "Available"
                        status.username = ""
                        status.session_name = ""
                        status.session_id = ""
                        status.idle_time = ""
                        status.logon_time = ""
                        status.last_heartbeat = None

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
