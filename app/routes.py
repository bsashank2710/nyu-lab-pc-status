from app import app, db, pc_names
from flask import render_template
from app.models import Status


@app.route('/')
@app.route('/index')
def index():
    status_dict = {}
    for name in pc_names.keys():
        try:
            stat = (
                Status.query
                .filter_by(domain_name=name)
                .order_by(Status.last_update.desc())
                .first())
            status_dict[name] = [
                stat.ip_address, stat.username, stat.session_name,
                stat.session_id, stat.state, stat.idle_time,
                stat.logon_time, stat.last_update]
        except AttributeError:
            pass
    return render_template('index.html', title='Home', status_dict=status_dict)
