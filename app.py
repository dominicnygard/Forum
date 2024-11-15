from os import getenv
from flask import Flask
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config['JWT_SECRET_KEY'] = getenv("JWT_SECRET_KEY")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
jwt = JWTManager(app)

socketio = SocketIO(app, logger=True, engineio_logger=True)

import routes

if __name__ == "__main__":
    socketio.run(app)
