import os
# from tkinter import Message
import requests
import markdown2
from dotenv import load_dotenv
from sqlalchemy import desc
from app.routes import intent
from app.utils.language_utils import  generate_local_response, predict_intent_cached
from app.models import Intent, Message

load_dotenv()

WEB_API_URL = "https://support.inanhonglen.com/Ask/Ask"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_TOKEN = os.getenv("openrouter_key")

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "HTTP-Referer": "http://localhost",
    "Content-Type": "application/json"
}

def fetch_data_from_web(keywords):
    try:
        response = requests.post(WEB_API_URL, json={"keywords": keywords}, timeout=10)
        return response.text if response.status_code == 200 else ""
    except Exception as e:
        #print(f"❌ Web API lỗi: {e}")
        return ""

def generate_online_response(prompt):
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)
        return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else None
    except Exception as e:
        #print(f"❌ OpenRouter lỗi: {e}")
        return None

def process_message(message, conversation_id):
    history = get_conversation_history(conversation_id, limit=5)
    context_text = " ".join([f"[User]: {m.message}" if m.message_type=="user" else f"[Bot]: {m.message}" for m in history])
    input_text = f"{context_text} [User]: {message}"
    input_text = input_text[-1000:]  # giữ tối đa 1000 ký tự
    # Sử dụng mô hình nội bộ tiếng Việt (microBERT)
    intent_code = predict_intent_cached(input_text)
    known_intents = get_known_intents()
    if intent_code in known_intents:
        response = generate_local_response(message, intent_code)
        source = "microbert"
    else:
        response = generate_online_response(message)
        source = "openrouter"
    html = markdown2.markdown(response)
    return {
        "intent_code": intent_code,
        "response": response,
        "source": source,
        "html": html
    }

# Học lịch sử để cải thiện phản hồi
def get_conversation_history(conversation_id, limit=5):
    messages = (
        Message.query
        .filter_by(conversation_id=conversation_id, message_type="user")
        .order_by(desc(Message.sent_at))
        .limit(limit)
        .all()
    )
    return list(reversed(messages))

def get_known_intents():
    """Lấy danh sách intent_code có sẵn trong CSDL (có phản hồi mẫu)."""
    try:
        return [intent.intent_code for intent in Intent.query.all()]
    except Exception as e:
        print("⚠️ Không thể truy xuất danh sách known intents:", e)
        return []