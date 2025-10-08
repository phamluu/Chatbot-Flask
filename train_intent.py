from app import db, create_app
from app.models import Intent, IntentInput
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Sử dụng CPU
import sys
sys.stdout.reconfigure(encoding='utf-8')

import torch
from sqlalchemy import create_engine
import pandas as pd
import pickle
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer
)
from sklearn.preprocessing import LabelEncoder
import traceback
MODEL_DIR = "./models/vibert4news"
SAVE_PATH = "./models/vibert4news_finetuned"

app = create_app()

with app.app_context():
    # Tải dữ liệu
    engine = create_engine(db.engine.url)
    query = IntentInput.query.join(Intent).with_entities(
        IntentInput.utterance, Intent.intent_code
    ).statement
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    texts = df["utterance"].tolist()
    labels = df["intent_code"].tolist()

    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

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
                max_length=12,  # Giảm độ dài để tiết kiệm RAM
                return_tensors="pt"
            )
            return {
                "input_ids": encoded["input_ids"].squeeze(),
                "attention_mask": encoded["attention_mask"].squeeze(),
                "labels": torch.tensor(self.labels[idx])
            }

    train_dataset = IntentDataset(texts, encoded_labels, tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_DIR,
        num_labels=len(label_encoder.classes_),
        ignore_mismatched_sizes=True
    )

    training_args = TrainingArguments(
        output_dir=SAVE_PATH,
        num_train_epochs=3,
        per_device_train_batch_size=1,   # Giảm batch size xuống 1
        save_strategy="no",
        evaluation_strategy="no",
        logging_strategy="no"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset
    )

    try:
        print("Bắt đầu huấn luyện...")
        trainer.train()
        print("✅ Huấn luyện xong.")

        model.save_pretrained(SAVE_PATH)
        tokenizer.save_pretrained(SAVE_PATH)
        with open(f"{SAVE_PATH}/label_encoder.pkl", "wb") as f:
            pickle.dump(label_encoder, f)

        print("✅ Đã huấn luyện và lưu mô hình.")
    except Exception as e:
        with open("logs/train_output.log", "a", encoding="utf-8") as logf:
            logf.write("\n\n=== ❌ Exception Occurred During Training ===\n")
            logf.write(str(e) + "\n")
            logf.write(traceback.format_exc())  # ✅ Ghi rõ traceback
        raise
   
