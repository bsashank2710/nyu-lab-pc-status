import subprocess
import socket
from app import db, pc_names, app
from app.models import Status
import time
from datetime import datetime

def ping_host(host):
    """Ping a host and return True if it responds, False otherwise."""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2)
        return result.returncode == 0
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

def check_rdp_port(ip):
    """Check if RDP port is in use (indicating an active session)"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        # Try to connect to RDP port
        result = sock.connect_ex((ip, 3389))
        sock.close()
        # If port is open but connection refused, someone is using it
        return result != 0
    except:
        sock.close()
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
                # Check if the system is in use
                in_use = check_rdp_port(ip)
                if in_use:
                    print(f"{name} is in use")
                    stat = Status(
                        domain_name=name,
                        ip_address=ip,
                        state="In Use",
                        last_update=datetime.now())
                else:
                    print(f"{name} is available")
                    stat = Status(
                        domain_name=name,
                        ip_address=ip,
                        state="Available",
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
