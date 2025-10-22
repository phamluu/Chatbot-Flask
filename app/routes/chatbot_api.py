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
admin_active = False
active_sessions = {}
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

        # 🔹 Xử lý tin nhắn dựa trên trạng thái admin
        # 🤖 Nếu admin chưa active → chatbot tự trả lời
        if not admin_active:
            response_data = process_message(message)
            handle_new_msg("", convo.id,  response_data["response"], "bot")
            socketio.emit(
                'new_message',
                {
                    "conversation_id": convo.id,
                    "sender": "bot",
                    "message": response_data["response"]
                },
                to=None
            )
            return jsonify(response_data)
        else:
            # admin đang online → chờ admin phản hồi
            pending_messages.append({"conversation_id": convo.id, "message": message})
            return jsonify({
                "response": "Tin nhắn đã gửi đến admin, vui lòng chờ phản hồi.",
                "source": "waiting"
            })
    except Exception as e:
        print("❌ Lỗi trong chat_api:", e)
        traceback.print_exc()
        return jsonify({"response": "❌ Lỗi nội bộ server.", "source": "error"}), 500



# Admin
@chatbot_api.route("/chat/<int:conversation_id>")
def view_conversation(conversation_id):
    convo = Conversation.query.get_or_404(conversation_id)
    messages = get_messages_by_conversation_id(convo.id)
    admin_active = session.get(f"admin_active_{conversation_id}", False)
    #tạm
    #key = f"admin_active_{conversation_id}"
    print(f"session hội thoại 1: 🔄 {admin_active}")
    #end tạm
    return render_template("chat_detail.html", conversation=convo, messages=messages, admin_active=admin_active)

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

# bot chuyển trạng thái admin active hay không active
@csrf.exempt
@chatbot_api.route("/chat/bot/<int:conversation_id>", methods=["POST"])
def chat_bot(conversation_id):
    global active_sessions, pending_messages
    if not request.is_json:
        return jsonify({"response": "⚠️ Request không phải JSON.", "source": "error"}), 400
    data = request.get_json(silent=True)
    status = data.get("message", "").strip() if data else ""
    if not status:
        return jsonify({"response": "❗ Thiếu message.", "source": "error"}), 400
    try:
        # 🔹 Xử lý thay đổi trạng thái
        if status == "active":
            active_sessions[conversation_id] = True
            session[f"admin_active_{conversation_id}"] = True 
            message = "Admin đã tham gia cuộc trò chuyện."
        elif status == "inactive":
            active_sessions[conversation_id] = False
            session[f"admin_active_{conversation_id}"] = False
            message = "Admin đã kết thúc cuộc trò chuyện."
        

        handle_new_msg("", conversation_id, message, "bot")
        socketio.emit(
            "new_message",
            {
                "conversation_id": conversation_id,
                "sender": "bot",
                "message": message
            },
            to=None
        )

        # 🔹 Gửi thêm sự kiện riêng để sidebar cập nhật trạng thái hội thoại
        # socketio.emit(
        #     "conversation_status",
        #     {
        #         "conversation_id": conversation_id,
        #         "status": "active" if active_sessions.get(conversation_id) else "inactive"
        #     },
        #     broadcast=True
        # )

        pending_messages.append({"user_id": "", "message": message})

        return jsonify({"response": message, "source": "status_updated"})
        
    except Exception as e:
        print("❌ Lỗi trong chat_api:", e)
        traceback.print_exc()
        return jsonify({"response": "❌ Lỗi nội bộ server.", "source": "error"}), 500
