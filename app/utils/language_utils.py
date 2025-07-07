from functools import lru_cache
import pickle
from flask import current_app
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langdetect import detect
import os
from app.models import Intent, IntentResponse
from app.services.model_holder import model_holder

torch.set_num_threads(1)
# Thiết bị sử dụng
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Biến toàn cục cho model
MODEL_NAME = "./models/vibert4news_finetuned"
model = None
tokenizer = None
label_encoder = None


@lru_cache(maxsize=512)
def predict_intent_cached(text: str) -> str:
    if model_holder.model is None:
        print("🔁 Loading model...")
        model_holder.load()

    tokenizer = model_holder.tokenizer
    model = model_holder.model
    label_encoder = model_holder.label_encoder
    device = model_holder.device

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
        predicted_class = logits.argmax(dim=1).item()
    return label_encoder.inverse_transform([predicted_class])[0]


conversation_history = []

def generate_local_response(message: str) -> str:
    from app import db  # ✅ Đặt trong hàm để không gây lỗi khi import sớm

    intent = predict_intent_cached(message)

    with current_app.app_context():
        try:
            intent_reply_map = {
                #ir.intent.intent_code: ir.response_text
                ir.intent.intent_code: (ir.intent.description, ir.response_text)
                for ir in IntentResponse.query.join(Intent).all()
            }
        except Exception as e:
            return "🚫 Không thể truy xuất dữ liệu phản hồi. Vui lòng kiểm tra cơ sở dữ liệu."

    if not intent_reply_map:
        return "🚫 Không có dữ liệu phản hồi. Vui lòng kiểm tra cơ sở dữ liệu intents/intent_responses."
    intent_info = intent_reply_map.get(intent)
    if intent_info is None:
        reply_text = "Xin lỗi, tôi chưa hiểu yêu cầu của bạn. Bạn có thể nói rõ hơn không?"
        return f"🧠{reply_text}"
    intent_description, response_text = intent_info
    conversation_history.append((message, intent))
    return f"🧠 {response_text}"

