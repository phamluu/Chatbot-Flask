from functools import lru_cache
import pickle
from flask import current_app
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langdetect import detect
import os
from app.models import Intent, IntentResponse
from app.services.model_holder import model_holder


import torch.nn.functional as F


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
    # đảm bảo model đã load và được đưa về device, và ở chế độ eval
    if model_holder.model is None:
        print("🔁 Loading model...")
        model_holder.load()
    model = model_holder.model
    tokenizer = model_holder.tokenizer
    label_encoder = model_holder.label_encoder
    device = model_holder.device

    # đảm bảo model trên device và ở chế độ eval
    model.to(device)
    model.eval()

    # tokenize và chuyển tất cả tensor lên device (an toàn hơn so với inputs.to(device))
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        # Một số model trả tuple, một số trả object với .logits
        logits = outputs.logits if hasattr(outputs, "logits") else outputs[0]
        # print(f"🧩 Logits for '{text}':", logits.cpu().numpy())
        # print("Predicted index:", int(logits.argmax(dim=-1)))

        # kiểm tra logits để debug nếu cần
        # print("logits:", logits.cpu().numpy())

        # lấy xác suất và lớp dự đoán
        probs = F.softmax(logits, dim=-1)
        predicted_idx = int(probs.argmax(dim=-1).cpu().item())
        predicted_prob = float(probs.max().cpu().item())
    # trả về nhãn gốc qua LabelEncoder
    #print("Label encoder classes:", label_encoder.classes_)

    try:
        label = label_encoder.inverse_transform([predicted_idx])[0]
    except Exception as e:
        print("Lỗi khi inverse_transform label_encoder:", e)
        # fallback: in ra classes để debug
        print("label_encoder.classes_:", getattr(label_encoder, "classes_", None))
        raise
    return label

# @lru_cache(maxsize=512)
# def predict_intent_cached(text: str) -> str:
#     if model_holder.model is None:
#         print("🔁 Loading model...")
#         model_holder.load()
#     tokenizer = model_holder.tokenizer
#     model = model_holder.model
#     label_encoder = model_holder.label_encoder
#     device = model_holder.device
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
#     with torch.no_grad():
#         logits = model(**inputs).logits
#         predicted_class = logits.argmax(dim=1).item()
#     print(f"Text của bạn: {text}")
#     print(f"Ý định của bạn: {predicted_class}")
#     return label_encoder.inverse_transform([predicted_class])[0]

conversation_history = []

def generate_local_response(message: str, intent_code: str) -> str:
    from app import db  # ✅ Đặt trong hàm để không gây lỗi khi import sớm
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
    intent_info = intent_reply_map.get(intent_code)
    if intent_info is None:
        reply_text = "Xin lỗi, tôi chưa hiểu yêu cầu của bạn. Bạn có thể nói rõ hơn không?"
        return f"🧠{reply_text}"
    intent_description, response_text = intent_info
    conversation_history.append((message, intent_code))
    return f"🧠 {response_text}"

