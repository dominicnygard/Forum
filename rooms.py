from sqlalchemy.sql import text
from threading import Lock
import uuid
from db import db
from app import app

user_rooms_lock = Lock()
user_rooms = {}

def get_user_rooms(id):
    try:
        if id in user_rooms:
            return sort_rooms(user_rooms[id])
        
        user_chats = {}
        sql = text("""
        SELECT DISTINCT cp2.room_id, u.id, u.username, COALESCE(last_message.latest_time, NOW()) as last_active
        FROM UserPermissions cp1 
        JOIN UserPermissions cp2 ON cp1.room_id = cp2.room_id 
        JOIN Users u ON cp2.user_id = u.id 
        LEFT JOIN (
            SELECT chat_id, MAX(sent_at) as latest_time
            FROM Messages
            GROUP BY chat_id
        ) last_message ON cp2.room_id = last_message.chat_id
        WHERE cp1.user_id = :user_id 
        AND cp2.user_id != :user_id       
        ORDER BY last_active DESC
        LIMIT 100;
        """)
        chats = db.session.execute(sql, {"user_id": id}).fetchall()

        user_chats = {
            str(row.room_id): [row.id, row.username, row.last_active.isoformat()] 
            for row in chats
        }

        user_rooms[id] = user_chats

        return sort_rooms(user_chats)
    except Exception as e:
        app.logger.error(f"Error fetching user rooms from database/memory: {e}")
        return []


def sort_rooms(rooms):
    return sorted(
        rooms.items(),
        key=lambda x: x[1][2],
        reverse=True
    )[:30]

def update_room(user_id, other_user_id, room_id, last_active):
    with user_rooms_lock:
        user_rooms[user_id][room_id][2] = last_active
        if other_user_id in user_rooms:
            user_rooms[other_user_id][room_id][2] = last_active


def get_other_user(user_id, room_id):
    if user_id in user_rooms and room_id in user_rooms[user_id]:
        return user_rooms[user_id][room_id][0]
    else:
        return None
    
def existing_room(user_id, other_user_id):
    for room_id, data in user_rooms[user_id].items():
        if data[0] == other_user_id:
            return room_id
    return None

def existing_room_db(user1_id, user2_id):
    try:
        sql = text("""
            SELECT cp1.room_id
            FROM UserPermissions cp1
            JOIN UserPermissions cp2 ON cp1.room_id = cp2.room_id
            WHERE cp1.user_id = :user1_id AND cp2.user_id = :user2_id
            LIMIT 1
        """)
        result = db.session.execute(sql, {"user1_id": user1_id, "user2_id": user2_id}).fetchone()
        return result
    except Exception as e:
        app.logger.error(f"Error fetching existing room from database: {e}")
        return None

def create_new_room(user1_id, user2_id):
    try:
        room_uuid = str(uuid.uuid4())
        sql = text("INSERT INTO chats (room_id) VALUES (:room_id) RETURNING id")
        result = db.session.execute(sql, {"room_id": room_uuid})
        db.session.commit()
        room_id = result.fetchone()[0]

        sql = text("""
            INSERT INTO UserPermissions (room_id, user_id, permission_id)
            VALUES
            (:room_id, :user1_id, 1),
            (:room_id, :user1_id, 2),
            (:room_id, :user2_id, 1),
            (:room_id, :user2_id, 2)
        """)
        db.session.execute(sql, {"room_id": room_id, "user1_id": user1_id, "user2_id": user2_id})
        db.session.commit()
        return room_id
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating chat room for users {user1_id} and {user2_id}: {e}")
        return None
    
def insert_user_room_memory(user_id, room_id):
    try:
        sql = text("""
        SELECT cp.room_id, u.id AS user_id, u.username, COALESCE(last_message.latest_time, NOW()) as last_active
        FROM UserPermissions cp
        JOIN Users u ON cp.user_id = u.id
        LEFT JOIN (
            SELECT chat_id, MAX(sent_at) as latest_time
            FROM Messages
            WHERE chat_id = :room_id
            GROUP BY chat_id
        ) last_message ON cp.room_id = last_message.chat_id
        WHERE cp.room_id = :room_id
        AND cp.user_id != :user_id
        LIMIT 1;
        """)

        chat = db.session.execute(sql, {"room_id": room_id, "user_id": user_id}).fetchone()

        if chat:
            room_data = {
                str(chat.room_id): [chat.user_id, chat.username, chat.last_active.isoformat()]
            }
            with user_rooms_lock:
                if user_id not in user_rooms:
                    user_rooms[user_id] = {}
                user_rooms[user_id].update(room_data)


    except Exception as e:
        app.logger.error(f"Error inserting room {room_id} for user {user_id}: {e}")
        return None