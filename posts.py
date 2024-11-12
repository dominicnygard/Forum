from db import db
import users
from sqlalchemy.sql import text

def get_posts():
    sql = text("""SELECT P.title, P.content, U.username, P.sent_at 
            FROM Posts P, Users U 
            WHERE P.user_id=U.id ORDER BY P.id;""")
    return db.session.execute(sql).fetchall()

def send(title, content):
    user_id = users.user_id()
    if user_id == 0:
        return False
    sql = text("INSERT INTO posts (title, content, user_id, sent_at) VALUES (:title, :content, :user_id, NOW())")
    db.session.execute(sql, {"title":title, "content":content, "user_id":user_id})
    db.session.commit()
    return True