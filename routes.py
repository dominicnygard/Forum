from app import app, socketio, jwt
from flask import render_template, request, redirect, jsonify, make_response, abort
from flask_socketio import join_room, emit
from flask_jwt_extended import create_access_token, set_access_cookies, jwt_required, get_jwt, verify_jwt_in_request
from functools import wraps
import posts, users, chats

def has_room_permissions(room_id, permission_name, token=None):
    if token is None:
        token = get_jwt()
    
    user_permissions = token.get('user_permissions')
    room_permissions = user_permissions.get(str(room_id), [])

    return permission_name in room_permissions

def room_permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            jwt_data = get_jwt()


            room_id = kwargs.get('room_id')
            if not room_id:
                abort(400, description="Room ID not provided")

            if not has_room_permissions(room_id, permission_name, jwt_data):
                abort(403, description=f"Missing required permission: {permission_name}")

            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/")
def index():
    post_list = posts.get_posts()
    return render_template("index.html", count=len(post_list), messages = post_list)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            user_permissions = users.get_user_permissions(username)
            access_token = create_access_token(identity=users.user_id(), additional_claims={"user_permissions": user_permissions})
            response = make_response(redirect("/"))
            set_access_cookies(response, access_token)
            return response
        return redirect("/login")
        
@app.route("/register", methods=["GET", "POST"])
def register():
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
        else:
            return render_template("error.html", message="Rekisteröinti ei onnistunut")
        
@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/new", methods=["GET", "POST"])
def send():
    if request.method == "GET":
        return render_template("new.html")
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        if posts.send(title, content):
            return redirect("/")
        else:
            return render_template("error.html", message="Viestin lähetys ei onnistunut")
    
@app.route("/post/<int:id>/comment", methods=["GET", "POST"])
def comment(id):
    if request.method == "GET":
        return render_template("comment.html", id=id)
    if request.method == "POST":
        content = request.form["content"]
        if posts.comment(content, id):
            return redirect(f"/post/{id}")
        else:
            return render_template("error.html", message="Ei onnisutnut")

@app.route("/post/<int:id>")
def post(id):
    post = posts.get_post(id)
    comments = posts.get_comments(id)
    return render_template("post.html", post_id=id, post=post, comments=comments)

@app.route("/chat/<string:room_id>", methods=["GET", "POST"])
@jwt_required()
@room_permission_required('view')
def chat(room_id):
    #if user1.token in room.session and not user2.token in room.session:
        #pass
    #elif user2.token in room.session and not user1.token in room.session:
        #pass
    #elif not user1.token in room.session and not user2.token in room.session:
        #create room
    if request.method == "GET":
        messages = chats.chat(room_id)
        return render_template("chat.html", id=room_id, messages=messages)
    if request.method == "POST":
        content = request.form["content"]
        if chats.send_chat(id, content):
            return redirect(f"/chat/{room_id}")
        else:
            return render_template("error.html", message="Ei toimi")




@app.route("/start_chat/<int:user_id>")
@jwt_required()
def start_chat(user_id):
    room = chats.get_user_rooms(user_id)
    if room == None:
        chats.create_room(user_id)
    return redirect(f"/chat/{room[0]}")

        
@socketio.on('join')
@jwt_required()
def join(data):
    user_id = users.user_id()
    room = data['room_id']
    join_room(room)

    emit('join_confirmation', {'msg': f"{user_id} has enterend room {room}"}, room=room)

@socketio.on('send-message')
@jwt_required()
def handle_send_message(data):
    room_id = data['room_id']
    message = data['message']
    receiver_id = users.get_other_user(room_id)[0]

    chats.send_chat(room_id, receiver_id, message)

    emit('receive_message', {
        'user_id': receiver_id,
        'message': message
    }, room=room_id)


