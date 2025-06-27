import os
import requests
import markdown2
from dotenv import load_dotenv
from app.utils.language_utils import extract_keywords, generate_local_response

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
        print(f"❌ Web API lỗi: {e}")
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
        print(f"❌ OpenRouter lỗi: {e}")
        return None

def process_message(message):
    keywords = extract_keywords(message)
    print("🔑 Từ khóa trích xuất:", keywords)

    reference_data = fetch_data_from_web(keywords)

    prompt = f"""Người dùng hỏi: "{message}"

Dưới đây là thông tin dữ liệu liên quan được hệ thống tìm thấy:
{reference_data}

Hãy trả lời người dùng một cách tự nhiên và hữu ích dựa trên thông tin ở trên."""

    response = generate_online_response(prompt)
    source = "openrouter"

    if response is None:
        response = generate_local_response(message)
        source = "local"

    html = markdown2.markdown(response)

    return {
        "response": response,
        "source": source,
        "html": html
    }
