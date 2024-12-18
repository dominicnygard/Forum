import re
from app import app, socketio, jwt
from flask import render_template, request, redirect, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from jwt.exceptions import ExpiredSignatureError
from route_sockets import room_permission_required, has_room_permissions
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
    search_query = request.args.get("search", "")
    return render_template("index.html", search_query=search_query)

@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "GET":
            return render_template("login.html")
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            if len(username) < 4 or len(username) >= 20:
                return render_template("login.html", error="Invalid username, username must be between 4 and 20 characters long")
            if len(password) < 8 or len(password) >= 20:
                return render_template("login.html", error="Invalid password, password must be between 8 and 20 characters long")
            
            response = users.login(username, password)
            if response:
                response.headers['location'] = url_for("index")
                response.status_code = 302
                return response
            else:
                return render_template("login.html", error="Wrong username or password")
                
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
            if re.fullmatch(r"^[a-zA-Z0-9_.]{4,20}$", username) is None:
                return render_template("register.html", error="Invalid username, username must be between 4 and 20 characters long")
            if re.fullmatch(r"^[a-zA-Z0-9_#%&$!*?.;:~^]{8,20}$", password) is None:
                return render_template("register.html", error="Invalid password, password must be between 8 and 20 characters long")
            if password != confirm_password:
                return render_template("register.html", error="The passwords don't match")
            
            success = users.register(username, password)
            if success:
                return redirect(url_for("login"))
            else:
                return render_template("register.html", error="Username already exists")

    except Exception as e:
        app.logger.error(f"Register error: {e}")
        return render_template("error.html", message="An unexpected error occurred during registration")
        
@app.route("/logout")
def logout():
    response = users.logout()
    return response

@app.route("/new", methods=["GET", "POST"])
@jwt_required()
@room_permission_required('post')
def new_post():
    if request.method == "GET":
        return render_template("new.html")
    if request.method == "POST":
        if not has_room_permissions(permission_name='post', token=get_jwt()):
            return render_template("error.html", message="You are not permitted to post"), 403
        
        title = request.form["title"]
        content = request.form["content"]
        max_title_length = 100
        max_content_length = 5000

        errors = {}

        if not (1 <= len(title) <= max_title_length):
            errors["title"] = f"Title must be between 1-{max_title_length} characters long"

        if not (1 <= len(content) <= max_content_length):
            errors["content"] = f"Post must be between 1-{max_content_length} characters long"
        
        if errors:
            return jsonify({"succcess": False, "errors": errors}), 400
        
        try:
            posts.send(title, content)
            return jsonify({"success": True}), 200
        except Exception as e:
            app.logger.error(f"Error sending post: {e}")
            return jsonify({"success": False, "errors": {"general": "An unexpected error occurred. Please try again."}}), 500

@app.route("/post/<int:post_id>", methods=["GET", "POST", "DELETE"])
def post(post_id):
    try:
        if request.method == "GET":
            post = posts.get_post(post_id)
            return render_template("post.html", post_id=post_id, post=post)
    except Exception as e:
        app.logger.error(f"Error fetching post {post_id}: {e}")
        return render_template("error.html", message=f"An error occured while loading the page for post {post_id}")
            
    if request.method == "POST":
        try:
            verify_jwt_in_request()
            content = request.form["content"]
            if has_room_permissions(permission_name='comment', token=get_jwt()):
                if len(content) < 1 or len(content) >= 2000:
                    return jsonify({"success": False, "error": "Comment must be between 1 and 2000 characters long"}), 400
                posts.comment(content, post_id)
                return jsonify({"success": True}), 200
        except Exception as e:
            app.logger.error(f"Error posting comment to post {post_id}: {e}")
            return render_template("error.html", message="An error occurred while posting the comment"), 500
        
    if request.method == "DELETE":
        try:
            verify_jwt_in_request()
            comment_id = int(request.args.get("comment_id", 0))
            user_id = get_jwt_identity()
            comment = posts.check_user_comment(user_id, comment_id)

            if comment is None:
                return jsonify({"success": False, "error": "This is not your comment!"}), 403
            if has_room_permissions(permission_name='delete', token=get_jwt()):
                posts.delete_comment(comment_id, user_id)
                return jsonify({"success": True}), 200
            return jsonify({"success": False, "error": "You do not have permission to delete this comment"}), 403
        except Exception as e:
            app.logger.error(f"Error deleting comment on post {post_id}: {e}")
            return jsonify({"success": False, "error": "An unknown error occured"}), 500

        

@app.route("/chat/<int:room_id>", methods=["GET"])
@jwt_required()
@room_permission_required('view')
def chat(room_id):
    try:
        return render_template("chat.html", id=room_id)
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
            socketio.emit('update-rooms')


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
    
@app.route('/load-posts', methods=['GET'])
def api_load_posts():
    try:
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 10))
        search_query = request.args.get("search_query", '')

        post_data = posts.get_posts(offset, limit, search_query)
        posts_list = []
        for post in post_data:
            posts_list.append({
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "user_id": post.user_id,
                "username": post.username,
                "sent_at": post.sent_at.isoformat(),
                "comment_count": post.comment_count
            })

        return jsonify(posts_list), 200
    except Exception as e:
        app.logger.error(f"Error fetching posts: {e}")
        return jsonify({"error": "An error occurred while fetching the posts"}), 500

@app.route('/load-comments/<int:post_id>', methods=['GET'])
def api_load_comments(post_id):
    try:
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 15))

        comments_data = posts.get_comments(post_id, offset, limit)
        comments_list = []
        for comment in comments_data:
            comments_list.append({
                'user_id':  comment.user_id,
                'username': comment.username,
                'sent_at':  comment.sent_at.isoformat(),
                'content':  comment.content,
                'id':       comment.id
            })
        
        return jsonify(comments_list), 200
    except Exception as e:
        app.logger.error(f"Error fetching comments for post {post_id}: {e}")
        return jsonify({"error": "An error occurred while fetching comments"}), 500
                
@app.route('/load-messages/<int:room_id>', methods=['GET'])
@jwt_required()
@room_permission_required('view')
def api_load_messages(room_id):
    try:
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 30))

        messages_data = chats.chat(room_id, offset, limit)
        messages_list = []
        for message in messages_data:
            messages_list.append({
                'username': message.username,
                'sent_at': message.sent_at.isoformat(),
                'content': message.content,
                'message_id': message.id
            })

        return jsonify(messages_list), 200
    except Exception as e:
        app.logger.error(f"Error fetching messages for chat {room_id}: {e}")
        return jsonify({"error": "An error occurred while fetching messages"}), 500

@app.route('/delete-post/<int:post_id>', methods=['DELETE'])
@jwt_required()
@room_permission_required('delete')
def api_delete_post(post_id):
    user_id = get_jwt_identity()
    user_post = posts.check_user_post(user_id, post_id)
    if user_post is None:
        return jsonify({"error": "You are not permitted to delete this post"}), 403
    try:
        posts.delete_post(post_id, get_jwt_identity())
        return jsonify({"msg": "Post deleted"}), 200
    except Exception as e:
        app.logger.error(f"Error deleting post {post_id}: {e}")
        return jsonify({"error": "An error occurred while deleting the post"}), 500

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

@app.context_processor
def inject_user():
    user = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            token = get_jwt()
            username = token.get("username")
            user = {"id": user_id, "username": username}
    except Exception as e:
        app.logger.error(f"Error in context processor: {e}")
    return {'current_user': user}

@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return render_template("error.html", message="You are not logged in"), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return render_template("error.html", message="Your token has expired"), 401

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    return render_template("error.html", message="Your token is invalid"), 401