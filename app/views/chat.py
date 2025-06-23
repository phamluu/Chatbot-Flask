# app/views/chat.py
from datetime import datetime
from venv import logger
from flask import Blueprint, Response, jsonify, render_template, request
from flask_socketio import  join_room, leave_room, send
from app.models import ChatbotResponse, Faq, Message, User
from app.models import Conversation
from app import db, socketio
from app.views.staff import get_conversations_by_staff_id
from transformers import pipeline

# Khởi tạo mô hình NLP (ở đây sử dụng GPT-2)
nlp_pipeline = pipeline("text-generation", model="gpt2")

chat_bp = Blueprint('chat', __name__)

connected_users = {}

@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('user_id')
    if user_id:
        connected_users[user_id] = request.sid
        print(f"User {user_id} connected with SID {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    user_id = next((uid for uid, sid in connected_users.items() if sid == request.sid), None)
    if user_id:
        del connected_users[user_id]
        print(f"User {user_id} disconnected")

@socketio.on('get_users')
def send_users():
        from sqlalchemy.orm import aliased
        from sqlalchemy.sql import func
        users = db.session.query(
            User.id,
            User.username,
            User.email,
            func.coalesce(Conversation.id, None).label('conversation_id')
        ).outerjoin(
            Conversation, (User.id == Conversation.user_id)
        ).distinct()
        user_data = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'conversation_id': user.conversation_id  
            } 
            for user in users
        ]
        socketio.emit('update_user_list', user_data)

@socketio.on('new_user')
def handle_new_user():
    new_user = User()
    db.session.add(new_user)
    db.session.commit()

    socketio.emit('new_user', new_user.id)

    send_users()

    join_room(new_user.id)
    send(f'1 khách đã tham gia phòng chat!', room=new_user.id)

#Lắng nghe tin nhắn được gửi lên từ client
@socketio.on('new_message')
def handle_message(data):
    print(f"Đã nhận tin nhắn từ client: {data}", flush=True)  # Thêm flush=True
    try:
        conversation_id = data['conversation_id']
        sender_id = data['sender_id']

        message = Message()
        message.sender_id = sender_id
        message.conversation_id = conversation_id
        message.message = data['message']
        message.message_type = data['message_type']
        message.sent_at = datetime.now()
        db.session.add(message)
        db.session.commit()

        print(f"đã gửi lên server: {message.message}, "
                f"Conversation ID: {message.conversation_id}, "
                f"Sender ID: {message.sender_id}", flush=True)
        
        # Gửi tin nhắn mới về client trong cùng một cuộc trò chuyện
        conversation = Conversation.query.filter_by(id=conversation_id).first()
        if not conversation:
            print(f"Conversation {conversation_id} not found")
            return
        target_user_ids = [conversation.user_id, conversation.staff_id]
        # Emit tới từng người dùng có session ID trong danh sách
        for user_id in target_user_ids:
            sid = connected_users.get(str(user_id))
            if sid:
                socketio.emit('new_message', {
                    'message': data['message'],
                    'conversation_id': conversation_id,
                    'sender_id': sender_id,
                    'message_type': message.message_type,
                    'sent_at': message.sent_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                , to=sid
                )
        
        print(f"đã gửi về khách: {message.message}, "
                f"Conversation ID: {message.conversation_id}, "
                f"Sender ID: {message.sender_id}", flush=True)
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")

    # send_users()

@chat_bp.route('/api/messages', methods=['GET'])
def get_messages():
    conversation_id = request.args.get('conversation_id')
    if not conversation_id:
        return jsonify({'error': 'Conversation ID is required'}), 400

    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.sent_at).all()
    messages_data = [
        {
            'id': message.id,
            'sender_id': message.sender_id,
            'content': message.message,
            'message_type': message.message_type,
            'sent_at': message.sent_at.strftime('%Y-%m-%d %H:%M:%S') if message.sent_at else None
        }
        for message in messages
    ]
    return jsonify(messages_data)

@socketio.on('new_conversation')
def handle_new_conversation(data):
        print("Received data for new conversation:", data)  # Log dữ liệu nhận được

        new_conversation = Conversation(
            staff_id=data.get('staff_id'),
            user_id=data.get('user_id')
        )
        db.session.add(new_conversation)
        db.session.commit()

        conversation_data = {
            'id': new_conversation.id,
            'staff_id': new_conversation.staff_id,
            'user_id': new_conversation.user_id
        }
        socketio.emit('new_conversation', conversation_data)

        conversations_staff = get_conversations_by_staff_id(new_conversation.staff_id)
        conversations = Conversation.query.all()
        socketio.emit('update_conversations_staff', conversations_staff)
        socketio.emit('update_conversations', conversations)

@socketio.on('get_conversations')
def handle_get_conversations(data):
    staff_id = data.get('staff_id')
    conversations = get_conversations_by_staff_id(staff_id)
    socketio.emit('update_conversations', conversations)

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

@chat_bp.route('/chat')
def chat():
    return render_template('chat.html')


@chat_bp.route("/chat", methods=["POST"])
def chat_post():
    user_input = request.json.get("message", "").lower()

    # 1. Tìm câu hỏi trong bảng FAQ
    faq = Faq.query.filter(Faq.question.ilike(f"%{user_input}%")).first()
    if faq:
        return jsonify({"response": faq.answer})

    # 2. Tìm từ khóa trong bảng ChatbotResponse
    responses = ChatbotResponse.query.filter(ChatbotResponse.keyword.ilike(f"%{user_input}%")).all()
    if responses:
        # Chọn ngẫu nhiên một phản hồi
        import random
        response = random.choice(responses).response
        return jsonify({"response": response})
    
    # 3. Không tìm thấy kết quả
    return jsonify({"response": "Xin lỗi, tôi chưa hiểu câu hỏi của bạn."})
