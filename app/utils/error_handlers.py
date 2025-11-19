from flask import render_template

def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(_):
        return render_template("403.html"), 403

    @app.errorhandler(500)
    def internal(_):
        return render_template("500.html"), 500
