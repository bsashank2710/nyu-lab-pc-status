from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from app import app, db

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

# Import routes after models to avoid circular imports
from app import routes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
