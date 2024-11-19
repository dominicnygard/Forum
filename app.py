from os import getenv
from flask import Flask
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from datetime import timedelta

app = Flask(__name__)

app.secret_key = getenv("SECRET_KEY")
app.config['JWT_SECRET_KEY'] = getenv("JWT_SECRET_KEY")

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_SAMESITE'] = "strict"

app.config["JWT_ACCESS_COOKIE_PATH"] = "/"

jwt = JWTManager(app)

socketio = SocketIO(app, logger=True, engineio_logger=True)


import routes

#if __name__ == "__main__":
    #socketio.run(app)
