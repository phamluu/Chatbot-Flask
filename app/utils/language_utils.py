import spacy
from langdetect import detect
from pyvi import ViTokenizer

try:
    nlp = spacy.load("./models/en_core_web_sm")
    print("✅ spaCy model đã sẵn sàng.")
except Exception as e:
    print(f"❌ spaCy load error: {e}")
    nlp = None

def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"

def extract_keywords(text):
    lang = detect_language(text)
    if lang == "vi":
        tokens = ViTokenizer.tokenize(text).split()
        return list(set([w for w in tokens if len(w) > 2]))
    elif nlp:
        doc = nlp(text)
        return list(set([token.text for token in doc if token.pos_ in ("NOUN", "PROPN") and not token.is_stop]))
    return []

def generate_local_response(message):
    lang = detect_language(message)
    if lang == "vi":
        return "⚠️ Tôi nhận thấy bạn đang nói tiếng Việt."
    elif nlp:
        doc = nlp(message)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return f"📌 spaCy phát hiện entities: {entities}" if entities else "⚠️ Không tìm thấy entity nào."
    else:
        return "⚠️ Không có công cụ phân tích ngôn ngữ khả dụng."
