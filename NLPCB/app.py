import json
import os
import random

from flask import Flask, jsonify, render_template, request

from services.predictor import predict_intent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, "Intents.json")

with open(INTENTS_PATH, "r", encoding="utf-8") as f:
    intents_data = json.load(f)

# Below this, we don't trust the prediction enough to show it as an answer.
# Between this and 0.6 we still answer, but flag it as a "likely" match
# rather than a confident one. Tune both as your training data grows.
CONFIDENCE_THRESHOLD = 0.35
LIKELY_THRESHOLD = 0.60

app = Flask(__name__)


def get_response(intent):
    for item in intents_data["intents"]:
        if item["tag"] == intent:
            return random.choice(item["responses"])
    return "Sorry, I couldn't find a response."


def confidence_tier(confidence):
    if confidence < CONFIDENCE_THRESHOLD:
        return "uncertain"
    if confidence < LIKELY_THRESHOLD:
        return "likely"
    return "verified"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Message is empty."}), 400

    intent, confidence = predict_intent(message)
    intent = str(intent)
    confidence = float(confidence)
    tier = confidence_tier(confidence)

    if tier == "uncertain":
        reply = "Sorry, I didn't understand your question. Could you rephrase it?"
    else:
        reply = get_response(intent)

    return jsonify({
        "reply": reply,
        "intent": intent,
        "confidence": round(confidence, 3),
        "tier": tier,
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
