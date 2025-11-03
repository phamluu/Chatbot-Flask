# check_intents.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Intent, IntentInput
from sqlalchemy import create_engine
import pandas as pd

app = create_app()

with app.app_context():
    engine = create_engine(db.engine.url)
    query = IntentInput.query.join(Intent).with_entities(
        IntentInput.utterance,
        Intent.intent_code
    ).statement

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

print("🔹 Mẫu dữ liệu:")
print(df.head())

print("\n🔎 Phân bố số lượng mẫu theo intent_code:")
print(df["intent_code"].value_counts())

print("\n📊 Tỷ lệ phần trăm:")
print((df["intent_code"].value_counts(normalize=True) * 100).round(2))
