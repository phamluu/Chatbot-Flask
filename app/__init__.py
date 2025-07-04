from flask import Flask, render_template
from app.config import Config  # 🔁 Import Config chuẩn
from app.extensions import db, migrate, socketio, security, mail  # ✅ Đã được tách ra đúng cách
from flask_security import SQLAlchemyUserDatastore
from app.models import User, Role

# from version1 import app

# #from version1 import app
# from .config import Config

# db = SQLAlchemy()
# migrate = Migrate() 
# socketio = SocketIO()

# # Thiết lập Flask-Security
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security()  # đừng truyền app ở đây

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo extensions
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    mail.init_app(app)  # Khởi tạo Flask-Mail

    # Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore, register_blueprint=True)

    # Đăng ký các blueprint
    # Đăng ký API bảo mật
    # from app.routes.security import security_bp as security_bp_blueprint
    # app.register_blueprint(security_bp_blueprint)
    #end

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

    return app

   