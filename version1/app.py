from flask import Flask, render_template, request
from flask_socketio import SocketIO, send

app = Flask(__name__)
socketio = SocketIO(app)

clients = {}
staff_joined = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/staff')
def staff():
    return render_template('bot.html')

# Khi một người dùng kết nối, lưu lại socket_id
@socketio.on('connect')
def handle_connect():
    print("Client connected:", request.sid)
    clients[request.sid] = None  # Lưu socket id vào danh sách clients

# Lắng nghe sự kiện 'message' và truyền tin nhắn đến tất cả client, ngoại trừ người gửi
@socketio.on('message')
def handle_message(message):
    global staff_joined

    # Kiểm tra nếu message là một đối tượng có 'message' và 'sender'
    if isinstance(message, dict) and 'message' in message and 'sender' in message:
        # Nếu nhân viên chưa tham gia và khách gửi tin nhắn
        if not staff_joined and message['sender'] == 'customer':
            # Trả lời tự động từ bot cho khách hàng
            auto_reply = "Tôi là Hồng Vân Bot: Cảm ơn bạn đã liên hệ, chúng tôi sẽ kết nối với bạn ngay."
            send({"message": auto_reply, "sender": "bot"}, broadcast=True)
        else:
            # Chỉ gửi tin nhắn cho tất cả người dùng trừ người gửi
            for client_id in clients:
                # Không gửi lại tin nhắn cho chính người gửi
                if client_id != request.sid:
                    socketio.emit('message', {"message": message['message'], "sender": message['sender']}, room=client_id)

# Khi nhân viên tham gia vào chat, thay đổi trạng thái
@socketio.on('staff_join')
def staff_join():
    global staff_joined
    staff_joined = True
    # Thông báo cho khách hàng về sự tham gia của nhân viên
    for client_id in clients:
        if clients[client_id] != 'staff':  # Gửi thông báo cho khách hàng
            socketio.emit('message', {"message": "Nhân viên đã tham gia vào cuộc trò chuyện. Bạn có thể bắt đầu trò chuyện với họ.", "sender": "bot"}, room=client_id)
    print("Nhân viên đã tham gia")

# Khi một người dùng ngắt kết nối, xóa khỏi danh sách
@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected:", request.sid)
    if request.sid in clients:
        del clients[request.sid]

if __name__ == '__main__':
    socketio.run(app, debug=True)