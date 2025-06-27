from flask import Blueprint, request, jsonify, render_template
from app.services.chatbot_service import process_message

chatbot_api = Blueprint('chatbot_api', __name__)

@chatbot_api.route("/chatbot", methods=["GET"])
def chatbot_view():
    return render_template("chatbot.html")

@chatbot_api.route("/api/chat", methods=["POST"])
def chat_api():
    if not request.is_json:
        return jsonify({"response": "⚠️ Request không phải JSON.", "source": "error"})

    data = request.get_json(silent=True)
    message = data.get("message", "").strip() if data else ""
    if not message:
        return jsonify({"response": "❗ Vui lòng nhập nội dung.", "source": "error"}), 400

    response_data = process_message(message)
    return jsonify(response_data)
