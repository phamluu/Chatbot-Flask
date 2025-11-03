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

    # ✅ Thêm phần chia dữ liệu train/validation tại đây
    from sklearn.model_selection import train_test_split
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, encoded_labels, test_size=0.2, stratify=encoded_labels, random_state=42
    )

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
                #max_length=12,  # Giảm độ dài để tiết kiệm RAM, có thể cắt cụt nhiều câu → làm model học sai.
                max_length=32, 
                return_tensors="pt"
            )
            return {
                "input_ids": encoded["input_ids"].squeeze(),
                "attention_mask": encoded["attention_mask"].squeeze(),
                "labels": torch.tensor(self.labels[idx])
            }

    train_dataset = IntentDataset(texts, encoded_labels, tokenizer)
    val_dataset = IntentDataset(val_texts, val_labels, tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_DIR,
        num_labels=len(label_encoder.classes_),
        ignore_mismatched_sizes=True
    )
    # --- Gán mapping nhãn đúng cho model ---
    id2label = {i: label for i, label in enumerate(label_encoder.classes_)}
    label2id = {label: i for i, label in enumerate(label_encoder.classes_)}
    model.config.id2label = id2label
    model.config.label2id = label2id

    training_args = TrainingArguments(
        output_dir=SAVE_PATH,
        num_train_epochs=5,
        per_device_train_batch_size=2,   # Giảm batch size xuống 1
        #save_strategy="no",
        #evaluation_strategy="no",
        #logging_strategy="no"

        save_strategy="epoch",   # ✅ Lưu checkpoint sau mỗi epoch
        evaluation_strategy="epoch",
        logging_strategy="steps",
        logging_steps=10,
        save_total_limit=2       # ✅ Giữ lại tối đa 2 checkpoint gần nhất
    )

    from sklearn.utils.class_weight import compute_class_weight
    import numpy as np

    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(encoded_labels),
        y=encoded_labels
    )
    class_weights = torch.tensor(class_weights, dtype=torch.float)

    # Gán vào loss function trong Trainer
    from transformers import Trainer
    from torch.nn import CrossEntropyLoss

    def compute_loss(model, inputs, return_outputs=False):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = CrossEntropyLoss(weight=class_weights.to(logits.device))
        loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

    from transformers import Trainer
    from torch.nn import CrossEntropyLoss

    class WeightedTrainer(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False):
            labels = inputs.pop("labels")
            outputs = model(**inputs)
            logits = outputs.logits
            loss_fct = CrossEntropyLoss(weight=class_weights.to(logits.device))
            loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))
            return (loss, outputs) if return_outputs else loss
    
    trainer = WeightedTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset
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
   
