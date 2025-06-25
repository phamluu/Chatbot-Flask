from flask import Blueprint, json, request, jsonify
import os
import requests
import spacy
import markdown2
from dotenv import load_dotenv

load_dotenv()

chatbot_api = Blueprint('chatbot_api', __name__)

# URL Web API để tìm kiếm theo từ khóa
WEB_API_URL = "https://support.inanhonglen.com/Ask/Ask"

# OpenRouter
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_TOKEN = os.getenv("openrouter_key")

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "HTTP-Referer": "http://localhost",  # Hoặc tên miền thật khi deploy
    "Content-Type": "application/json"
}

# Load spaCy
try:
    nlp = spacy.load("./models/en_core_web_sm")
    print("✅ spaCy model đã sẵn sàng.")
except Exception as e:
    print(f"❌ spaCy load error: {e}")
    nlp = None


def extract_keywords(text):
    """
    Trích xuất từ khóa cơ bản bằng cách lọc noun, proper noun, hoặc tên riêng
    """
    if not nlp:
        return []
    doc = nlp(text)
    keywords = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN") and not token.is_stop]
    return list(set(keywords))  # loại bỏ trùng


def fetch_data_from_web(keywords):
    """
    Gửi danh sách từ khóa đến Web API để lấy dữ liệu liên quan
    """
    try:
        response = requests.post(WEB_API_URL, json={"keywords": keywords}, timeout=10)
        if response.status_code == 200:
            return response.text  # plain text hoặc JSON chuỗi
        print(f"⚠️ Web API lỗi: {response.status_code} - {response.text}")
        return ""
    except Exception as e:
        print(f"❌ Lỗi gọi Web API: {e}")
        return ""


def generate_online_response(contextual_prompt):
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": contextual_prompt}]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        print(f"⚠️ OpenRouter lỗi: {response.text}")
        return None
    except Exception as e:
        print(f"❌ OpenRouter exception: {e}")
        return None


def generate_local_response(message):
    if not nlp:
        return "⚠️ spaCy chưa sẵn sàng."
    doc = nlp(message)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    if entities:
        return f"📌 spaCy phát hiện entities: {entities}"
    return "🤖 Không tìm thấy entity nào."

@chatbot_api.route("/chatbot", methods=["GET"])
def chatbot_view():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chatbot</title>
        <style>
            body { font-family: sans-serif; padding: 2em; background: #f9f9f9; }
            #result { margin-top: 1em; padding: 1em; background: #fff; border: 1px solid #ccc; }
            textarea, input[type="text"] { width: 100%; padding: 0.5em; margin-top: 0.5em; }
            button { padding: 0.6em 1.2em; margin-top: 1em; }
        </style>
    </head>
    <body>
        <h1>💬 Chatbot Demo</h1>
        <form id="chat-form">
            <label for="message">Nhập nội dung:</label>
            <input type="text" id="message" name="message" placeholder="Ví dụ: Tôi muốn đặt thiệp cưới..." required />
            <button type="submit">Gửi</button>
        </form>
        <div id="result"></div>

        <script>
            const form = document.getElementById('chat-form');
            const resultDiv = document.getElementById('result');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const message = document.getElementById('message').value;
                resultDiv.innerHTML = "⏳ Đang xử lý...";

                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message })
                    });

                    const data = await res.json();
                    resultDiv.innerHTML = `<h3>Phản hồi:</h3><div>${data.html || data.response}</div>`;
                } catch (err) {
                    resultDiv.innerHTML = "❌ Lỗi khi gửi yêu cầu.";
                }
            });
        </script>
    </body>
    </html>
    """

@chatbot_api.route("/api/chat", methods=["POST"])
def chat_api():
    if not request.is_json:
        return jsonify({"response": "⚠️ Request không phải JSON.", "source": "error"})

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"response": "⚠️ Không đọc được JSON.", "source": "error"})

    message = data.get("message", "").strip()
    if not message:
        return jsonify({"response": "❗ Vui lòng nhập nội dung.", "source": "error"}), 400

    # 🔍 Bước 1: Tách từ khóa từ tin nhắn
    keywords = extract_keywords(message)
    print("🔑 Từ khóa trích xuất:", keywords)

    # 🌐 Bước 2: Gọi Web API lấy dữ liệu liên quan
    reference_data = fetch_data_from_web(keywords)

    # 🧠 Bước 3: Kết hợp thành prompt ngữ cảnh
    prompt = f"""Người dùng hỏi: "{message}"

Dưới đây là thông tin dữ liệu liên quan được hệ thống tìm thấy:
{reference_data}

Hãy trả lời người dùng một cách tự nhiên và hữu ích dựa trên thông tin ở trên."""

    # 🤖 Bước 4: Gửi vào OpenRouter để sinh phản hồi
    result = generate_online_response(prompt)
    source = "openrouter"

    # 🔁 Fallback nếu OpenRouter không phản hồi
    if result is None:
        result = generate_local_response(message)
        source = "local"

    html = markdown2.markdown(result)

    return jsonify({
        "response": result,
        "source": source,
        "html": html
    })
