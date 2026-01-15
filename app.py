import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import requests
from ml.ml_service import MLService

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize ML service
ml_service = MLService()

# MongoDB Setup
interactions_col = None
orders_col = None

try:
    uri = os.getenv("MONGODB_URI")
    if uri:
        mongo_client = MongoClient(uri)
        db = mongo_client.get_database()
        interactions_col = db["user_interactions"]
        orders_col = db["orders"]
        print("✅ Connected to MongoDB")
    else:
        print("⚠️ MONGODB_URI not found in environment")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")

# --- INTENT RESPONSE MAP ---
INTENT_RESPONSES = {
    "greeting": "Hello! How can I help you today? 🛍️",
    "thanks": "You're welcome! Happy to help.",
    "goodbye": "Goodbye! Have a great day! 👋",
    "positive_feedback": "Thank you so much! We love hearing that! ❤️",
    "unknown": "I'm not sure I understood. You can ask about orders, shipping, returns, or our products!",
    "shipping_info": "We offer Free Shipping on orders over $50! Standard takes 3-5 days.",
    "payment_info": "We accept Visa, Mastercard, AMEX, PayPal, and Apple Pay.",
    "account_issue": "For login issues, click 'Forgot Password' or visit your profile page.",
    "promos_discounts": "Use code SAVE20 for 20% off your first order!",
    "stock_info": "Stock is updated daily. Check the product page for live availability.",
    "price_query": "Current prices and discounts are listed on the product pages.",
    "sizing_help": "Check the Size Chart on each product page for detailed measurements.",
    "refund": "To request a refund, please visit our Returns Center within 30 days.",
    "product_issue": "I'm sorry! Please reply with your Order ID and photo of the issue.",
    "wrong_order": "Apologies! Please give me your Order ID and we'll fix it.",
    "cancel_order": "To cancel, visit 'My Orders' immediately. shipped orders cannot be cancelled.",
    "change_order": "We can modify orders within 1 hour. Contact support immediately.",
    "change_shipping_address": "Update your address in 'My Orders' if still 'Processing'.",
    "track_refund": "Refunds take 5-7 business days to appear on your statement.",
    "request_invoice": "Download invoices from your Order History page.",
    "missing_item": "Check split shipment emails. If not found, contact support.",
    "product_catalog": "We sell Perfumes, Makeup, Skincare, Hair Care, Bath & Body, and Electronics.",
    "product_care": "Most items have care labels. generally, wash cold and hang dry.",
    "out_of_scope": "I'm your shopping assistant! I can't play music or answer general questions, but I can help you find products, track orders, or explain our shipping. 🛍️"
}

def get_secured_order_details(order_id):
    """
    Placeholder for JWT-secured external API call.
    In a real scenario, we would:
    1. Authenticate with an auth service to get a JWT token.
    2. Call the e-commerce engine with the token in headers.
    """
    # Simulate external API logic
    # token = authenticate_external_system() 
    # response = requests.get(f"https://api.ecommerce.com/orders/{order_id}", headers={"Authorization": f"Bearer {token}"})
    
    # For now, fallback to local MongoDB (as instructed to keep existing functionality)
    if orders_col is None:
        return None
    order = orders_col.find_one({"orderNumber": order_id})
    if order:
        return f"Order {order['orderNumber']}\nStatus: {order['status']}\nItems: {', '.join(order['items'])}\nTotal: ${order['total']}"
    return None

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'reply': "Please say something!"})

        # 1. Prediction
        intent = ml_service.predict_intent(message)
        sentiment = ml_service.predict_sentiment(message)

        # 2. Sentiment Guardrail: Don't be too happy if the user is upset
        # Note: We only override positive_feedback. Greetings stay as greetings.
        if sentiment == "negative" and intent == "positive_feedback":
            intent = "product_issue"

        # 3. Extract Order ID
        order_id = None
        lower_msg = message.lower()
        if intent == "get_order" or "order" in lower_msg:
            order_match = re.search(r'order\s*#?\s*(\d+)', lower_msg)
            if order_match:
                order_id = int(order_match.group(1))
            elif intent == "get_order":
                nums = re.findall(r'\b\d{5,}\b', lower_msg)
                if nums: order_id = int(nums[0])

        # 3. Handle Dynamic Intent (Orders)
        if intent == "get_order":
            if order_id:
                details = get_secured_order_details(order_id)
                if details:
                    reply = details
                else:
                    reply = f"No order found with number {order_id}."
            else:
                reply = "Please provide an order number."
        elif intent == "product_catalog":
            # Dynamic Category Links
            if "perfume" in lower_msg or "fragrance" in lower_msg:
                reply = "You can browse our Perfume collection here: [Perfumes](https://example.com/perfumes) 🌸"
            elif "makeup" in lower_msg or "lipstick" in lower_msg:
                reply = "Check out our latest Makeup trends: [Makeup](https://example.com/makeup) 💄"
            elif "skincare" in lower_msg:
                reply = "Explore our Skincare range: [Skincare](https://example.com/skincare) ✨"
            elif "electronics" in lower_msg:
                reply = "Discover our Tech & Electronics: [Electronics](https://example.com/electronics) 🎧"
            else:
                reply = INTENT_RESPONSES.get("product_catalog")
        else:
            # 4. Handle Product Care Variations (Ported from server.js)
            reply = INTENT_RESPONSES.get(intent, INTENT_RESPONSES["unknown"])
            
            if intent == "product_care":
                if "leather" in lower_msg:
                    reply = "For leather: Wipe with a damp cloth and avoid direct heat."
                elif "cotton" in lower_msg:
                    reply = "For cotton: Machine wash cold. Tumble dry low."
                elif any(x in lower_msg for x in ["silk", "delicate"]):
                    reply = "For silk: Hand wash cold. Do not wring."

        # 5. Log to MongoDB for Continuous Learning
        if interactions_col is not None:
            try:
                interactions_col.insert_one({
                    "text": message,
                    "intent": intent,
                    "sentiment": sentiment,
                    "timestamp": datetime.now()
                })
            except Exception as e:
                print(f"Logging error: {e}")

        return jsonify({
            'reply': reply,
            'intent': intent,
            'sentiment': sentiment
        })
    except Exception as e:
        print(f"🔥 CRITICAL CHAT ERROR: {e}")
        return jsonify({
            'reply': f"Internal Error: {str(e)}",
            'error': str(e)
        }), 500

@app.route('/predict', methods=['POST'])
def predict():
    # Keep legacy endpoint for safety during transition
    data = request.get_json()
    message = data.get('message', '')
    intent = ml_service.predict_intent(message)
    sentiment = ml_service.predict_sentiment(message)
    return jsonify({'intent': intent, 'sentiment': sentiment})

if __name__ == '__main__':
    # Using 5001 as the primary backend port now
    app.run(port=5001, debug=True)