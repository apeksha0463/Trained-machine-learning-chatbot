from flask import Flask, request, jsonify
from flask_cors import CORS
from ml.ml_service import MLService
import re

app = Flask(__name__)
CORS(app)

# Initialize ML service
ml_service = MLService()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    message = data.get('message', '')

    # Use ML service to predict intent
    intent = ml_service.predict_intent(message)

    # Extract order number if present
    order_match = re.search(r'\b\d+\b', message)
    order_id = int(order_match.group()) if order_match else None

    return jsonify({
        'intent': intent,
        'order_id': order_id
    })

if __name__ == '__main__':
    app.run(port=5001, debug=True)