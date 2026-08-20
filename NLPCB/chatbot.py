import json
import random
# from services.preprocessing import preprocess
from services.predictor import predict_intent

with open("Intents.json", "r",encoding="utf-8") as file:
    data = json.load(file)


def get_response(intent):

    for item in data["intents"]:

        if item["tag"] == intent:

            responses = item["responses"]

            return random.choice(responses)

    return "Sorry, I couldn't find a response."


print("=" * 40)
print("     Civic NLP Chatbot")
print("Type 'exit' to quit")
print("=" * 40)

while True:

    user_message = input("\nYou: ")

    if user_message.lower() == "exit":
        print("Bot: Goodbye!")
        break

    intent, confidence = predict_intent(user_message)

    print(f"[Intent: {intent} | Confidence: {confidence:.2f}]")

    if confidence < 0.10:
        print("Bot: Sorry, I didn't understand your question.")
        continue

    print("Bot:", get_response(intent))