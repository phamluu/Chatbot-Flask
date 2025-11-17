#from tkinter import Message
import traceback
import uuid
from flask_login import current_user
from flask_security import roles_required, login_required
from flask import Blueprint, app, request, jsonify, render_template, session
from flask_wtf import CSRFProtect
from app.models import Conversation
from app.services.chat_service import get_messages_by_conversation_id, get_or_create_open_conversation, handle_delete_conversation, handle_new_msg, is_staff_active_in_conversation, update_conversation_staff
from app.services.chatbot_service import process_message
from app.extensions import csrf 
from app.extensions import socketio
from flask_socketio import emit

chatbot_api = Blueprint('chatbot_api', __name__) #endpoint: chatbot_api
# admin_active = False
active_sessions = {}
pending_messages = []  # lưu tin nhắn chờ admin xử lý

#User
@chatbot_api.route("/", methods=["GET"])
def chatbot_view():
    user_id = session.get("user_id") # id của người dùng được tạo ngẫu nhiên và lưu trong session
    if not user_id:
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id
    # 🔹 2. Lấy hoặc tạo hội thoại đang mở
    conversation_id = session.get("conversation_id")
    if conversation_id:
        convo = Conversation.query.get(conversation_id)
        if not convo:
            convo = get_or_create_open_conversation(user_id)
            session["conversation_id"] = convo.id
    else:
        convo = get_or_create_open_conversation(user_id)
        session["conversation_id"] = convo.id
    messages = get_messages_by_conversation_id(convo.id)
    # print("=== SESSION HIỆN TẠI ===")
    # print(dict(session))
    return render_template("chatbot.html", conversation=convo, messages=messages)

# gửi tin nhắn
@chatbot_api.route("/api/send", methods=["POST"])
def send_message():
    if not request.is_json:
        return jsonify({"response": "⚠️ Request không phải JSON.", "source": "error"}), 400
    data = request.get_json(silent=True)
    message = data.get("message", "").strip() if data else ""
    conversation_id = data.get("conversation_id")
    user_id = session.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id
    if not message:
        return jsonify({"response": "❗ Vui lòng nhập nội dung.", "source": "error"}), 400
    try:
        #convo = get_or_create_open_conversation(user_id)
        handle_new_msg(
            user_id,
            conversation_id,
            "",
            message,
            "user"
        )
        socketio.emit(
            'new_message',
            {
                "conversation_id": conversation_id,
                "sender": "user",
                "message": message
            },
            to=None
        )
        return jsonify({
            "response": "✅ Tin nhắn đã gửi thành công.",
            "conversation_id": conversation_id,
            "source": "success"
        }), 200
    except Exception as e:
        print("❌ Lỗi trong chat_api:", e)
        traceback.print_exc()
        return jsonify({"response": "❌ Lỗi nội bộ server.", "source": "error"}), 500

# Kiểm tra trạng thái admin để phản hồi tự động nếu cần
@chatbot_api.route("/api/response", methods=["POST"])
def response_message():
    global pending_messages
    if not request.is_json:
        #print("❌ Request không phải JSON.")
        return jsonify({"response": "⚠️ Request không phải JSON.", "source": "error"}), 400
    data = request.get_json(silent=True)
    message = data.get("message", "").strip() if data else ""
    conversation_id = data.get("conversation_id")
    user_id = session.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id
    if not message:
        #print("❌ Thiếu message.")
        return jsonify({"response": "❗ Vui lòng nhập nội dung.", "source": "error"}), 400
    try:
        #convo = get_or_create_open_conversation(user_id)
        # Kiểm tra có nhân viên trong hội thoại không
        admin_active = is_staff_active_in_conversation(conversation_id)
        if not admin_active:
                response_data = process_message(message, conversation_id)
                handle_new_msg("", conversation_id, response_data["intent_code"], response_data["response"], "bot")
                socketio.emit(
                    'new_message',
                    {
                        "conversation_id": conversation_id,
                        "sender": "bot",
                        "message": response_data["response"]
                    },
                    to=None
                )
                return jsonify(response_data)
        else:
            # admin đang online → chờ admin phản hồi
            pending_messages.append({"conversation_id": conversation_id, "message": message})
            return jsonify({
                "response": "Tin nhắn đã gửi đến admin, vui lòng chờ phản hồi.",
                "source": "waiting"
            })
    except Exception as e:
        print("❌ Lỗi trong chat_api:", e)
        traceback.print_exc()
        return jsonify({"response": "❌ Lỗi nội bộ server.", "source": "error"}), 500


# Admin
# Admin xem chi tiết hội thoại
@chatbot_api.route("/chat/<int:conversation_id>")
def view_conversation(conversation_id):
    convo = Conversation.query.get_or_404(conversation_id)
    messages = get_messages_by_conversation_id(convo.id)
    #admin_active = session.get(f"admin_active_{conversation_id}", False)
    admin_active = is_staff_active_in_conversation(convo.id)
    #tạm
    #key = f"admin_active_{conversation_id}"
    print(f"session hội thoại 1: 🔄 {admin_active}")
    #end tạm
    return render_template("chat_detail.html", conversation=convo, messages=messages, admin_active=admin_active)

# Admin gửi tin nhắn trong hội thoại
@csrf.exempt
@chatbot_api.route("/chat/<int:conversation_id>", methods=["POST"])
def chat_admin(conversation_id):
    # Lưu tin nhắn vào hội thoại
    # Nếu admin thì trả lời và lưu vào hội thoại
    # Nếu admin chưa active thì chatbot trả lời
    # Giả lập trạng thái admin
    global pending_messages

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
            "",          
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
    global pending_messages
    if not request.is_json:
        return jsonify({"response": "⚠️ Request không phải JSON.", "source": "error"}), 400
    data = request.get_json(silent=True)
    status = data.get("message", "").strip() if data else ""
    if not status:
        return jsonify({"response": "❗ Thiếu message.", "source": "error"}), 400
    try:
        # 🔹 Xử lý thay đổi trạng thái
        if status == "active":
            # Cập nhật id nhân viên vào database
            # Lấy iduser đang đăng nhập
            staff_id = current_user.id
            update_conversation_staff(conversation_id, staff_id)
            active_sessions[conversation_id] = True
            session[f"admin_active_{conversation_id}"] = True 
            message = "Admin đã tham gia cuộc trò chuyện."
        elif status == "inactive":
            update_conversation_staff(conversation_id, None)
            active_sessions[conversation_id] = False
            session[f"admin_active_{conversation_id}"] = False
            message = "Admin đã kết thúc cuộc trò chuyện."
        

        handle_new_msg("", conversation_id, "", message, "bot")
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

# Admin xóa hội thoại
@chatbot_api.route('/api/conversation/<int:conversation_id>', methods=['DELETE'])
@csrf.exempt
def delete_conversation(conversation_id):
    convo = Conversation.query.get(conversation_id)
    if not convo:
        return jsonify({"error": "Conversation not found"}), 404
    handle_delete_conversation(conversation_id)

    # nếu dùng socket để broadcast thay đổi, emit event ở đây (tuỳ cách triển khai)
    # socketio.emit('conversation_deleted', {'conversation_id': conversation_id}, broadcast=True)

    return jsonify({"message": "Conversation deleted"}), 200