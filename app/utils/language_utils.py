import pickle
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langdetect import detect
import os
from app import db
from app.models import Intent, IntentResponse

# ✅ Thiết lập thiết bị
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ✅ Biến toàn cục nhưng chưa khởi tạo model/tokenizer
MODEL_NAME = "./models/vibert4news_finetuned"
model = None
tokenizer = None
label_encoder = None

def load_model():
    """Tải model, tokenizer, và label encoder nếu chưa load."""
    global model, tokenizer, label_encoder

    if model is None or tokenizer is None or label_encoder is None:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        # Load label encoder
        with open(os.path.join(MODEL_NAME, "label_encoder.pkl"), "rb") as f:
            label_encoder = pickle.load(f)

        # Load model
        num_labels = len(label_encoder.classes_)
        model_instance = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME,
            num_labels=num_labels,
            ignore_mismatched_sizes=True
        ).to(device)

        model = model_instance

# ✅ Phát hiện ngôn ngữ
def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"

# ✅ Tách từ khóa tiếng Việt
def extract_keywords(text):
    lang = detect_language(text)
    if lang == "vi":
        from pyvi import ViTokenizer  # ✅ Trì hoãn import
        tokens = ViTokenizer.tokenize(text).split()
        return list(set([w for w in tokens if len(w) > 2]))
    return []


# ✅ Dự đoán intent từ văn bản
def predict_intent(text):
    load_model()  # ✅ Đảm bảo model/tokenizer/encoder được load
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
        predicted_class = logits.argmax(dim=1).item()
    return label_encoder.inverse_transform([predicted_class])[0]

# ✅ Sinh phản hồi từ intent
conversation_history = []

def generate_local_response(message):
    intent = predict_intent(message)  # Dự đoán intent
    #response = f"📌 Ý định của bạn là: **{intent}**.\n"
    response = f""
    intent_reply_map = {
        intent_response.intent.intent_code: intent_response.response_text
        for intent_response in IntentResponse.query.join(Intent).all()
    }
    if not intent_reply_map:
        return "🚫 Không có dữ liệu phản hồi. Vui lòng kiểm tra cơ sở dữ liệu intents/intent_responses."

    reply_text = intent_reply_map.get(
        intent,
        "Xin lỗi, tôi chưa hiểu yêu cầu của bạn. Bạn có thể nói rõ hơn không?"
    )
    # intent_reply_map = {
    #     "greeting": "Xin chào bạn! Tôi có thể giúp gì hôm nay?",
    #     "website": "Bạn đang quan tâm đến thiết kế website đúng không?",
    #     "price": "Bạn muốn hỏi về giá cả phải không?",
    #     "delivery": "Bạn đang hỏi về giao hàng?",
    #     "contact": "Bạn muốn được liên hệ lại chứ?",
    #     "other": "Tôi chưa rõ yêu cầu của bạn. Bạn có thể nói rõ hơn không?"
    # }

    conversation_history.append((message, intent))
    response += reply_text

    return response
