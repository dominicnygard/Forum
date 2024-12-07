import uuid
from sqlalchemy.sql import text
from db import db
from users import user_id
from app import app

def chat(room_id, offset=0, limit=30):
    try:
        sql = text("""
                SELECT username, content, sent_at, sub.id AS id 
                FROM (
                    SELECT M.sender_id, M.content, M.sent_at, M.id
                    FROM messages M
                    WHERE M.chat_id = :room_id
                    ORDER BY M.sent_at DESC
                    LIMIT :limit OFFSET :offset
                    ) sub
                LEFT JOIN users ON users.id = sub.sender_id
                ORDER BY sub.sent_at DESC
                """)
        return db.session.execute(sql, {"room_id": room_id, "limit": limit, "offset": offset}).fetchall()
    except Exception as e:
        app.logger.error(f"Error fetching chat {room_id}: {e}")
        return []

def send_chat(room_id, content):
    try:
        sender_id = user_id()
        sql = text("""INSERT INTO messages (chat_id, sender_id, content, sent_at) 
                   VALUES (:chat_id, :sender_id, :content, NOW()) RETURNING sent_at""")
        result = db.session.execute(sql, {"chat_id":room_id, "sender_id": sender_id, "content": content})
        db.session.commit()
        sent_at = result.fetchone()[0]
        return sent_at
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error inserting chat into database: {e}")
        raise


def get_user_rooms(id):
    sql = text("""SELECT room_id 
        FROM UserPermissions 
        WHERE user_id IN (:user1_id, :user2_id) 
        GROUP BY room_id 
        HAVING COUNT(DISTINCT user_id) = 2 
        """)
    return db.session.execute(sql, {"user1_id": id, "user2_id": user_id()}).fetchone()

def create_room(id):
    room_id = str(uuid.uuid4())
    sql = text("INSERT INTO chats (room_id) VALUES (:room_id) RETURNING id")
    result = db.session.execute(sql, {"room_id": room_id})
    db.session.commit()
    id_room = result.fetchone()[0]
    sql = text("""INSERT INTO UserPermissions (room_id, user_id, permission_id) 
               VALUES 
               (:room_id, :user1_id, 1), 
               (:room_id, :user1_id, 2), 
               (:room_id, :user2_id, 1), 
               (:room_id, :user2_id, 2) 
               """)
    db.session.execute(sql, {"room_id": id_room[0], "user1_id": user_id(), "user2_id": id})
    db.session.commit()

    return id_room[0]

def delete_message(message_id, user_id):
    try:
        sql = text("""
                   DELETE FROM messages 
                   WHERE id = :id AND sender_id = :user_id
                   """)
        db.session.execute(sql, {"id": message_id, "user_id": user_id})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting message  {message_id} from database: {e}")
        raise