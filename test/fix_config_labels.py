import json
import pickle
import os

model_dir = "./models/vibert4news_finetuned"
config_path = os.path.join(model_dir, "config.json")
label_path = os.path.join(model_dir, "label_encoder.pkl")

# Đọc label encoder
with open(label_path, "rb") as f:
    le = pickle.load(f)

# Đọc config.json gốc
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

# Cập nhật các trường
config["_name_or_path"] = model_dir
config["num_labels"] = len(le.classes_)
config["id2label"] = {i: label for i, label in enumerate(le.classes_)}
config["label2id"] = {label: i for i, label in enumerate(le.classes_)}

# Ghi đè file
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print("✅ config.json đã được cập nhật lại khớp với label_encoder.pkl")
print(f"🔢 Tổng số nhãn: {len(le.classes_)}")
print("🏷️ Ví dụ:", le.classes_[:5])
