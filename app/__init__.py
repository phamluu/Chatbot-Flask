from flask import Flask
from app.config import Config
from app.extensions import db, migrate, mail, socketio, security, csrf
from flask_security import SQLAlchemyUserDatastore
from app.models import User, Role

from app.routes import register_routes
from app.utils.error_handlers import register_error_handlers
from app.utils.context_processors import inject_conversations


def create_app(use_socketio=False):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Security
    user_store = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_store, register_blueprint=True)

    if use_socketio:
        socketio.init_app(app)

    # Register Routes
    register_routes(app)

    # Error Handlers
    register_error_handlers(app)

    # Context Processors
    app.context_processor(inject_conversations)

    return app
