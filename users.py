from flask import make_response, redirect, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, create_access_token, set_access_cookies, unset_jwt_cookies
from db import db

def login(username, password):
    sql =  text("SELECT id, password FROM users WHERE username = :username")
    user = db.session.execute(sql, {"username": username}).fetchone()
    if not user:
        return False
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            user_permissions = get_permissions(username)
            access_token = create_access_token(
                identity=user.id, 
                additional_claims=
                {
                    "user_permissions": user_permissions[0], 
                    "public_permissions": user_permissions[1]
                },
            )
            response = make_response(redirect("/"))

            response.delete_cookie('access_token_cookie')
            response.delete_cookie('csrf_access_token')

            set_access_cookies(response, access_token)
            return response
        else:
            return False
        
def register(username, password):
    hash_value = generate_password_hash(password)
    try:
        sql = text("INSERT INTO users (username, password) VALUES (:username, :password)")
        db.session.execute(sql, {"username": username, "password": hash_value})
        db.session.commit()
        sql = text('SELECT id FROM users WHERE username = :username')
        user_id = db.session.execute(sql, {"username": username}).fetchone()
        sql = text("INSERT INTO PublicPermissions (user_id, permission_id) VALUES (:user_id, 3), (:user_id, 4)")
        db.session.execute(sql, {"user_id": user_id[0]})
        db.session.commit()
    except Exception as e:
        print(e)
        return False
    return login(username, password)

def logout():
    response = make_response(redirect("/"))
    unset_jwt_cookies(response)
    return response

def user_id():
    verify_jwt_in_request()
    return get_jwt_identity()

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

