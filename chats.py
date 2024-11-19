from sqlalchemy.sql import text
import uuid
from db import db
from users import user_id
from rooms import user_rooms

def chat(room_id):
    sql = text("SELECT * FROM messages WHERE chat_id= :room_id")
    return db.session.execute(sql, {"room_id": room_id}).fetchall()

def send_chat(room_id, content):
    sender_id = user_id()
    sql = text("INSERT INTO messages (chat_id, sender_id, content, sent_at) VALUES (:chat_id, :sender_id, :content, NOW()) RETURNING sent_at")
    result = db.session.execute(sql, {"chat_id":room_id, "sender_id": sender_id, "content": content})
    db.session.commit()
    sent_at = result.fetchone()[0]
    return sent_at

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

    return id_room[0]

def get_room_id(id):
    sql = text("SELECT room_id FROM chats WHERE id = :id")
    return db.session.execute(sql, {"id": id}).fetchone()


"""SELECT cp2.room_id, u.id, u.username, m.sent_at as last_active
FROM UserPermissions cp1 
JOIN UserPermissions cp2 ON cp1.room_id = cp2.room_id 
JOIN Users u ON cp2.user_id = u.id 
JOIN Messages m ON cp2.room_id = m.chat_id
WHERE cp1.user_id = :user_id 
AND cp2.user_id != :user_id
AND cp2.room_id = :specific_chat_id
ORDER BY m.sent_at DESC
LIMIT 1;"""

