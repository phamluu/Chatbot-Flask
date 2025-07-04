from flask_security import roles_required, login_required
from flask import Blueprint, request, jsonify, render_template
from app.services.chatbot_service import process_message
from app.services.intent_service import (
    handle_delete_intent,
    handle_delete_intent_response,
    handle_manage_intent,
    handle_manage_intent_input,
    handle_manage_intent_response, 
    handle_update_intent,
    handle_update_intent_input,
    handle_update_intent_response
    ) 

chatbot_api = Blueprint('chatbot_api', __name__) #endpoint: chatbot_api

# intent management routes
@chatbot_api.route("/intent", methods=['GET', 'POST'])
@roles_required('admin')
def manage_intent():
    return handle_manage_intent(request)
@chatbot_api.route('/intent/update/<int:id>', methods=['POST'])
@roles_required('admin')
def update_intent(id):
    return handle_update_intent(id, request)
@chatbot_api.route('/intent/delete/<int:id>', methods=['POST'])
@roles_required('admin')
def delete_intent(id):
    return handle_delete_intent(id)
#end

# intent input management routes
@chatbot_api.route("/intent_input/<int:intent_id>", methods=['GET', 'POST'])
@roles_required('admin')
def manage_intent_input(intent_id):
    return handle_manage_intent_input(request, intent_id)

@chatbot_api.route('/intent_input/update/<int:id>', methods=['POST'])
@roles_required('admin')
def update_intent_input(id):
    return handle_update_intent_input(id, request)

@chatbot_api.route('/intent_input/delete/<int:id>', methods=['POST'])
@roles_required('admin')
def delete_intent_input(id):
    return handle_delete_intent(id)
#end

# intent response management routes
@chatbot_api.route("/intent_response/<int:intent_id>", methods=["GET", "POST"])
@roles_required('admin')
def manage_intent_responses(intent_id):
    return handle_manage_intent_response(request, intent_id)

@chatbot_api.route('/intent_response/update/<int:id>', methods=['POST'])
@roles_required('admin')
def update_intent_responses(id):
    return handle_update_intent_response(id, request)
    
@chatbot_api.route('/intent_response/delete/<int:id>', methods=['POST'])
@roles_required('admin')
def delete_intent_responses(id):
    return handle_delete_intent_response(id)
#end

@chatbot_api.route("/chatbot", methods=["GET"])
def chatbot_view():
    return render_template("chatbot.html")

@chatbot_api.route("/api/chat", methods=["POST"])
def chat_api():
    if not request.is_json:
        print("❌ Request không phải JSON.")
        return jsonify({"response": "⚠️ Request không phải JSON.", "source": "error"})

    data = request.get_json(silent=True)
    message = data.get("message", "").strip() if data else ""
    if not message:
        print("❌ Thiếu message.")
        return jsonify({"response": "❗ Vui lòng nhập nội dung.", "source": "error"}), 400

    print("📩 Nhận message:", message)

    try:
        response_data = process_message(message)
        print("✅ Dữ liệu trả về từ process_message:", response_data)
        return jsonify(response_data)
    except Exception as e:
        print("❌ Lỗi trong chat_api:", e)
        return jsonify({"response": "❌ Lỗi nội bộ server.", "source": "error"}), 500

