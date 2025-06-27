from flask import render_template
from app.models import Conversation

def get_conversations_by_staff_id(staff_id):
    conversations = Conversation.query.filter_by(staff_id=staff_id).all()
    return [{
        'id': convo.id,
        'user_id': convo.user_id,
    } for convo in conversations]

def render_staff_page():
    conversations = Conversation.query.all()
    conversations_staff = get_conversations_by_staff_id(42)
    return render_template('staff.html',
                           conversations=conversations,
                           conversations_staff=conversations_staff)
