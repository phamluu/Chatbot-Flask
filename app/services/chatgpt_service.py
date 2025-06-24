# app/services/chatgpt_service.py
import openai

openai.api_key = "YOUR_API_KEY"  # nên để vào biến môi trường

def chat_with_gpt(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # hoặc gpt-4 nếu bạn có quyền
        messages=[
            {"role": "system", "content": "Bạn là một trợ lý thân thiện."},
            {"role": "user", "content": message}
        ]
    )
    return response['choices'][0]['message']['content']
