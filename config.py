import os

# Get the directory containing this file
basedir = os.path.abspath(os.path.dirname(__file__))

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'status_app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask configuration
DEBUG = True
SECRET_KEY = 'dev'  # Change this to a random string in production!
