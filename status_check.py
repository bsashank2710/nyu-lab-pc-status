import subprocess
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

def check_rdp_session(ip):
    """Check if there's an active RDP session on the host."""
    try:
        # Try to establish a connection to RDP port (3389)
        result = subprocess.run(
            ['nc', '-z', '-w', '1', ip, '3389'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

def status_check():
    print(f"\nStarting status check at {datetime.now()}")
    with app.app_context():
        # First, delete all old records
        db.session.query(Status).delete()
        db.session.commit()
        
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
            else:
                # Check if RDP is accessible
                rdp_available = check_rdp_session(ip)
                if rdp_available:
                    print(f"{name} is available")
                    state = "Available"
                else:
                    print(f"{name} is in use")
                    state = "In Use"

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
