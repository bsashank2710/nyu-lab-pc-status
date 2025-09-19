from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from app import app, db

# Import routes after models to avoid circular imports
from app import routes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
