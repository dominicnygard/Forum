from db import db
import users
from app import app
from sqlalchemy.sql import text

def get_posts(offset=0, limit=10):
    try:
        sql = text("""
                SELECT P.title, P.content, U.username, P.sent_at, P.id 
                FROM Posts P, Users U 
                WHERE P.user_id=U.id 
                ORDER BY P.sent_at DESC
                LIMIT :limit OFFSET :offset
                """)
        return db.session.execute(sql, {"limit": limit, "offset": offset}).fetchall()
    except Exception as e:
        app.logger.error(f"Error fetching posts from database: {e}")
        return []
    
def send(title, content):
    try:
        user_id = users.user_id()
        if user_id == 0:
            return False
        sql = text("""
                   INSERT INTO posts (title, content, user_id, sent_at) 
                   VALUES (:title, :content, :user_id, NOW())""")
        db.session.execute(sql, {"title":title, "content":content, "user_id":user_id})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error inserting post into database: {e}")
        raise

def get_post(id):
    try:
        sql = text("""
                   SELECT P.title, P.content, U.username, P.sent_at 
                   FROM Posts P, Users U 
                   WHERE P.id = :id AND P.user_id=U.id
                   """)
        return db.session.execute(sql, {"id":id}).fetchone()
    except Exception as e:
        app.logger.error(f"Error fetching post from database: {e}")
        return None

def comment(content, id):
    try:
        user_id = users.user_id()
        if user_id == 0:
            return False
        sql = text("""
                   INSERT INTO comments (content, user_id, post_id, sent_at) 
                   VALUES (:content, :user_id, :post_id, NOW())
                   """)
        db.session.execute(sql, {"content":content, "user_id":user_id, "post_id":id})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error inserting comment into database: {e}")
        raise

def get_comments(post_id, offset=0, limit=15):
    try:
        sql = text("""
                   SELECT U.username, C.sent_at, C.content 
                   FROM Comments C, Users U 
                   WHERE C.post_id = :id AND C.user_id=U.id 
                   ORDER BY C.sent_at DESC
                   LIMIT :limit OFFSET :offset
                   """)
        return db.session.execute(sql, {"id":post_id, "limit": limit, "offset": offset}).fetchall()
    except Exception as e:
        app.logger.error(f"Error fetching comments from database: {e}")
        return []