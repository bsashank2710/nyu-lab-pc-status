from app import app, db, pc_names
from flask import render_template, Response
from app.models import Status


@app.route('/')
@app.route('/index')
def index():
    status_dict = {}
    w_count = 0
    d_count = 0
    for name in pc_names.keys():
        try:
            stat = (
                Status.query
                .filter_by(domain_name=name)
                .order_by(Status.last_update.desc())
                .first())
            if stat:
                status_dict[name] = [
                    stat.ip_address, stat.username, stat.session_name,
                    stat.session_id, stat.state, stat.idle_time,
                    stat.logon_time, stat.last_update]
                if stat.state == 'Available':
                    w_count += 1
                elif stat.state == 'System Down':
                    d_count += 1
        except Exception as e:
            print(f"Error getting status for {name}: {e}")
            continue
    
    return render_template('index.html', 
                         title='Home', 
                         status_dict=status_dict,
                         w_count=w_count,
                         d_count=d_count)


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

@app.route("/get-rdp-file/<domain_name>")
def get_rdp_file(domain_name):
    contents = rdp_file_contents.format(pc_names[domain_name])

    return Response(
        contents, mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment;filename={domain_name}.rdp"})
