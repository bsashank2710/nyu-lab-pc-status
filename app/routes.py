from flask import render_template, jsonify, request, Response
from app import app, db, pc_names
from app.models import Status
from datetime import datetime, timedelta
from sqlalchemy import desc

@app.route('/')
@app.route('/index')
def index():
    """Main page showing PC status."""
    counts = Status.get_status_counts()
    status_dict = {}
    
    for name in pc_names.keys():
        try:
            stat = (
                Status.query
                .filter_by(domain_name=name)
                .order_by(Status.last_update.desc())
                .first()
            )
            if stat:
                status_dict[name] = [
                    stat.ip_address,
                    stat.username,
                    stat.session_name,
                    stat.session_id,
                    stat.state,
                    stat.idle_time,
                    stat.logon_time,
                    stat.last_update
                ]
        except Exception as e:
            print(f"Error getting status for {name}: {e}")
            continue

    return render_template('index.html',
                         title='Home',
                         status_dict=status_dict,
                         w_count=counts['available'],
                         in_use_count=counts['in_use'],
                         d_count=counts['down'],
                         last_update=datetime.now().strftime('%I:%M:%S %p'))

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """Endpoint for PCs to send their heartbeat."""
    data = request.get_json()
    
    if not data or 'hostname' not in data:
        return jsonify({'error': 'Missing hostname'}), 400
        
    hostname = data['hostname']
    username = data.get('user', '')
    
    # Update or create status record
    status = Status.query.filter_by(domain_name=hostname).first()
    if not status:
        status = Status(domain_name=hostname)
        
    status.username = username
    status.last_heartbeat = datetime.utcnow()
    status.state = "In Use" if username else "Available"
    
    if 'ip' in data:
        status.ip_address = data['ip']
    
    try:
        db.session.add(status)
        db.session.commit()
        return jsonify({'status': 'ok'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/debug/inuse')
def debug_inuse():
    """Debug endpoint to show which PCs are counted as in use."""
    recent_cut = datetime.utcnow() - timedelta(seconds=90)
    machines = Status.query.filter(
        Status.username != "",
        Status.last_heartbeat >= recent_cut
    ).all()
    return jsonify({
        'in_use': [
            {
                'hostname': m.domain_name,
                'user': m.username,
                'last_heartbeat': m.last_heartbeat.isoformat() if m.last_heartbeat else None
            }
            for m in machines
        ],
        'total_count': len(machines)
    })

@app.route('/get_last_update')
def get_last_update():
    """Get latest status updates for all PCs."""
    status_dict = {}
    last_update = None
    try:
        for name in pc_names.keys():
            stat = (
                Status.query
                .filter_by(domain_name=name)
                .order_by(Status.last_update.desc())
                .first())
            if stat:
                status_dict[name] = {
                    'state': stat.state,
                    'last_update': stat.last_update.strftime('%I:%M:%S %p') if stat.last_update else 'Never'
                }
                if not last_update or (stat.last_update and stat.last_update > last_update):
                    last_update = stat.last_update
    except Exception as e:
        print(f"Error getting status updates: {e}")
    
    return jsonify({
        'last_update': last_update.strftime('%I:%M:%S %p') if last_update else 'Never',
        'pc_status': status_dict
    })

@app.route("/get-rdp-file/<domain_name>")
def get_rdp_file(domain_name):
    """Generate RDP file for a PC."""
    if domain_name not in pc_names:
        return "Invalid PC name", 400
        
    contents = rdp_file_contents.format(pc_names[domain_name])
    return Response(
        contents, mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment;filename={domain_name}.rdp"})

# RDP file template
rdp_file_contents = """gatewaybrokeringtype:i:0
use redirection server name:i:0
disable themes:i:0
disable cursor setting:i:0
disable menu anims:i:1
remoteapplicationcmdline:s:
redirected video capture encoding quality:i:0
audiocapturemode:i:0
prompt for credentials on client:i:1
remoteapplicationprogram:s:
gatewayusagemethod:i:2
screen mode id:i:2
use multimon:i:0
authentication level:i:2
desktopwidth:i:0
desktopheight:i:0
redirectclipboard:i:1
loadbalanceinfo:s:
enablecredsspsupport:i:1
promptcredentialonce:i:0
redirectprinters:i:0
autoreconnection enabled:i:1
administrative session:i:0
redirectsmartcards:i:0
authoring tool:s:
alternate shell:s:
remoteapplicationmode:i:0
disable full window drag:i:1
gatewayusername:s:
shell working directory:s:
audiomode:i:0
remoteapplicationappid:s:
username:s:
allow font smoothing:i:1
connect to console:i:0
gatewayhostname:s:
camerastoredirect:s:
drivestoredirect:s:
session bpp:i:32
disable wallpaper:i:0
full address:s:{}
gatewayaccesstoken:s:
"""
