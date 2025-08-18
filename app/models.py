from datetime import datetime
from app import db

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    domain_name = db.Column(db.String, index=True)
    ip_address = db.Column(db.String)
    username = db.Column(db.String)
    session_name = db.Column(db.String)
    session_id = db.Column(db.Integer)
    state = db.Column(db.String)
    idle_time = db.Column(db.String)
    logon_time = db.Column(db.String)
    last_update = db.Column(db.DateTime, default=datetime.now, index=True)
