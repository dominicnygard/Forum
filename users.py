from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
import secrets
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
    hash_token = generate_password_hash(secrets.token_urlsafe())
    try:
        sql = text("INSERT INTO users (username, password, token) VALUES (:username, :password, :token)")
        db.session.execute(sql, {"username": username, "password": hash_value, "token": hash_token})
        db.session.commit()
    except Exception as e:
        print(e)
        return False
    return login(username, password)

def logout():
    del session["user_id"]

def user_id():
    return session.get("user_id", 0)

def get_other_user(id):
    user_id = session.get("user_id", 0)
    sql = text("SELECT user_id FROM UserPermissions WHERE room_id = :room_id AND user_id != :user_id")
    return db.session.execute(sql, {"room_id": id, "user_id": user_id}).fetchone()