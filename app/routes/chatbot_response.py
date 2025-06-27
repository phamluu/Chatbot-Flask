from flask import Blueprint, request
from app.services.chatbot_response_service import (
    render_chatbot_responses,
    handle_post_response,
    handle_update_response,
    handle_delete_response
)

chatbot_bp = Blueprint('chatbot_response', __name__)

@chatbot_bp.route('/chatbot-response', methods=['GET'])
def manage_chatbot_response():
    return render_chatbot_responses()

@chatbot_bp.route('/post-chatbot-response', methods=['POST'])
def post_chatbot_response():
    return handle_post_response(request)

@chatbot_bp.route('/chatbot-response/update/<int:id>', methods=['POST'])
def update_chatbot_response(id):
    return handle_update_response(id, request)

@chatbot_bp.route('/chatbot-response/delete/<int:id>', methods=['POST'])
def delete_chatbot_response(id):
    return handle_delete_response(id)
