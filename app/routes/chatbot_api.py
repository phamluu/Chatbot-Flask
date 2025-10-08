from tkinter import Message
import traceback
import uuid
from flask_security import roles_required, login_required
from flask import Blueprint, app, request, jsonify, render_template, session
from flask_wtf import CSRFProtect
from app.models import Conversation
from app.services.chat_service import get_messages_by_conversation_id, get_or_create_open_conversation, handle_new_msg
from app.services.chatbot_service import process_message
from app.extensions import csrf 
from app.extensions import socketio
from flask_socketio import emit

chatbot_api = Blueprint('chatbot_api', __name__) #endpoint: chatbot_api
admin_active = True
pending_messages = []  # lưu tin nhắn chờ admin xử lý

#User
@chatbot_api.route("/", methods=["GET"])
def chatbot_view():
    user_id = session.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id
    # 🔹 2. Lấy hoặc tạo hội thoại đang mở
    convo = get_or_create_open_conversation(user_id)
    # 🔹 3. Lấy danh sách tin nhắn trong hội thoại đó
    messages = get_messages_by_conversation_id(convo.id)
    print(f"🆔 User ID: {user_id}, Hội thoại ID: {convo.id}, Tin nhắn: {len(messages)}")
    # 🔹 5. Trả về giao diện kèm dữ liệu
    return render_template("chatbot.html", conversation=convo,messages=messages)

@csrf.exempt
@chatbot_api.route("/api/chat", methods=["POST"])
def chat_api():
    # Lưu tin nhắn vào hội thoại
    # Nếu admin thì trả lời và lưu vào hội thoại
    # Nếu admin chưa active thì chatbot trả lời
    # Giả lập trạng thái admin
    global admin_active, pending_messages

    if not request.is_json:
        #print("❌ Request không phải JSON.")
        return jsonify({"response": "⚠️ Request không phải JSON.", "source": "error"}), 400

    data = request.get_json(silent=True)
    message = data.get("message", "").strip() if data else ""
    
    user_id = session.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id
    if not message:
        #print("❌ Thiếu message.")
        return jsonify({"response": "❗ Vui lòng nhập nội dung.", "source": "error"}), 400

    #print("📩 Nhận message:", message)

    try:
        #Lưu tin nhắn người dùng vào DB
        convo = get_or_create_open_conversation(user_id)
        print("🔍 Hội thoại hiện tại:", convo.id)
        print("💬 Tin nhắn từ người dùng:", user_id)
        handle_new_msg(
            user_id,          
            convo.id,         
            message,          
            "user"            
        )

        # Gửi sự kiện real-time cho admin nếu có kết nối
        socketio.emit(
            'new_message',
            {
                "conversation_id": convo.id,
                "sender": "user",
                "message": message
            },
            to=None
        )

        # 🤖 Nếu admin chưa active → chatbot tự trả lời
        if admin_active != True:
            response_data = process_message(message)
            response_data["source"] = "bot"
            response_data["user_id"] = user_id
            return jsonify(response_data)
        #print("✅ Dữ liệu trả về từ process_message:", response_data)
    except Exception as e:
        print("❌ Lỗi trong chat_api:", e)
        traceback.print_exc()
        return jsonify({"response": "❌ Lỗi nội bộ server.", "source": "error"}), 500



# Admin
@chatbot_api.route("/chat/<int:conversation_id>")
def view_conversation(conversation_id):
    convo = Conversation.query.get_or_404(conversation_id)
    messages = get_messages_by_conversation_id(convo.id)
    return render_template("chat_detail.html", conversation=convo, messages=messages)

@csrf.exempt
@chatbot_api.route("/chat/<int:conversation_id>", methods=["POST"])
def chat_admin(conversation_id):
    # Lưu tin nhắn vào hội thoại
    # Nếu admin thì trả lời và lưu vào hội thoại
    # Nếu admin chưa active thì chatbot trả lời
    # Giả lập trạng thái admin
    global admin_active, pending_messages

    if not request.is_json:
        #print("❌ Request không phải JSON.")
        return jsonify({"response": "⚠️ Request không phải JSON.", "source": "error"}), 400

    data = request.get_json(silent=True)
    message = data.get("message", "").strip() if data else ""
    
    if not message:
        return jsonify({"response": "❗ Thiếu message.", "source": "error"}), 400

    #print("📩 Nhận message:", message)

    try:
        #Lưu tin nhắn người dùng vào DB
        handle_new_msg(
            "",          
            conversation_id,         
            message,          
            "admin"            
        )
        # Gửi sự kiện real-time cho user nếu có kết nối
        socketio.emit(
            'new_message',
            {
                "conversation_id": conversation_id,
                "sender": "admin",
                "message": message
            },
            to=None
        )

        pending_messages.append({"user_id": "", "message": message})
        return jsonify({"response": message, "source": "waiting"})
        
    except Exception as e:
        print("❌ Lỗi trong chat_api:", e)
        traceback.print_exc()
        return jsonify({"response": "❌ Lỗi nội bộ server.", "source": "error"}), 500
