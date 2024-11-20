from app import app, socketio
from flask import render_template, request, redirect, make_response, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from route_sockets import room_permission_required
import posts, users, chats, rooms
from datetime import datetime, timedelta

@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", message="Bad Request (400)"), 400

@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", message="Forbidden (403)"), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", message="Page Not Found (404)"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", message="Internal Server Error (500)"), 500

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    app.logger.error(f"Unhandled exception: {e}")
    return render_template("error.html", message="An unexpected error occurred"), 500

@app.route("/")
def index():
    post_list = posts.get_posts()
    return render_template("index.html", count=len(post_list), messages = post_list)

@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "GET":
            return render_template("login.html")
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            response = users.login(username, password)
            if response:
                return response
            return redirect("/login")
    except Exception as e:
        app.logger.error(f"Login error: {e}")
        return render_template("error.html", message="An unexpected error occurred during login")
        
@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        if request.method == "GET":
            return render_template("register.html")
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]
            if password != confirm_password:
                return render_template("error.html", message="Salasanat eroavat")
            if users.register(username, password):
                return redirect("/")
            return redirect("/register")
    except Exception as e:
        app.logger.error(f"Register error: {e}")
        return render_template("error.html", message="An unexpected error occurred during registration")
        
@app.route("/logout")
def logout():
    response = users.logout()
    return response

@app.route("/new")
@jwt_required()
@room_permission_required('post')
def send():
    return render_template("new.html")

@app.route("/post/<int:id>")
def post(id):
    try:
        post = posts.get_post(id)
        comments = posts.get_comments(id)
        return render_template("post.html", post_id=id, post=post, comments=comments)
    except Exception as e:
        app.logger.error(f"Error fetching post {id}: {e}")
        return render_template("error.html", message="An unexpected error occurred while fetching the post"), 500
        

@app.route("/chat/<int:room_id>", methods=["GET"])
@jwt_required()
@room_permission_required('view')
def chat(room_id):
    try:
        messages = chats.chat(room_id)

        return render_template("chat.html", id=room_id, messages=messages)
    except Exception as e:
        app.logger.error(f"Error fetching chat {room_id}: {e}")
        return render_template("error.html", message="An unexpected error occurred while fetching the chat"), 500

@app.route("/start-chat/<int:user_id>")
@jwt_required()
def start_chat(user_id):
    try:
        current_user = get_jwt_identity()

        room_id = rooms.existing_room(current_user, user_id)
        if room_id:
            return redirect(f"/chat/{room_id}")
        
        room_id = rooms.existing_room_db(current_user, user_id)
        if room_id:
            return redirect(f"/chat/{room_id[0]}")
        
        room_id = rooms.create_new_room(current_user, user_id)
        rooms.insert_user_room_memory(current_user, room_id)
        rooms.insert_user_room_memory(user_id, room_id)
        socketio.emit('join-room', {'room': room_id}, room=f"user_{current_user}")
        socketio.emit('join-room', {'room': room_id}, room=f"user_{user_id}")

        response = users.refresh_access_token(current_user)
        if not response:
            return render_template("error.html", message="Failed to refresh access token"), 500
        
        if user_id in users.active_users:
            socketio.emit('refresh-token', room=f"user_{user_id}")

        response.headers['location'] = url_for('chat', room_id=room_id)
        response.status_code = 302
        return response
    except Exception as e:
        app.logger.error(f"Error starting chat with user {user_id}: {e}")
        return render_template("error.html", message="An error occurred while starting the chat"), 500

@app.route('/get-chats', methods=['GET'])
@jwt_required()
def api_get_chats():
    try:
        user_id = get_jwt_identity()
        chat_list = rooms.get_user_rooms(user_id)
        return jsonify(chat_list)
    except Exception as e:
        app.logger.error(f"Error fetching chats for user {user_id}: {e}")
        return jsonify({"error": "An unexpected error occurred while fetching the chats"}), 500
    
@app.route('/refresh', methods=['GET'])
@jwt_required()
def refresh():
    try:
        user_id = get_jwt_identity()
        response = users.refresh_access_token(user_id)
        if response:
            return response
        return jsonify({"error": "Failed to refresh access token"}), 500
    except Exception as e:
        app.logger.error(f"Error refreshing token for user {user_id}: {e}")
        return jsonify({"error": "An unexpected error occurred while refreshing the token"}), 500

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now()
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            response = users.refresh_access_token(get_jwt_identity())
        return response
    except (RuntimeError, KeyError):
        return response



