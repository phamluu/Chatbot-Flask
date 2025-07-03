# download_model.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "vinai/phobert-base"
SAVE_DIR = "./models/vibert4news"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=6)

# Lưu về local
model.save_pretrained(SAVE_DIR)
tokenizer.save_pretrained(SAVE_DIR)

print("✅ Mô hình đã được tải và lưu ở:", SAVE_DIR)
