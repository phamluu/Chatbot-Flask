import traceback
from flask_security import roles_required, login_required
from flask import Blueprint, app, request, jsonify, render_template
from flask_wtf import CSRFProtect
from app.services.chatbot_service import process_message
from app.extensions import csrf 

chatbot_api = Blueprint('chatbot_api', __name__) #endpoint: chatbot_api


@chatbot_api.route("/", methods=["GET"])
def chatbot_view():
    return render_template("chatbot.html")

@csrf.exempt
@chatbot_api.route("/api/chat", methods=["POST"])
def chat_api():
    if not request.is_json:
        #print("❌ Request không phải JSON.")
        return jsonify({"response": "⚠️ Request không phải JSON.", "source": "error"}), 400

    data = request.get_json(silent=True)
    message = data.get("message", "").strip() if data else ""
    if not message:
        #print("❌ Thiếu message.")
        return jsonify({"response": "❗ Vui lòng nhập nội dung.", "source": "error"}), 400

    #print("📩 Nhận message:", message)

    try:
        response_data = process_message(message)
        #print("✅ Dữ liệu trả về từ process_message:", response_data)
        return jsonify(response_data)
    except Exception as e:
        print("❌ Lỗi trong chat_api:", e)
        traceback.print_exc()
        return jsonify({"response": "❌ Lỗi nội bộ server.", "source": "error"}), 500

