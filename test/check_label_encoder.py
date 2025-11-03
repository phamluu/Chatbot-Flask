import pickle

path = "./models/vibert4news_finetuned/label_encoder.pkl"

with open(path, "rb") as f:
    le = pickle.load(f)

print("🔢 Số class:", len(le.classes_))
print("🏷️ Danh sách nhãn:")
for i, c in enumerate(le.classes_):
    print(f"{i}: {c}")
