from flask import make_response, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, create_access_token, set_access_cookies, unset_jwt_cookies
from db import db
from app import app
import rooms

active_users = set()
print(active_users)

def login(username, password):
    try:
        sql =  text("SELECT id, password FROM users WHERE username = :username")
        user = db.session.execute(sql, {"username": username}).fetchone()
        if not user:
            return False
        else:
            hash_value = user.password
            if check_password_hash(hash_value, password):
               response = refresh_access_token(user.id)
               if response:
                   active_users.add(user.id)
                   response.headers['location'] = "/"
                   response.status_code = 302
                   return response
            else:
                return False
    except Exception as e:
        app.logger.error(f"A Database error occured durin login: {e}")
        return False
        
def register(username, password):
    hash_value = generate_password_hash(password)
    try:
        sql = text("INSERT INTO users (username, password) VALUES (:username, :password) RETURNING id")
        result = db.session.execute(sql, {"username": username, "password": hash_value})
        db.session.commit()
        user_id = result.fetchone()[0]
        sql = text("INSERT INTO PublicPermissions (user_id, permission_id) VALUES (:user_id, 3), (:user_id, 4)")
        db.session.execute(sql, {"user_id": user_id})
        db.session.commit()
        return login(username, password)
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"An error occured inserting registration into database: {e}")
        raise

def logout():
    response = make_response(redirect("/"))
    rooms.user_rooms.pop(user_id(), None)
    active_users.remove(user_id())
    unset_jwt_cookies(response)
    return response

def user_id():
    verify_jwt_in_request()
    return get_jwt_identity()

def get_permissions(user_id):
    try:
        user_permissions = {}

        sql = text("SELECT UP.room_id, P.permission_name \
        FROM UserPermissions UP, Permissions P, Users U \
        WHERE UP.permission_id = P.id AND U.id = :user_id AND U.id = UP.user_id \
        ")

        permissions = db.session.execute(sql, {"user_id": user_id}).fetchall()

        for perm in permissions:
            if perm[0] not in user_permissions:
                user_permissions[perm[0]] = []
            user_permissions[perm[0]].append(perm[1])
        
        sql = text("SELECT P.permission_name \
                FROM publicPermissions PP, permissions P, Users U \
                WHERE U.id = :user_id AND P.id = PP.permission_id AND PP.user_id = U.id \
                ")

        permissions = db.session.execute(sql, {"user_id": user_id}).fetchall()
        public_permissions = []
        for perm in permissions:
            public_permissions.append(perm[0])

        return (user_permissions, public_permissions)
    except Exception as e:
        app.logger.error(f"Database error during getting permissions: {e}")
        return None
    
def get_username(user_id):
    try:
        sql = text("SELECT username FROM users WHERE id = :user_id")
        result = db.session.execute(sql, {"user_id": user_id}).fetchone()
        return result[0]
    except Exception as e:
        app.logger.error(f"Database error during getting username: {e}")
        return None

def refresh_access_token(user_id):
    try:
        username = get_username(user_id)
        user_permissions = get_permissions(user_id)
        access_token = create_access_token(
            identity=user_id, 
            additional_claims=
            {
                "username": username,
                "user_permissions": user_permissions[0], 
                "public_permissions": user_permissions[1]
            },
        )
        response = make_response()

        response.delete_cookie('access_token_cookie')
        response.delete_cookie('csrf_access_token')

        set_access_cookies(response, access_token)
        return response
    except Exception as e:
        app.logger.error(f"Error refreshing access token for user {user_id}: {e}")
        return None