import json
import os
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from services.preprocessing import preprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, "Intents.json")
MODELS_DIR = os.path.join(BASE_DIR, "models")

with open(INTENTS_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

texts = []
labels = []

for intent in data["intents"]:

    tag = intent["tag"]

    for pattern in intent["patterns"]:

        cleaned_pattern = preprocess(pattern)

        texts.append(cleaned_pattern)

        labels.append(tag)

vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)

X = vectorizer.fit_transform(texts)

model = LogisticRegression(max_iter=1000, C=10)

model.fit(X, labels)

os.makedirs(MODELS_DIR, exist_ok=True)

joblib.dump(model, os.path.join(MODELS_DIR, "model.pkl"))
joblib.dump(vectorizer, os.path.join(MODELS_DIR, "vectorizer.pkl"))

print(f"Model trained successfully on {len(texts)} patterns across {len(set(labels))} intents!")