from sqlalchemy.sql import text
import uuid
from db import db
from users import user_id

def chat(room_id):
    sql = text("SELECT * FROM messages WHERE chat_id= :room_id")
    return db.session.execute(sql, {"room_id": room_id}).fetchall()

def send_chat(room_id, content):
    sender_id = user_id()
    sql = text("INSERT INTO messages (chat_id, sender_id, content, sent_at) VALUES (:chat_id, :sender_id, :content, NOW())")
    db.session.execute(sql, {"chat_id":room_id, "sender_id": sender_id, "content": content})
    db.session.commit()
    return True

def get_permissions(username):
    user_permissions = {}

    sql = text("SELECT UP.room_id, P.permission_name \
    FROM UserPermissions UP, Permissions P, Users U \
    WHERE UP.permission_id = P.id AND U.username = :username AND U.id = UP.user_id \
    ")

    permissions = db.session.execute(sql, {"username": username}).fetchall()

    for perm in permissions:
        if perm[0] not in user_permissions:
            user_permissions[perm[0]] = []
        user_permissions[perm[0]].append(perm[1])
    
    sql = text("SELECT P.permission_name \
               FROM publicPermissions PP, permissions P, Users U \
               WHERE U.username = :username AND P.id = PP.permission_id AND PP.user_id = U.id \
               ")

    permissions = db.session.execute(sql, {"username": username}).fetchall()
    public_permissions = []
    for perm in permissions:
        public_permissions.append(perm[0])

    return (user_permissions, public_permissions)

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

def get_user_rooms_layout(id):
    user_chats = {}
    sql = text("SELECT DISTINCT cp2.room_id, u.id, u.username \
        FROM UserPermissions cp1 \
        JOIN UserPermissions cp2 ON cp1.room_id = cp2.room_id  \
        JOIN Users u ON cp2.user_id = u.id \
        WHERE cp1.user_id = :user_id  \
        AND cp2.user_id != :user_id;")
    chats = db.session.execute(sql, {"user_id": id}).fetchall()

    for chat in chats:
        if chat[0] not in user_chats:
            user_chats[chat[0]] = []
        user_chats[chat[0]].append((chat[1], chat[2]))
    return user_chats


def get_every_user_room():
    all_rooms = {}
    sql = text("""WITH LastActive AS (
    SELECT 
        chat_id,
        MAX(sent_at) as last_active
    FROM Messages
    GROUP BY chat_id
    )
    SELECT 
        u1.id as user1_id,
        u1.username as user1_name,
        array_agg(json_build_object(
            'user_id', u2.id,
            'username', u2.username,
            'chat_id', c.id,
            'last_active', la.last_active
        )) as chats
    FROM chats c
    JOIN chatParticipants cp1 ON c.id = cp1.chat_id
    JOIN chatParticipants cp2 ON c.id = cp2.chat_id
    JOIN Users u1 ON cp1.user_id = u1.id
    JOIN Users u2 ON cp2.user_id = u2.id
    LEFT JOIN LastActive la ON c.id = la.chat_id
    WHERE cp1.user_id != cp2.user_id
    GROUP BY u1.id, u1.username
    ORDER BY u1.id;""")
    rooms = db.session.execute(sql).fetchall()
    print(rooms)

    for room in rooms:
        all_rooms.update({room[0]: room[1]})
    
    return all_rooms

sql = text("""SELECT 
    u1.id, 
    u1.username,
    u2.id,
    u2.username,
    c.id,
    MAX(m.sent_at)
    FROM chats c
    JOIN chatParticipants cp1 ON c.id = cp1.chat_id
    JOIN chatParticipants cp2 ON c.id = cp2.chat_id
    JOIN Users u1 ON cp1.user_id = u1.id
    JOIN Users u2 ON cp2.user_id = u2.id
    LEFT JOIN Messages m ON c.id = m.chat_id
    WHERE cp1.user_id != cp2.user_id
    GROUP BY c.id, u1.id, u1.username, u2.id, u2.username
    ORDER BY c.id, u1.id;
    """)

