from os import getenv
from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager



app = Flask(__name__)


app.secret_key = getenv("SECRET_KEY")
app.config['JWT_SECRET_KEY'] = getenv("JWT_SECRET_KEY")

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_SAMESITE'] = 'strict'

app.config["JWT_ACCESS_COOKIE_PATH"] = "/"

if not app.debug:
    handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

jwt = JWTManager(app)

socketio = SocketIO(app, logger=True, engineio_logger=True)


import routes