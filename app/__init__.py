import traceback
from flask import Flask, current_app, render_template
from app.config import Config  # 🔁 Import Config chuẩn
from app.extensions import db, migrate, socketio, security, mail, csrf  # ✅ Đã được tách ra đúng cách
from flask_security import SQLAlchemyUserDatastore
from app.models import Conversation, Message, User, Role


def create_app(use_socketio=False):
    app = Flask(__name__)
    app.debug = True

    csrf.init_app(app)
    app.config.from_object(Config)

    # Khởi tạo extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  # Khởi tạo Flask-Mail

    # Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore, register_blueprint=True)

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
    
    # Đăng ký các route liên quan đến intent
    from app.routes.intent import intent_bp as intent
    app.register_blueprint(intent)
    # end

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
    
    @app.context_processor
    def inject_conversations():
        try:
            conversations = (
                db.session.query(Conversation)
                .all()
            )
            print("Injected conversations:", conversations)
            return dict(
                sidebar_conversations=[
                    {
                        "id": c.id,
                        "user_id": c.user_id,
                        "status": c.status,
                        "last_message": (
                                lambda m: {
                                    "id": m.id,
                                    "sender_id": m.sender_id,
                                    "message": m.message,
                                    "message_type": m.message_type,
                                    "sent_at": m.sent_at.strftime("%Y-%m-%d %H:%M:%S") if m.sent_at else None
                                }
                                if m else None
                            )(
                                db.session.query(Message)
                                .filter(Message.conversation_id == c.id)
                                .order_by(Message.sent_at.desc())
                                .first()
                            )
                    }
                    for c in conversations
                ]
            )
        except Exception as e:
            current_app.logger.error(f"Lỗi khi inject_conversations: {e}")
            return dict(sidebar_conversations=[])
        finally:
            db.session.close()  
    return app

