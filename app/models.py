from app import db  
from sqlalchemy.orm import relationship
from datetime import datetime
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    user_type = db.Column(db.String(50), nullable=False)
    def __repr__(self):
        return f'<User {self.name}>'


    
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
    
class Faq(db.Model):
    __tablename__ = 'faq'
    id = db.Column(db.Integer, primary_key=True)   	
    answer = db.Column(db.Text, nullable=True)
    question = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=True)

class ChatbotResponse(db.Model):
    __tablename__ = 'chatbot_responses'
    id = db.Column(db.Integer, primary_key=True)  
    keyword = db.Column(db.String(255), nullable=True)
    response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=True)

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
