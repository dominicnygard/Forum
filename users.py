from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from db import db

def login(username, password):
    sql =  text("SELECT id, password FROM users WHERE username = :username")
    user = db.session.execute(sql, {"username": username}).fetchone()
    if not user:
        return False
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["user_id"] = user.id
            return True
        else:
            return False
        
def register(username, password):
    hash_value = generate_password_hash(password)
    try:
        sql = text("INSERT INTO users (username, password) VALUES (:username, :password)")
        db.session.execute(sql, {"username": username, "password": hash_value})
        db.session.commit()
        sql = text('SELECT id FROM users WHERE username = :username')
        user_id = db.session.execute(sql, {"username": username}).fetchone()
        sql = text("INSERT INTO PublicPermissions (user_id, permission_id) VALUES (:user_id, 4), (:user_id, 5)")
        db.session.execute(sql, {"user_id": user_id[0]})
        db.session.commit()
    except Exception as e:
        print(e)
        return False
    return login(username, password)

def logout():
    del session["user_id"]

def user_id():
    return session.get("user_id", 0)

