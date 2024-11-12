from db import db
import users
from sqlalchemy.sql import text

def get_posts():
    sql = text("""SELECT P.title, P.content, U.username, P.sent_at, P.id 
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

def get_post(id):
    sql = text("""SELECT P.title, P.content, U.username, P.sent_at FROM Posts P, Users U WHERE P.id = :id AND P.user_id=U.id""")
    return db.session.execute(sql, {"id":id}).fetchone()

def comment(content, id):
    user_id = users.user_id()
    if user_id == 0:
        return False
    sql = text("INSERT INTO comments (content, user_id, post_id, sent_at) VALUES (:content, :user_id, :post_id, NOW())")
    db.session.execute(sql, {"content":content, "user_id":user_id, "post_id":id})
    db.session.commit()
    return True

def get_comments(id):
    sql = text("""SELECT U.username, C.sent_at, C.content FROM Comments C, Users U WHERE C.post_id = :id AND C.user_id=U.id ORDER BY C.id""")
    return db.session.execute(sql, {"id":id}).fetchall()