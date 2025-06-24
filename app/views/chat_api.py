from flask import Blueprint, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

chatbot_api = Blueprint('chatbot_api', __name__)

# Dùng OpenRouter API
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_TOKEN = os.getenv("openrouter_key")  # Đặt trong file .env

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "HTTP-Referer": "http://localhost",  # hoặc domain của bạn nếu deploy
    "Content-Type": "application/json"
}

def generate_response(message):
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return f"Lỗi API: {response.text}"

@chatbot_api.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json()
    message = data.get("message", "")
    result = generate_response(message)
    return jsonify({"response": result})
