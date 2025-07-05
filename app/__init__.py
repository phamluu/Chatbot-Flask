import traceback
from flask import Flask, render_template
from app.config import Config  # 🔁 Import Config chuẩn
from app.extensions import db, migrate, socketio, security, mail  # ✅ Đã được tách ra đúng cách
from flask_security import SQLAlchemyUserDatastore
from app.models import User, Role

def create_app(use_socketio=False):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  # Khởi tạo Flask-Mail

    # Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore, register_blueprint=True)

    from flask_wtf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)

    # ONLY INIT socketio WHEN NOT USING WSGI (dev mode)
    if use_socketio:
        socketio.init_app(app)

    # đăng ký dashboard blueprint
    from app.routes.dashboard import dashboard_bp as dashboard
    app.register_blueprint(dashboard)
    # end

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

    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        return f"""
        <h1>500 Internal Server Error</h1>
        <pre>{traceback.format_exc()}</pre>
        """, 500
    return app

   