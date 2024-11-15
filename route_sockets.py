from app import socketio
from flask_socketio import join_room, emit, disconnect
from flask import abort, request
from functools import wraps
from flask_jwt_extended import create_access_token, set_access_cookies, jwt_required, get_jwt, verify_jwt_in_request
import users, chats, posts

@socketio.on('connect')
def handle_connect():
    try:
        verify_jwt_in_request()
        token = get_jwt()
        if not token:
            return disconnect()
        user_permissions = token.get('user_permissions')
        rooms = user_permissions.keys()
        for room in rooms:
            join_room(room)
        emit('connected', {'message': 'Connected'})
    except Exception as e:
        print(f"Authentication failed: {e}")
    

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

    chats.send_chat(room_id, message)

    emit('receive_message', {
        'user_id': users.user_id(),
        'message': message
    }, room=room_id)

@socketio.on('send-post')
@jwt_required()
def handle_send_post(data):
    title = data['title']
    content = data['content']
    token = get_jwt()

    if has_room_permissions(permission_name='post', token=token):
        posts.send(title, content)
        emit('redirect', {'url': "/"}, to=request.sid)
    else:
        emit('post_denied', {'msg': "Access denied"})

@socketio.on('send-comment')
@jwt_required()
def handle_send_post(data):
    content = data['content']
    id = data['post_id']
    token = get_jwt()

    if has_room_permissions(permission_name='comment', token=token):
        posts.comment(content, id)
        emit('success', {'url': "/"})
    else:
        emit('post_denied', {'msg': "Access denied"})



def has_room_permissions(room_id=None, permission_name="", token=None):
    if token is None:
        token = get_jwt()
    
    if room_id == None:
        public_permissions = token.get('public_permissions')
        return permission_name in public_permissions
    else:
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

            if not has_room_permissions(room_id, permission_name, jwt_data):
                abort(403, description=f"Missing required permission: {permission_name}")

            
            return f(*args, **kwargs)
        return decorated_function
    return decorator