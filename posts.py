from db import db
import users
from app import app
from sqlalchemy.sql import text

def get_posts(offset=0, limit=10, search = ''):
    try:
        search = "%" + search + "%"
        sql = text("""
                    SELECT 
                        P.title, 
                        P.content, 
                        U.username, 
                        P.sent_at, 
                        P.id, 
                        U.id AS user_id,
                        COALESCE(comment_count.total_comments, 0) AS comment_count
                    FROM 
                        Posts P
                    JOIN 
                        Users U ON P.user_id = U.id
                    LEFT JOIN 
                        (SELECT post_id, COUNT(*) AS total_comments 
                        FROM Comments 
                        GROUP BY post_id) comment_count 
                    ON 
                        P.id = comment_count.post_id
                    WHERE 
                        P.title ILIKE :search
                    ORDER BY 
                        P.sent_at DESC
                    LIMIT :limit OFFSET :offset
                """)
        return db.session.execute(sql, {"search": search, "limit": limit, "offset": offset}).fetchall()
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

def get_post(post_id):
    try:
        sql = text("""
                   SELECT P.title, P.content, U.username, P.sent_at, P.user_id
                   FROM Posts P, Users U 
                   WHERE P.id = :id AND P.user_id=U.id
                   """)
        return db.session.execute(sql, {"id":post_id}).fetchone()
    except Exception as e:
        app.logger.error(f"Error fetching post from database: {e}")
        return None

def comment(content, id):
    try:
        user_id = users.user_id()
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
                   SELECT U.id AS user_id, U.username, C.sent_at, C.content, C.id 
                   FROM Comments C, Users U 
                   WHERE C.post_id = :id AND C.user_id=U.id 
                   ORDER BY C.sent_at DESC
                   LIMIT :limit OFFSET :offset
                   """)
        return db.session.execute(sql, {"id":post_id, "limit": limit, "offset": offset}).fetchall()
    except Exception as e:
        app.logger.error(f"Error fetching comments from database: {e}")
        return []

def check_user_post(user_id, post_id):
    try:
        sql = text("""
                   SELECT P.id 
                   FROM Posts P 
                   WHERE P.id = :post_id AND P.user_id = :user_id 
                   """)
        return db.session.execute(sql, {"user_id":user_id, "post_id":post_id}).fetchone()
    except Exception as e:
        app.logger.error(f"Error fetching user {user_id} post {post_id} from database: {e}")
        return None

def check_user_comment(user_id, comment_id):
    try:
        sql = text("""
                   SELECT C.id 
                   FROM Comments C 
                   WHERE C.id = :comment_id AND C.user_id = :user_id 
                   """)
        return db.session.execute(sql, {"user_id":user_id, "comment_id":comment_id}).fetchone()
    except Exception as e:
        app.logger.error(f"Error fetching user {user_id} comment {comment_id} from database: {e}")
        return None

def delete_post(post_id, user_id):
    try:
        sql = text("""
                   DELETE FROM Posts 
                   WHERE id = :id AND user_id = :user_id
                   """)
        db.session.execute(sql, {"id":post_id, "user_id":user_id})
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting post from database: {e}")
        return False
    
def delete_comment(comment_id, user_id):
    try:
        sql = text("""
                   DELETE FROM Comments 
                   WHERE id = :id AND user_id = :user_id
                   """)
        db.session.execute(sql, {"id":comment_id, "user_id":user_id})
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting comment from database: {e}")
        return False