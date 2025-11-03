from transformers import AutoModelForSequenceClassification
import torch

path = "./models/vibert4news_finetuned"

model = AutoModelForSequenceClassification.from_pretrained(path)

print("🔍 Head weight mean:", model.classifier.out_proj.weight.mean().item())
print("🔍 Head bias mean:", model.classifier.out_proj.bias.mean().item())
