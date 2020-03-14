from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)


pc_names = {
    'CUE0301WK-WX': '192.168.237.34',
    'CUE0302WK-WX': '192.168.237.35',
    'CUE0303WK-WX': '192.168.237.36',
    'CUE0304WK-WX': '192.168.237.37',
    'CUE0305WK-WX': '192.168.237.38',
    'CUE0306WK-WX': '192.168.237.39',
    'CUE0307WK-WX': '192.168.237.40',
    'CUE0308WK-WX': '192.168.237.41',
    'CUE0309WK-WX': '192.168.237.43',
    'CUE0310WK-WX': '192.168.237.44',
    'CUE0311WK-WX': '192.168.237.45',
    'CUE0312WK-WX': '192.168.237.46',
    'CUE0313WK-WX': '192.168.237.47',
    'CUE0314WK-WX': '192.168.237.48',
    'CUE0315WK-WX': '192.168.237.49',
    'CUE0316WK-WX': '192.168.237.50',
    'CUE0317WK-WX': '192.168.237.51',
    'CUE0318WK-WX': '192.168.237.52',
    'CUE0319WK-WX': '192.168.237.53',
    'CUE0320WK-WX': '192.168.237.54',
    'CUE0321WK-WX': '192.168.237.55',
    'CUE0322WK-WX': '192.168.237.56',
    'CUE0323WK-WX': '192.168.236.136',
    'CUE0324WK-WX': '192.168.237.58',
    'CUE0325WK-WX': '192.168.237.59',
    'CUE0326WK-WX': '192.168.237.60',
    'CUE0327WK-WX': '192.168.237.61',
    'CUE0328WK-WX': '192.168.237.62',
    'CUE0329WK-WX': '192.168.237.63',
    'CUE0330WK-WX': '192.168.237.64',
    'CUE0331WK-WX': '192.168.237.65',
    'CUE0332WK-WX': '192.168.237.66',
}

from app import routes, models
