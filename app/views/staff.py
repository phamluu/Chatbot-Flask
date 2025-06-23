# app/views/staff.py
from flask import Blueprint, render_template
from app.models import User
from app.models import Conversation

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff')
def staff():
    conversations = Conversation.query.all()
    conversations_staff = get_conversations_by_staff_id(42)
    return render_template('staff.html', conversations_staff=conversations_staff, conversations = conversations)


def get_conversations_by_staff_id(staff_id):
    conversations = Conversation.query.filter_by(staff_id=staff_id).all()
    result = [{
        'id': convo.id,
        'user_id': convo.user_id,
    } for convo in conversations]
    return result

