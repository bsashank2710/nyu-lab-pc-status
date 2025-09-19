from app import db
from datetime import datetime, timedelta

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
    last_heartbeat = db.Column(db.DateTime)

    @staticmethod
    def get_in_use_count():
        """Get count of PCs currently in use based on heartbeat."""
        recent_cut = datetime.utcnow() - timedelta(seconds=90)  # Consider PCs inactive after 90s
        return Status.query.filter(
            Status.username != "",
            Status.last_heartbeat >= recent_cut
        ).count()

    @staticmethod
    def get_status_counts():
        """Get counts for each status."""
        recent_cut = datetime.utcnow() - timedelta(seconds=90)
        
        # First mark old heartbeats as Available
        old_sessions = Status.query.filter(
            Status.username != "",
            db.or_(
                Status.last_heartbeat < recent_cut,
                Status.last_heartbeat == None
            )
        )
        for status in old_sessions:
            status.state = "Available"
            status.username = ""
        db.session.commit()
        
        # Now get counts
        return {
            "available": Status.query.filter_by(state="Available").count(),
            "in_use": Status.query.filter(
                Status.username != "",
                Status.last_heartbeat >= recent_cut
            ).count(),
            "down": Status.query.filter_by(state="System Down").count()
        }

    def __repr__(self):
        return f'<Status {self.domain_name} - {self.state}>'
