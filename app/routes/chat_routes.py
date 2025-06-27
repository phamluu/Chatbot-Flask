from flask import Blueprint, render_template, request, jsonify
from app.models import Faq, ChatbotResponse, Message
from app.services.chat_service import get_messages_by_conversation_id
import random

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
def chat():
    return render_template('chat.html')

@chat_bp.route("/chat", methods=["POST"])
def chat_post():
    user_input = request.json.get("message", "").lower()

    # FAQ logic
    faq = Faq.query.filter(Faq.question.ilike(f"%{user_input}%")).first()
    if faq:
        return jsonify({"response": faq.answer})

    responses = ChatbotResponse.query.filter(ChatbotResponse.keyword.ilike(f"%{user_input}%")).all()
    if responses:
        return jsonify({"response": random.choice(responses).response})

    return jsonify({"response": "Xin lỗi, tôi chưa hiểu câu hỏi của bạn."})

@chat_bp.route('/api/messages', methods=['GET'])
def get_messages():
    conversation_id = request.args.get('conversation_id')
    if not conversation_id:
        return jsonify({'error': 'Conversation ID is required'}), 400
    return jsonify(get_messages_by_conversation_id(conversation_id))
