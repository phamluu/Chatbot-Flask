from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from .config import Config

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
app.config.from_object(Config)

# Khởi tạo các extension
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Đăng ký các blueprint
from app.views import user_bp, staff_bp, chat_bp, faq_bp, chatbot_bp
app.register_blueprint(user_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(faq_bp)
app.register_blueprint(chatbot_bp)

# Cấu hình chạy ứng dụng Flask
if __name__ == "__main__":
    socketio.run(app, debug=True)