def register_routes(app):
    from app.routes.chat_routes import admin_route
    from app.routes.dashboard import dashboard_bp
    from app.routes.staff import staff_bp
    from app.routes.user import user_bp
    from app.routes.chatbot_api import chatbot_api
    from app.routes.intent import intent_bp
    from app.routes.test import test_bp

    app.register_blueprint(admin_route)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(chatbot_api)
    app.register_blueprint(intent_bp)
    app.register_blueprint(test_bp)