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
            timeout=3)  # Increased timeout
        return result.returncode == 0
    except Exception as e:
        print(f"Ping error: {e}")
        return False

def check_rdp_connection(ip):
    """Check if RDP port is in use.
    Returns (is_in_use, client_info):
        - is_in_use: True if someone is using the PC (can't connect to RDP)
        - client_info: Additional information about the connection
    """
    try:
        # Try to connect to RDP port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # Increased timeout
        result = sock.connect_ex((ip, 3389))
        sock.close()
        
        # If we can't connect to the port, it's likely in use
        if result != 0:
            return True, "RDP session active"
            
        # If we can connect, check netstat to confirm no active connections
        try:
            system = platform.system().lower()
            if system == "windows":
                netstat_cmd = ['netstat', '-n']
            elif system == "darwin":  # macOS
                netstat_cmd = ['netstat', '-n', '-p', 'tcp']
            else:  # Linux
                netstat_cmd = ['netstat', '-tn']
            
            netstat_result = subprocess.run(
                netstat_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=3)
            netstat_output = netstat_result.stdout.decode()
            
            # Look for established RDP connections
            for line in netstat_output.split('\n'):
                if ip in line and ':3389' in line and ('ESTABLISHED' in line or 'EST' in line):
                    return True, "Active RDP connection"
            
            # If we can connect and no established connections found,
            # the system is available
            return False, None
            
        except Exception as e:
            print(f"Netstat error: {e}")
            # If netstat check fails but we could connect to RDP port,
            # assume system is available
            return False, None
            
    except Exception as e:
        print(f"Socket error: {e}")
        # If we can't even create/use the socket, something is wrong
        # Assume system is down rather than in use
        return False, None
    
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
                in_use, client_info = check_rdp_connection(ip)
                
                if in_use:
                    print(f"{name} is in use")
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
