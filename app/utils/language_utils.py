from functools import lru_cache
import pickle
from flask import current_app
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langdetect import detect
import os
from app.models import Intent, IntentResponse

torch.set_num_threads(1)
# Thiết bị sử dụng
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Biến toàn cục cho model
MODEL_NAME = "./models/vibert4news_finetuned"
model = None
tokenizer = None
label_encoder = None


def load_model():
    """Chỉ tải mô hình 1 lần duy nhất khi app khởi tạo"""
    global model, tokenizer, label_encoder

    if model is not None and tokenizer is not None and label_encoder is not None:
        return  # ✅ Đã load rồi thì bỏ qua

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    with open(os.path.join(MODEL_NAME, "label_encoder.pkl"), "rb") as f:
        label_encoder = pickle.load(f)

    num_labels = len(label_encoder.classes_)
    model_instance = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels,
        ignore_mismatched_sizes=True
    ).to(device)

    model = model_instance


def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"


def extract_keywords(text):
    lang = detect_language(text)
    if lang == "vi":
        from pyvi import ViTokenizer
        tokens = ViTokenizer.tokenize(text).split()
        return list(set([w for w in tokens if len(w) > 2]))
    return []


def _predict_intent(text):
    global model, tokenizer, label_encoder
    if model is None or tokenizer is None or label_encoder is None:
        print("🔁 Model chưa load — gọi lại load_model trong _predict_intent")
        load_model()

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
        predicted_class = logits.argmax(dim=1).item()
    return label_encoder.inverse_transform([predicted_class])[0]

@lru_cache(maxsize=512)
def predict_intent_cached(text: str) -> str:
    global model, tokenizer, label_encoder
    if model is None or tokenizer is None or label_encoder is None:
        print("🔁 Model chưa load — thực hiện load_model()...")
        load_model()
    return _predict_intent(text)



conversation_history = []

def generate_local_response(message: str) -> str:
    from app import db  # ✅ Đặt trong hàm để không gây lỗi khi import sớm

    intent = predict_intent_cached(message)

    with current_app.app_context():
        try:
            intent_reply_map = {
                ir.intent.intent_code: ir.response_text
                for ir in IntentResponse.query.join(Intent).all()
            }
        except Exception as e:
            return "🚫 Không thể truy xuất dữ liệu phản hồi. Vui lòng kiểm tra cơ sở dữ liệu."

    if not intent_reply_map:
        return "🚫 Không có dữ liệu phản hồi. Vui lòng kiểm tra cơ sở dữ liệu intents/intent_responses."

    reply_text = intent_reply_map.get(
        intent,
        "Xin lỗi, tôi chưa hiểu yêu cầu của bạn. Bạn có thể nói rõ hơn không?"
    )

    conversation_history.append((message, intent))
    return reply_text
