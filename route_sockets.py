from app import socketio, app
from flask_socketio import join_room, emit, disconnect
from flask import abort, request
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
import users, chats, posts, rooms

@socketio.on('connect')
def handle_connect():
    try:
        verify_jwt_in_request()
        token = get_jwt()
        if not token:
            emit('error', {'message': 'Authentication required'}, to=request.sid)
            return disconnect()
        user_permissions = token.get('user_permissions')
        rooms = user_permissions.keys()
        for room in rooms:
            join_room(room)
        user_id = users.user_id()
        join_room(f"user_{user_id}")
        emit('connected', {'message': 'Connected'})
    except Exception as e:
        app.logger.error(f"Connecting to server failed: {e}")
        emit('error', {'message': 'An error occurred while connecting to the server'}, to=request.sid)
        disconnect()

@socketio.on('join')
@jwt_required()
def join(data):
    try:
        user_id = users.user_id()
        room = data['room_id']
        join_room(room)

        emit('join-confirmation', {'msg': f"{user_id} has entered room {room}"}, room=room)
    except Exception as e:
        app.logger.error(f"Error joining room {room}: {e}")
        emit('error', {'message': 'An error occurred while joining a room'}, to=request.sid)

@socketio.on('send-message')
@jwt_required()
def handle_send_message(data):
    try:
        verify_jwt_in_request()
        room_id = data['room_id']
        message = data['message']

        sent_at = chats.send_chat(room_id, message)
        other_user_id = rooms.get_other_user(users.user_id(), room_id)

        rooms.update_room(users.user_id(), other_user_id, room_id, sent_at.isoformat())

        token = get_jwt()
        username = token.get('username')
        emit('receive-message', {
            'username': username,
            'message': message,
        }, room=room_id)

        emit('update-rooms', room=room_id)
    except Exception as e:
        app.logger.error(f"Error sending message: {e}")
        emit('error', {'message': 'An error occurred while sending the message'}, to=request.sid)

@socketio.on('send-post')
@jwt_required()
def handle_send_post(data):
    try:
        title = data['title']
        content = data['content']
        token = get_jwt()

        if has_room_permissions(permission_name='post', token=token):
            posts.send(title, content)
            emit('redirect', {'url': "/"}, to=request.sid)
        else:
            emit('post_denied', {'msg': "Access denied"})
    except Exception as e:
        app.logger.error(f"Error sending post: {e}")
        emit('error', {'message': 'An error occurred while sending the post'}, to=request.sid)

@socketio.on('send-comment')
@jwt_required()
def handle_send_post(data):
    try:
        content = data['content']
        id = data['post_id']
        token = get_jwt()

        if has_room_permissions(permission_name='comment', token=token):
            posts.comment(content, id)
            emit('success', {'url': "/"})
        else:
            emit('post_denied', {'msg': "Access denied"})
    except Exception as e:
        app.logger.error(f"Error sending comment: {e}")
        emit('error', {'message': 'An error occurred while sending the comment'}, to=request.sid)



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
            print(room_id)

            if not has_room_permissions(room_id, permission_name, jwt_data):
                abort(403, description=f"Missing required permission: {permission_name}")

            
            return f(*args, **kwargs)
        return decorated_function
    return decorator