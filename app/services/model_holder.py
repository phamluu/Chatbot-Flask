# app/services/model_holder.py

import os
import pickle
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class ModelHolder:
    def __init__(self, model_path="./models/vibert4news_finetuned"):
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.label_encoder = None

    def load(self):
        if self.model is not None:
            return  # already loaded

        tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        with open(os.path.join(self.model_path, "label_encoder.pkl"), "rb") as f:
            label_encoder = pickle.load(f)

        num_labels = len(label_encoder.classes_)
        model_instance = AutoModelForSequenceClassification.from_pretrained(
            self.model_path,
            num_labels=num_labels,
            ignore_mismatched_sizes=True
        ).to(self.device)

        self.model = model_instance.eval()
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder

# Singleton instance
model_holder = ModelHolder()
