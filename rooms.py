from sqlalchemy.sql import text
from db import db

user_rooms = {}

def get_user_rooms_db(id):
    if id in user_rooms:
        print("Dict")
        print(sort_rooms(user_rooms[id]))
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

def sort_rooms(rooms):
    return sorted(
        rooms.items(),
        key=lambda x: x[1][2],
        reverse=True
    )[:30]

def update_room(user_id, other_user_id, room_id, last_active):
    print(last_active)
    user_rooms[user_id][room_id][2] = last_active
    user_rooms[other_user_id][room_id][2] = last_active
    print(user_rooms)

def get_other_user(user_id, room_id):
    if user_id in user_rooms and room_id in user_rooms[user_id]:
        return user_rooms[user_id][room_id][0]
    else:
        return None


    