import subprocess
from app import db, pc_names, app
from app.models import Status
import time
import platform
from datetime import datetime
import socket
import struct

def check_rdp_session(host):
    """Check if there are active RDP sessions on the host."""
    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # 1 second timeout
        
        # Try to connect to RDP port (3389)
        result = sock.connect_ex((host, 3389))
        sock.close()
        
        if result == 0:
            # Port is open, try to establish a connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((host, 3389))
            
            # Send RDP negotiation request
            # MS-RDPBCGR protocol - RDP Negotiation Request
            packet = struct.pack('>BBHBH', 3, 0, 19, 0, 3389)
            sock.send(packet)
            
            # Receive response
            response = sock.recv(1024)
            sock.close()
            
            # If we get a response and it's longer than 0 bytes
            # it likely means someone is using the system
            return len(response) > 0
    except:
        pass
    return False

def ping_host(host):
    """Ping a host and return True if it responds, False otherwise."""
    # Use -c for Linux/Mac, -n for Windows
    try:
        # Use shell=True for Windows-style hostnames
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2)
        return result.returncode == 0
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

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

            if not (host_up or ip_up):
                print(f"{name} is down")
                stat = Status(
                    domain_name=name,
                    ip_address=ip,
                    state="System Down",
                    last_update=datetime.now())
            else:
                # Check for RDP sessions
                in_use = check_rdp_session(ip)
                state = "In Use" if in_use else "Available"
                print(f"{name} is {state.lower()}")
                stat = Status(
                    domain_name=name,
                    ip_address=ip,
                    state=state,
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
