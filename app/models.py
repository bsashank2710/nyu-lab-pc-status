from app import db
from datetime import datetime

class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    domain_name = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(32), default="Available")  # Available, In Use, System Down
    username = db.Column(db.String(255), default="")
    session_name = db.Column(db.String(255), default="")
    session_id = db.Column(db.String(64), default="")
    idle_time = db.Column(db.String(64), default="")
    logon_time = db.Column(db.String(64), default="")
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Status {self.domain_name} - {self.state}>'
