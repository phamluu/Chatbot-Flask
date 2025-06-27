from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from .config import Config

db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo extensions
    db.init_app(app)
    socketio.init_app(app)

    # Đăng ký các blueprint

    from app.routes.chatbot_response import chatbot_bp as chatbot
    app.register_blueprint(chatbot)
    from app.routes.faq import faq_bp as faq
    app.register_blueprint(faq)

    # Đăng ký API nhân viên
    from app.routes.staff import staff_bp as staff
    app.register_blueprint(staff)

    # Đăng ký API người dùng
    from app.routes.user import user_bp as user
    app.register_blueprint(user)

    # Đăng ký API chatbot riêng biệt
    from app.routes.chatbot_api import chatbot_api
    app.register_blueprint(chatbot_api)
    
    from app.routes.chat_routes import chat_bp as chat
    app.register_blueprint(chat)

    return app
