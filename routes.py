from app import app
from flask import render_template, request, redirect, make_response, jsonify, Blueprint
from flask_jwt_extended import create_access_token, set_access_cookies, jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request, unset_jwt_cookies, set_refresh_cookies, create_refresh_token
from route_sockets import room_permission_required
import posts, users, chats
from datetime import datetime, timedelta

@app.route("/")
def index():
    print(chats.get_every_user_room())
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
            user_permissions = chats.get_permissions(username)
            access_token = create_access_token(
                identity=users.user_id(), 
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
            print("Token set in login:", access_token)
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
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200

@app.route("/new")
@jwt_required()
@room_permission_required('post')
def send():
    return render_template("new.html")
    
@app.route("/post/<int:id>/comment", methods=["GET", "POST"])
@jwt_required()
@room_permission_required('comment')
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
    #if request.method == "POST":
        #content = request.form["content"]
        #if chats.send_chat(id, content):
            #return redirect(f"/chat/{room_id}")
        #else:
            #return render_template("error.html", message="Ei toimi")

@app.route("/start_chat/<int:user_id>")
@jwt_required()
def start_chat(user_id):
    room = chats.get_user_rooms(user_id)
    if room == None:
        chats.create_room(user_id)
    return redirect(f"/chat/{room[0]}")

@app.route('/get-chats', methods=['GET'])
@jwt_required()
def api_get_chats():
    user_id = get_jwt_identity()
    chat_list = chats.get_user_rooms_layout(user_id)
    print(chat_list)
    return jsonify(chat_list)

@app.after_request
def refresh_expiring_jwts(response):
    print("after request")
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now()
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            print("token refresh")
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response



