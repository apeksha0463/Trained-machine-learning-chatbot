from flask import Flask, request, jsonify
import pickle
import re

# Load trained model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

class MLService:
    def predict_intent(self, message):
        X = self.vectorizer.transform([message])
        intent = self.model.predict(X)[0]
        return intent

    def __init__(self):
        self.model = model
        self.vectorizer = vectorizer

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("message", "")

    X = vectorizer.transform([text])
    intent = model.predict(X)[0]

    numbers = re.findall(r"\d+", text)
    order_id = int(numbers[0]) if numbers else None

    return jsonify({
        "intent": intent,
        "order_id": order_id
    })

if __name__ == "__main__":
    app.run(port=5001)

