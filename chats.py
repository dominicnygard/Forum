from sqlalchemy.sql import text
import uuid
from db import db
from users import user_id

def chat(room_id):
    sql = text("SELECT * FROM messages WHERE chat_id= :room_id")
    return db.session.execute(sql, {"room_id": room_id}).fetchall()

def send_chat(room_id, receiver_id, content):
    sender_id = user_id()
    sql = text("INSERT INTO messages (chat_id, sender_id, receiver_id, content, sent_at) VALUES (:chat_id, :sender_id, :receiver_id, :content, NOW())")
    db.session.execute(sql, {"chat_id":room_id, "sender_id": sender_id, "receiver_id": receiver_id, "content": content})
    db.session.commit()
    return True

def get_user_permissions(username):
    user_permissions = {}

    sql = text("SELECT UP.room_id, P.permission_name \
    FROM UserPermissions UP, Permisions P, Users U \
    WHERE UP.permission_id = P.id AND U.username = :username AND U.id = UP.user_id \
    ")

    permissions = db.session.execute(sql, {"username": username}).fetchall()

    for perm in permissions:
        if perm[0] not in user_permissions:
            user_permissions[perm[0]] = []
        user_permissions[perm[0]].append(perm[1])
    
    return user_permissions

def get_user_rooms(id):
    sql = text("SELECT room_id \
        FROM UserPermissions \
        WHERE user_id IN (:user1_id, :user2_id) \
        GROUP BY room_id \
        HAVING COUNT(DISTINCT user_id) = 2 \
        ")
    return db.session.execute(sql, {"user1_id": id, "user2_id": user_id()}).fetchone()

def create_room(id):
    room_id = str(uuid.uuid4())
    sql = text("INSERT INTO chats (room_id) VALUES (:room_id)")
    db.session.execute(sql, {"room_id": room_id})
    db.session.commit()
    id_room = db.session.execute(text("SELECT id FROM Chats WHERE room_id=:room_id"), {"room_id": room_id}).fetchone()
    sql = text("INSERT INTO UserPermissions (room_id, user_id, permission_id) \
               VALUES \
               (:room_id, :user1_id, 1), \
               (:room_id, :user1_id, 2), \
               (:room_id, :user2_id, 1), \
               (:room_id, :user2_id, 2) \
               ")
    db.session.execute(sql, {"room_id": id_room[0], "user1_id": user_id(), "user2_id": id})
    db.session.commit()

def get_room_id(id):
    sql = text("SELECT room_id FROM chats WHERE id = :id")
    return db.session.execute(sql, {"id": id}).fetchone()