from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
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
    except Exception as e:
        print(e)
        return False
    return login(username, password)

def logout():
    del session["user_id"]

def user_id():
    return session.get("user_id", 0)

def chat(receiver_id):
    sender_id = user_id()
    sql = text("SELECT * FROM CHATS WHERE sender_id = :sender_id AND receiver_id = :receiver_id OR receiver_id = :sender_id AND sender_id = :receiver_id;")
    return db.session.execute(sql, {"sender_id": sender_id, "receiver_id": receiver_id}).fetchall()

def send_chat(receiver_id, content):
    sender_id = user_id()
    sql = text("INSERT INTO chats (sender_id, receiver_id, content, sent_at) VALUES (:sender_id, :receiver_id, :content, NOW())")
    db.session.execute(sql, {"sender_id": sender_id, "receiver_id": receiver_id, "content": content})
    db.session.commit()
    return True


