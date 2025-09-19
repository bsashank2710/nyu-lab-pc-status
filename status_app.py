from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Dictionary mapping PC names to their IP addresses
pc_names = {
    'ENG-RH227-LAB03': '192.168.236.90',
    'ENG-RH227-LAB04': '192.168.236.91',
    'ENG-RH227-LAB05': '192.168.236.92',
    'ENG-RH227-LAB06': '192.168.236.93',
    'ENG-RH227-LAB07': '192.168.236.94',
    'ENG-RH227-LAB08': '192.168.236.98',
    'ENG-RH227-LAB09': '192.168.236.99',
    'ENG-RH227-LAB10': '192.168.236.100',
    'ENG-RH227-LAB11': '192.168.236.101',
    'ENG-RH227-LAB12': '192.168.236.103',
    'ENG-RH227-LAB13': '192.168.236.105',
    'ENG-RH227-LAB14': '192.168.236.106',
    'ENG-RH227-LAB15': '192.168.236.108',
    'ENG-RH227-LAB16': '192.168.236.109',
    'ENG-RH227-LAB17': '192.168.236.110',
    'ENG-RH227-LAB18': '192.168.236.111',
    'ENG-RH227-LAB19': '192.168.236.112',
    'ENG-RH227-LAB20': '192.168.236.113',
    'ENG-RH227-LAB21': '192.168.236.114',
    'ENG-RH227-LAB22': '192.168.236.115',
    'ENG-RH227-LAB23': '192.168.236.116',
    'ENG-RH227-LAB24': '192.168.236.118',
    'ENG-RH227-LAB25': '192.168.236.119',
    'ENG-RH227-LAB26': '192.168.236.124',
    'ENG-RH227-LAB27': '192.168.236.125'
}

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
