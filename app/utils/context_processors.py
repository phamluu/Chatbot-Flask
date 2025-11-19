from flask import current_app
from app.models import Conversation, Message
from app.extensions import db

def inject_conversations():
        try:
            # Lấy tất cả hội thoại
            conversations = db.session.query(Conversation).all()

            # Tạo danh sách dict chứa hội thoại + tin nhắn cuối cùng
            sidebar_conversations = []
            for c in conversations:
                last_message = (
                    db.session.query(Message)
                    .filter(Message.conversation_id == c.id)
                    .order_by(Message.sent_at.desc())
                    .first()
                )
                sidebar_conversations.append({
                    "id": c.id,
                    "user_id": c.user_id,
                    "status": c.status,
                    "last_message": (
                        {
                            "id": last_message.id,
                            "sender_id": last_message.sender_id,
                            "message": last_message.message,
                            "message_type": last_message.message_type,
                            "sent_at": last_message.sent_at.strftime("%Y-%m-%d %H:%M:%S") if last_message.sent_at else None
                        }
                        if last_message else None
                    )
                })
            
            # 🔽 Sắp xếp theo last_message.sent_at giảm dần
            sidebar_conversations.sort(
                key=lambda c: c["last_message"]["sent_at"] if c["last_message"] else "",
                reverse=True
            )

            print("Injected conversations:", sidebar_conversations)
            return dict(sidebar_conversations=sidebar_conversations)
        except Exception as e:
            current_app.logger.error(f"Lỗi khi inject_conversations: {e}")
            return dict(sidebar_conversations=[])
        finally:
            db.session.close()