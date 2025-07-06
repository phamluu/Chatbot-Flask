# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_security import Security
from flask_mail import Mail
# app/extensions.py
from flask_wtf import CSRFProtect

csrf = CSRFProtect()

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
security = Security()
mail = Mail()