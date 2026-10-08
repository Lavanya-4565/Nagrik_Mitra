# import json
# import os
# import random

# from flask import Flask, jsonify, render_template, request

# from services.predictor import predict_intent

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# INTENTS_PATH = os.path.join(BASE_DIR, "Intents.json")

# with open(INTENTS_PATH, "r", encoding="utf-8") as f:
#     intents_data = json.load(f)

# # Below this, we don't trust the prediction enough to show it as an answer.
# # Between this and 0.6 we still answer, but flag it as a "likely" match
# # rather than a confident one. Tune both as your training data grows.
# CONFIDENCE_THRESHOLD = 0.35
# LIKELY_THRESHOLD = 0.60

# app = Flask(__name__)


# def get_response(intent):
#     for item in intents_data["intents"]:
#         if item["tag"] == intent:
#             return random.choice(item["responses"])
#     return "Sorry, I couldn't find a response."


# def confidence_tier(confidence):
#     if confidence < CONFIDENCE_THRESHOLD:
#         return "uncertain"
#     if confidence < LIKELY_THRESHOLD:
#         return "likely"
#     return "verified"


# @app.route("/")
# def index():
#     return render_template("index.html")


# @app.route("/api/chat", methods=["POST"])
# def chat():
#     payload = request.get_json(silent=True) or {}
#     message = (payload.get("message") or "").strip()

#     if not message:
#         return jsonify({"error": "Message is empty."}), 400

#     intent, confidence = predict_intent(message)
#     intent = str(intent)
#     confidence = float(confidence)
#     tier = confidence_tier(confidence)

#     if tier == "uncertain":
#         reply = "Sorry, I didn't understand your question. Could you rephrase it?"
#     else:
#         reply = get_response(intent)

#     return jsonify({
#         "reply": reply,
#         "intent": intent,
#         "confidence": round(confidence, 3),
#         "tier": tier,
#     })


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)



import json
import os
import random

import joblib
from flask import Flask, jsonify, render_template, request

from services.preprocessing import preprocess


# --------------------------------------------------
# BASE DIRECTORY
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------
# LOAD MODEL AND VECTORIZER
# --------------------------------------------------

MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "vectorizer.pkl")

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


# --------------------------------------------------
# LOAD INTENTS
# --------------------------------------------------

INTENTS_PATH = os.path.join(BASE_DIR, "Intents.json")

with open(INTENTS_PATH, "r", encoding="utf-8") as f:
    intents_data = json.load(f)


# --------------------------------------------------
# FLASK APP
# --------------------------------------------------

app = Flask(__name__)


# --------------------------------------------------
# CONFIDENCE SETTINGS
# --------------------------------------------------

CONFIDENCE_THRESHOLD = 0.35
LIKELY_THRESHOLD = 0.60


# --------------------------------------------------
# PREDICT INTENT
# --------------------------------------------------

def predict_intent(user_message):

    cleaned_message = preprocess(user_message)

    X = vectorizer.transform([cleaned_message])

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]
    confidence = max(probabilities)

    return prediction, confidence


# --------------------------------------------------
# GET RESPONSE
# --------------------------------------------------

def get_response(intent):

    for item in intents_data["intents"]:

        if item["tag"] == intent:
            return random.choice(item["responses"])

    return "Sorry, I couldn't find a response."


# --------------------------------------------------
# CONFIDENCE TIER
# --------------------------------------------------

def confidence_tier(confidence):

    if confidence < CONFIDENCE_THRESHOLD:
        return "uncertain"

    if confidence < LIKELY_THRESHOLD:
        return "likely"

    return "verified"


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def index():

    return render_template("index.html")


# --------------------------------------------------
# CHAT API
# --------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():

    payload = request.get_json(silent=True) or {}

    message = (payload.get("message") or "").strip()

    if not message:

        return jsonify({
            "error": "Message is empty."
        }), 400

    try:

        intent, confidence = predict_intent(message)

        intent = str(intent)
        confidence = float(confidence)

        tier = confidence_tier(confidence)

        if tier == "uncertain":

            reply = (
                "Sorry, I didn't understand your question. "
                "Could you rephrase it?"
            )

        else:

            reply = get_response(intent)

        return jsonify({
            "reply": reply,
            "intent": intent,
            "confidence": round(confidence, 3),
            "tier": tier
        })

    except Exception as e:

        print("CHAT ERROR:", repr(e))

        return jsonify({
            "reply": "Sorry, something went wrong while processing your question.",
            "intent": "error",
            "confidence": 0,
            "tier": "uncertain"
        }), 500


# --------------------------------------------------
# LOCAL DEVELOPMENT
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
