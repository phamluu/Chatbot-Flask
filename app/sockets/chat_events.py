from flask_socketio import SocketIO, join_room, leave_room, send, emit
from flask import request
from app import socketio, db
from app.models import User, Message, Conversation
from app.services.chat_service import handle_new_msg, get_users_data, create_conversation
from app.services.staff_service import get_conversations_by_staff_id

connected_users = {}

@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('user_id')
    if user_id:
        connected_users[user_id] = request.sid
        print(f"User {user_id} connected with SID {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    for uid, sid in connected_users.items():
        if sid == request.sid:
            del connected_users[uid]
            print(f"User {uid} disconnected")
            break

@socketio.on('get_users')
def send_users():
    emit('update_user_list', get_users_data())

@socketio.on('new_user')
def handle_new_user():
    new_user = User()
    db.session.add(new_user)
    db.session.commit()
    emit('new_user', new_user.id)
    send_users()
    join_room(new_user.id)
    send(f'1 khách đã tham gia phòng chat!', room=new_user.id)

@socketio.on('new_message')
def handle_message(data):
    handle_new_msg(data, connected_users)

@socketio.on('new_conversation')
def handle_new_conversation(data):
    convo_data = create_conversation(data)
    emit('new_conversation', convo_data)
    emit('update_conversations_staff', get_conversations_by_staff_id(data['staff_id']))
    emit('update_conversations', [c.to_dict() for c in Conversation.query.all()])

@socketio.on('get_conversations')
def handle_get_conversations(data):
    staff_id = data.get('staff_id')
    emit('update_conversations', get_conversations_by_staff_id(staff_id))

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    send(f'{data["user"]} đã tham gia phòng chat!', room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    send(f'{data["user"]} đã rời khỏi phòng chat.', room=room)
