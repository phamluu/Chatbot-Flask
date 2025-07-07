from app import db, create_app
from app.models import Intent, IntentInput, IntentResponse
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Chạy CPU

import torch
import pandas as pd
import pickle
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer
)
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import create_engine

# ⚙️ Cấu hình
MODEL_DIR = "./models/vibert4news"
SAVE_PATH = "./models/vibert4news_finetuned"

# ✅ Tạo Flask app và context
app = create_app()

with app.app_context():
    # ✅ Load dữ liệu từ database bằng SQLAlchemy ORM
    engine = create_engine(db.engine.url)

    query = IntentInput.query.join(Intent).with_entities(
        IntentInput.utterance, Intent.intent_code
    ).statement

    df = pd.read_sql(query, engine)
    texts = df["utterance"].tolist()
    labels = df["intent_code"].tolist()

    # ✅ Mã hóa nhãn
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)

    # ✅ Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

    # ✅ Dataset tuỳ chỉnh
    class IntentDataset(Dataset):
        def __init__(self, texts, labels, tokenizer):
            self.texts = texts
            self.labels = labels
            self.tokenizer = tokenizer

        def __len__(self):
            return len(self.texts)

        def __getitem__(self, idx):
            encoded = self.tokenizer(
                self.texts[idx],
                padding="max_length",
                truncation=True,
                max_length=16,
                return_tensors="pt"
            )
            return {
                "input_ids": encoded["input_ids"].squeeze(),
                "attention_mask": encoded["attention_mask"].squeeze(),
                "labels": torch.tensor(self.labels[idx])
            }

    train_dataset = IntentDataset(texts, encoded_labels, tokenizer)

    # ✅ Load mô hình
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_DIR,
        num_labels=len(label_encoder.classes_),
        ignore_mismatched_sizes=True
    )

    # ✅ Cấu hình huấn luyện
    training_args = TrainingArguments(
        output_dir=SAVE_PATH,
        num_train_epochs=5,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        save_strategy="no",
        evaluation_strategy="no",
        logging_strategy="no",
    )

    # ✅ Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )

    # ✅ Huấn luyện
    trainer.train()

    # ✅ Lưu mô hình, tokenizer, label encoder
    model.save_pretrained(SAVE_PATH)
    tokenizer.save_pretrained(SAVE_PATH)
    with open(f"{SAVE_PATH}/label_encoder.pkl", "wb") as f:
        pickle.dump(label_encoder, f)

    print("✅ Huấn luyện xong! Mô hình đã lưu tại:", SAVE_PATH)
