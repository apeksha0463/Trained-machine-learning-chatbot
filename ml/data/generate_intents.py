import csv
import random

# Product/Category samples for template filling
products = [
    "Charlene Spray Mist Perfume", "Denver Black Code Perfume", "Matte Lipstick",
    "Liquid Eyeliner", "Aloe Vera Moisturizer", "Vitamin C Face Serum",
    "Cocoa Butter Body Lotion", "Organic Shampoo", "Hair Conditioner", "Sunscreen SPF 50"
]
categories = ["perfumes", "makeup", "skincare", "hair care", "bath & body", "fragrances", "electronics", "fashion"]

templates = {
    # Greetings & Feedback
    "greeting": [
        "Hello", "Hi", "Good morning", "Hey there", "Is anyone available?", "Hi chatbot", 
        "Good evening", "Greetings", "Hii", "Hey", "Anyone home?", "Hello bot"
    ],
    "thanks": [
        "Thank you", "Thanks a lot", "Much appreciated", "You're helpful", "thanks", 
        "tysm", "thx", "appreciate the help", "thanks for the information", "ok thanks"
    ],
    "goodbye": [
        "Bye", "Goodbye", "See you later", "I'm done", "talk to you soon", 
        "cya", "bye bye", "leave chat", "exit", "have a good day"
    ],
    "positive_feedback": [
        "I love this product", "Great service", "Excellent experience", "Very happy with my purchase",
        "Best shop ever", "Wonderful support", "I really like the quality", "superb experience",
        "i would like to rate my order 5 stars", "rating my order 10/10", "amazing service",
        "the item was good", "the item was great", "order was amazing", "the quality is excellent",
        "everything was perfect", "really liked the item", "order experience was good"
    ],
    
    # Core E-commerce
    "get_order": [
        "Where is my order {oid}?", "Track order {oid}", "status of order {oid}", "Check my shipment",
        "can you track my shipment", "where is my stuff", "package status", "is my delivery on the way?",
        "check order {oid} status", "i want to track my order", "locate my package", "order tracking please",
        "has my order shipped yet?", "where is order {oid}", "track my delivery"
    ],
    "shipping_info": [
        "shipping charges?", "how long for delivery?", "do you ship to London?", "international shipping options",
        "when will i get my items?", "standard shipping time", "is delivery free?", "shipping policy",
        "express shipping cost", "do u deliver to my city?", "shipping speed", "delivery duration"
    ],
    "payment_info": [
        "which cards do you accept?", "do you take paypal?", "payment methods available", "is apple pay working?",
        "can i pay with visa?", "mastercard support", "secure payment", "cash on delivery?",
        "how can i pay?", "payment options", "secure checkout"
    ],
    "account_issue": [
        "cannot login", "forgot my password", "update my phone number", "where is my profile?",
        "reset password", "change my email", "account verification", "login failed",
        "access my settings", "edit profile details"
    ],
    "promos_discounts": [
        "any coupons?", "deals of the day", "discount codes for new users", "is there a sale?",
        "promo codes", "special offers", "save money", "cheapest items", "give me a discount"
    ],
    "stock_info": [
        "is this in stock?", "when will you restock?", "out of stock item", "check availability",
        "is {product} available?", "do you have {product}?", "stock status of {product}",
        "check if {product} is in store", "is {category} available?", "show me the stock for {product}",
        "can i buy {product} right now?", "do you currently sell {product}?"
    ],
    "sizing_help": [
        "size chart please", "does this run small?", "which size for 32 inch waist?", "standard fit details",
        "sizing guide", "measurements for Large", "find my size", "will this fit me?"
    ],

    # Support / Issues
    "refund": [
        "I want a refund", "return policy", "money back please", "how to return an item",
        "request a refund for order {oid}", "initiate return", "process a refund", "i am not happy need refund",
        "how do i send back my items?", "refund status for {oid}"
    ],
    "product_issue": [
        "item is broken", "damaged product received", "not working as expected", "poor quality",
        "this {product} is defective", "received a broken item", "quality is bad", "broken on arrival",
        "box was crushed", "faulty product", "horrible experience", "the order was terrible",
        "the item is garbage", "absolute worst quality", "received a total mess", "unhappy with the product",
        "the package arrived in awful condition", "this is so disappointing", "very bad service"
    ],
    "wrong_order": [
        "received wrong item", "not what I ordered", "wrong color delivered", "different product in box",
        "you sent me the wrong order", "item mismatch", "order is incorrect", "this is not what i bought"
    ],
    "cancel_order": [
        "cancel my order", "I want to stop my shipment", "don't send my items", "abort order",
        "cancel order {oid}", "i changed my mind cancel it", "stop the order processing"
    ],
    "change_order": [
        "modify my order", "I want to change the items", "add something to my order", "change order quantity",
        "edit order {oid}", "can i add more items?", "wrong quantity on my order"
    ],
    "change_shipping_address": [
        "update delivery address", "change where you ship to", "wrong address on order",
        "edit my shipping info", "change delivery location", "update street address"
    ],
    "track_refund": [
        "where is my refund?", "refund status", "haven't received my money back", "track my return payment",
        "is the refund processed?", "when will i see the money?"
    ],

    # Shipping Extras
    "expedited_shipping": [
        "fast delivery?", "express shipping options", "get it tomorrow", "overnight shipping",
        "priority delivery", "can i get it faster?", "one day shipping"
    ],

    # Account / Policy
    "delete_account": [
        "remove my account", "how to delete profile", "privacy request to delete data",
        "close account", "wipe my data"
    ],
    "privacy_policy": [
        "data security", "privacy policy details", "how do you use my data?", "GDPR info",
        "security measures", "is my info safe?"
    ],

    # Payment Extras
    "payment_failed": [
        "transaction failed", "payment error", "card declined", "why won't my payment go through?",
        "payment rejected", "checkout error"
    ],
    "currency_support": ["do you accept Euro?", "currency conversion", "pay in local currency", "USD to INR"],
    "gift_card": ["buy gift card", "redeem voucher", "gift certificate", "how to use gift card"],

    # Product Specifics
    "restock_alert": [
        "notify me when back in stock", "email when available", "restock dates",
        "get an alert for {product}", "when is {product} coming back?"
    ],
    "product_care": [
        "how to wash this?", "care instructions", "is it machine washable?", "cleaning tips",
        "how to use {product}?", "maintenance for {category}", "how do i clean my {product}",
        "tell me how to care for {category}", "best way to wash {category}", "cleaning guide for {product}",
        "how to handle {category} items", "process to clean {product}", "i need to clean my clothes",
        "how do i clean my cotton clothes", "step by step guide to clean {product}"
    ],
    "warranty_info": [
        "warranty period", "is there a guarantee?", "product insurance", "fix broken item under warranty",
        "is {product} under warranty?"
    ],
    "authenticity": ["is it original?", "fake or real?", "genuine product check", "authenticity guarantee"],

    # Store Info
    "store_hours": ["what time do you close?", "working hours", "is support online now?", "when do you open?"],
    "contact_support": ["customer care number", "email address", "how to call you?", "live agent please", "reach support"],
    "physical_location": ["do you have a store?", "physical shops", "where are you located?", "visit you in person"],
    "loyalty_program": ["rewards program", "VIP points", "membership benefits", "join the club"],
    "careers": ["hiring?", "job openings", "work for you", "careers page"],
    "gift_wrapping": ["add gift wrap", "special packaging", "birthday gift options"],
    
    # NEW: Catalog Browsing
    "product_catalog": [
        "what are the products u have", "show me your catalog", "what do you sell?", 
        "list your products", "view collection", "what categories do you have?",
        "browse store", "show me everything", "what products", "product list", "available items",
        "suggest some url for {category}", "give me a link for {category}", "where can i buy {category}",
        "website for {category}", "show me {category} collection", "recommend some {category}",
        "links for {category}", "i want to see {category}", "direct me to {category}"
    ],
    "price_query": [
        "how much is {product}", "price of {product}", "what does {product} cost?", 
        "how much for {category}", "cost of {category}", "give me the price",
        "how much is one red lipstick", "how much is the face serum", "price of face serum"
    ],
    "out_of_scope": [
        "can you play a song?", "play bollywood music", "tell me a joke", "what is the weather?",
        "who is the president?", "dance for me", "can you sing?", "write a poem",
        "do you like pizza?", "where do babies come from?", "i need to get a paper",
        "what is 2+2?", "tell me a story", "can you fly?", "what time is it in London?",
        "do you have a boyfriend?", "can you cook?", "i am bored", "play some videos"
    ]
}

def generate():
    output_file = "chatbot_intents.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["text", "intent"])
        # We increase the number of samples by looping more times for each intent
        for intent, sents in templates.items():
            # Generate 400 samples per intent to ensure they DOMINATE ALL NOISE
            for _ in range(400):
                s = random.choice(sents)
                text = s.format(
                    product=random.choice(products), 
                    category=random.choice(categories),
                    oid=str(random.randint(10000, 99999))
                )
                writer.writerow([text, intent])
    print(f"Generated {output_file} with {len(templates)} intents and balanced samples.")

if __name__ == "__main__":
    generate()
