import subprocess
import re
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

def parse_qwinsta_output(output):
    """Parse qwinsta output to get session info."""
    lines = output.split('\n')
    if len(lines) < 2:  # No sessions or header only
        return None, None, None, None
    
    for line in lines[1:]:  # Skip header
        parts = line.split()
        if len(parts) >= 4 and 'Active' in line:
            # Try to extract username, session name, and ID
            username = parts[0]
            session_name = parts[1] if len(parts) > 1 else ''
            session_id = parts[2] if len(parts) > 2 else ''
            idle_time = parts[3] if len(parts) > 3 else ''
            return username, session_name, session_id, idle_time
    return None, None, None, None

def get_session_info(ip):
    """Get detailed session information."""
    try:
        # Try to query user sessions using qwinsta
        result = subprocess.run(
            ['qwinsta', '/server:' + ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2)
        output = result.stdout.decode()
        
        if result.returncode == 0:
            username, session_name, session_id, idle_time = parse_qwinsta_output(output)
            if username:
                return {
                    'username': username,
                    'session_name': session_name,
                    'session_id': session_id,
                    'idle_time': idle_time,
                    'logon_time': datetime.now().strftime('%I:%M:%S %p')  # Current time as logon time
                }
    except:
        pass

    try:
        # Try net session as fallback
        result = subprocess.run(
            ['net', 'session', '\\\\' + ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2)
        output = result.stdout.decode()
        
        if result.returncode == 0 and len(output.strip()) > 0:
            # Try to extract username from net session output
            match = re.search(r'Computer\s+(\S+)', output)
            if match:
                return {
                    'username': match.group(1),
                    'session_name': 'RDP',
                    'session_id': '1',
                    'idle_time': '0',
                    'logon_time': datetime.now().strftime('%I:%M:%S %p')
                }
    except:
        pass

    return {
        'username': '',
        'session_name': '',
        'session_id': '',
        'idle_time': '',
        'logon_time': ''
    }

def check_user_sessions(ip):
    """Check if there are any active user sessions."""
    session_info = get_session_info(ip)
    return bool(session_info['username'])

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
                    username='',
                    session_name='',
                    session_id='',
                    idle_time='',
                    logon_time='',
                    last_update=datetime.now())
            else:
                # Get session information
                session_info = get_session_info(ip)
                in_use = bool(session_info['username'])
                
                if in_use:
                    print(f"{name} is in use by {session_info['username']}")
                    stat = Status(
                        domain_name=name,
                        ip_address=ip,
                        state="In Use",
                        username=session_info['username'],
                        session_name=session_info['session_name'],
                        session_id=session_info['session_id'],
                        idle_time=session_info['idle_time'],
                        logon_time=session_info['logon_time'],
                        last_update=datetime.now())
                else:
                    print(f"{name} is available")
                    stat = Status(
                        domain_name=name,
                        ip_address=ip,
                        state="Available",
                        username='',
                        session_name='',
                        session_id='',
                        idle_time='',
                        logon_time='',
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
