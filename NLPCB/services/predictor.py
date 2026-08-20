import os
import joblib
from services.preprocessing import preprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model = joblib.load(os.path.join(BASE_DIR, "models", "model.pkl"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "models", "vectorizer.pkl"))


def predict_intent(user_message):

    cleaned_message = preprocess(user_message)

    X = vectorizer.transform([cleaned_message])

    prediction = model.predict(X)[0]

    confidence = max(model.predict_proba(X)[0])

    return prediction, confidence


# for testing purpose
# while True:

#     message = input("You: ")

#     intent, confidence = predict_intent(message)

#     print("Intent:", intent)
#     print("Confidence:", confidence)
