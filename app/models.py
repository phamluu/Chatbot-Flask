from app import db  
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
# Vai trò người dùng (admin, user, editor,...)
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

# Bảng liên kết giữa user và role
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

# Người dùng
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)

    # 🛠 Bắt buộc từ Flask-Security >= 4.0.0
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Quan hệ với Role
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    
class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    staff_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=True)
    def __repr__(self):
        return f'<Conversation {self.id}>'

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, nullable=True)
    sender_id = db.Column(db.Integer, nullable=True)
    message = db.Column(db.Text, nullable=True)
    message_type = db.Column(db.String(50), nullable=True)
    sent_at = db.Column(db.TIMESTAMP, nullable=True)
    
class Intent(db.Model):
    __tablename__ = 'intents'
    id = db.Column(db.Integer, primary_key=True)
    intent_code = db.Column(db.String(100), nullable=False)
    intent_name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

    inputs = relationship('IntentInput', back_populates='intent', cascade='all, delete-orphan')
    responses = relationship('IntentResponse', back_populates='intent', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Intent {self.intent_code}>'

class IntentInput(db.Model):
    __tablename__ = 'intent_inputs'
    id = db.Column(db.Integer, primary_key=True)
    intent_id = db.Column(db.Integer, db.ForeignKey('intents.id'), nullable=False)  # ✅ thêm ForeignKey
    utterance = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=True)

    intent = relationship('Intent', back_populates='inputs')

    def __repr__(self):
        return f'<IntentInput {self.utterance[:30]}>'

class IntentResponse(db.Model):
    __tablename__ = 'intent_responses'
    id = db.Column(db.Integer, primary_key=True)
    intent_id = db.Column(db.Integer, db.ForeignKey('intents.id'), nullable=False)  # ✅ thêm ForeignKey
    response_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=True)

    intent = relationship('Intent', back_populates='responses')

    def __repr__(self):
        return f'<IntentResponse {self.response_text[:30]}>'
