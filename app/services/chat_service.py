from app.models import Message, User, Conversation
from app import db
from datetime import datetime
from flask_socketio import emit

def get_messages_by_conversation_id(convo_id):
    messages = (
        Message.query
        .filter_by(conversation_id=convo_id)
        .order_by(Message.sent_at.asc())
        .all()
    )

    return [
        {
            "id": m.id,
            "sender_id": m.sender_id or "Ẩn danh",
            "content": m.message or "",
            "message_type": m.message_type or "user",
            "sent_at": (
                m.sent_at.strftime("%Y-%m-%d %H:%M:%S")
                if m.sent_at else ""
            ),
        }
        for m in messages
    ]


def get_users_data():
    from sqlalchemy.sql import func
    users = db.session.query(
        User.id, User.username, User.email,
        func.coalesce(Conversation.id, None).label('conversation_id')
    ).outerjoin(Conversation, User.id == Conversation.user_id).distinct()
    return [{
        'id': u.id, 'username': u.username, 'email': u.email,
        'conversation_id': u.conversation_id
    } for u in users]

def handle_new_msg(sender_id, conversation_id, message, message_type):
    msg = Message(
        sender_id=sender_id,
        conversation_id=conversation_id,
        message=message,
        message_type=message_type,
        sent_at=datetime.now()
    )
    db.session.add(msg)
    db.session.commit()

    # convo = Conversation.query.get(conversation_id)
    # if convo:
    #     for uid in [convo.user_id, convo.staff_id]:
    #         sid = connected_users.get(str(uid))
    #         if sid:
    #             emit('new_message', {
    #                 'message': msg.message,
    #                 'conversation_id': msg.conversation_id,
    #                 'sender_id': msg.sender_id,
    #                 'message_type': msg.message_type,
    #                 'sent_at': msg.sent_at.strftime('%Y-%m-%d %H:%M:%S')
    #             }, to=sid)

def create_conversation(data):
    convo = Conversation(staff_id=data['staff_id'], user_id=data['user_id'])
    db.session.add(convo)
    db.session.commit()
    return {
        'id': convo.id,
        'staff_id': convo.staff_id,
        'user_id': convo.user_id
    }

def get_or_create_open_conversation(user_id):
    conv = Conversation.query.filter_by(user_id=user_id, status="open").first()
    if not conv:
        conv = Conversation(user_id=user_id, status="open")
        db.session.add(conv)
        db.session.commit()
    return conv
