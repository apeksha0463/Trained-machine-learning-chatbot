import csv
import os
import random
import re

# --- Configuration ---
OUTPUT_FILE = "../../chatbot_training_data.csv" # Relative to ml/data if run from there, or correct path
# We will assume this script is run from `ml/data/` or we adjust paths. 
# Best to use absolute paths or relative to script location.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "../chatbot_training_data.csv")

ALLOWED_INTENTS = {
    "greeting", "thanks", "goodbye", "positive_feedback",
    "get_order", "shipping_info", "payment_info", "account_issue",
    "promos_discounts", "stock_info", "sizing_help",
    "refund", "product_issue", "wrong_order",
    "cancel_order", "change_order", "change_shipping_address",
    "track_refund", "request_invoice", "missing_item",
    "expedited_shipping", "shipping_restrictions",
    "delete_account", "update_account", "newsletter_subscription", "privacy_policy",
    "payment_failed", "currency_support", "gift_card",
    "restock_alert", "product_care", "warranty_info", "authenticity",
    "store_hours", "contact_support", "physical_location", "loyalty_program",
    "careers", "gift_wrapping", "product_catalog", "price_query", "unknown"
}

ALLOWED_SENTIMENTS = {"positive", "neutral", "negative"}

# Limits to prevent imbalance
LIMIT_PER_SOURCE_TYPE = 100
INTENT_CAP = 1000

# --- Helper Functions ---

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', str(text)).strip()
    return text

def get_sentiment_for_rating(rating):
    try:
        r = float(rating)
        if r >= 4.0:
            return "positive"
        elif r <= 2.0:
            return "negative"
        else:
            return "neutral"
    except:
        return "neutral"

def infer_sentiment_from_intent(intent, text=""):
    if intent in ["positive_feedback", "thanks"]:
        return "positive"
    if intent in ["product_issue", "refund", "wrong_order", "cancel_order", "payment_failed", "missing_item"]:
        return "negative"
    return "neutral"

def write_row(writer, text, intent, sentiment, stats):
    if not text or len(text) < 2: return False
    if intent not in ALLOWED_INTENTS: return False
    if stats[intent] >= INTENT_CAP: return False # ENFORCE CAP
    
    if sentiment not in ALLOWED_SENTIMENTS: sentiment = "neutral"
    
    writer.writerow({
        "text": text,
        "intent": intent,
        "sentiment": sentiment
    })
    stats[intent] += 1
    return True

# --- Main Processing ---

def generate_csv():
    print(f"Generating {OUTPUT_PATH}...")
    
    records_written = 0
    stats = {i: 0 for i in ALLOWED_INTENTS}

    with open(OUTPUT_PATH, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ["text", "intent", "sentiment"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # 1. Chatbot Intents (Synthetic - PRIORITY)
        fname = os.path.join(BASE_DIR, "chatbot_intents.csv")
        if os.path.exists(fname):
            print(f"Processing synthetic {fname}...")
            with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                random.shuffle(rows) # Variety
                for row in rows:
                    text = clean_text(row.get('text'))
                    intent = row.get('intent')
                    label_map = {
                        "refund_request": "refund",
                        "order_tracking": "get_order",
                        "availability_check": "stock_info",
                        "delivery_query": "shipping_info"
                    }
                    intent = label_map.get(intent, intent)
                    if write_row(writer, text, intent, infer_sentiment_from_intent(intent), stats):
                        records_written += 1

        # 2. Books (Flipkart) -> stock_info, price_query
        fname = os.path.join(BASE_DIR, "Best Selling Books- Buy Products Online at Best Price in India - All Categories _ Flipkart.com.csv")
        if os.path.exists(fname):
            print(f"Processing {fname}...")
            count = 0
            with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                items = [row.get('Item') for row in reader if row.get('Item')]
                random.shuffle(items)
                for item in items:
                    item = clean_text(item)
                    if not item: continue
                    
                    if write_row(writer, f"is {item} book in stock?", "stock_info", "neutral", stats):
                        count += 1
                    if write_row(writer, f"price of book {item}", "price_query", "neutral", stats):
                        count += 1
                    
                    if count >= LIMIT_PER_SOURCE_TYPE: break
            records_written += count

        # 3. Cosmetics -> stock_info, restock_alert
        fname = os.path.join(BASE_DIR, "E-commerce  cosmetic dataset.csv")
        if os.path.exists(fname):
            print(f"Processing {fname}...")
            count = 0
            with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                prods = [row.get('product_name') for row in reader if row.get('product_name')]
                random.shuffle(prods)
                for prod in prods:
                    prod = clean_text(prod)
                    if not prod: continue
                    if write_row(writer, f"is {prod} available?", "stock_info", "neutral", stats):
                        count += 1
                    if write_row(writer, f"restock {prod}?", "restock_alert", "neutral", stats):
                        count += 1
                    if count >= LIMIT_PER_SOURCE_TYPE: break
            records_written += count

        # 4. Fashion -> sizing_help, product_care
        fname = os.path.join(BASE_DIR, "FashionDataset.csv")
        if os.path.exists(fname):
            print(f"Processing {fname}...")
            count = 0
            with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                random.shuffle(rows)
                for row in rows:
                    brand = clean_text(row.get('BrandName'))
                    details = clean_text(row.get('Deatils'))
                    if brand and write_row(writer, f"sizing for {brand}", "sizing_help", "neutral", stats):
                        count += 1
                    if details and write_row(writer, f"how to wash {details}", "product_care", "neutral", stats):
                        count += 1
                    if count >= LIMIT_PER_SOURCE_TYPE: break
            records_written += count

        # 5. Sales Data -> get_order
        fname = os.path.join(BASE_DIR, "Ecommerce_Sales_Data_2024_2025.csv")
        if os.path.exists(fname):
            print(f"Processing {fname}...")
            count = 0
            with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                random.shuffle(rows)
                for row in rows:
                    oid = clean_text(row.get('Order ID'))
                    if oid and write_row(writer, f"order status {oid}", "get_order", "neutral", stats):
                        count += 1
                    if count >= LIMIT_PER_SOURCE_TYPE: break
            records_written += count

        # 6. Reviews -> positive_feedback, product_issue, shipping_info
        fname = os.path.join(BASE_DIR, "Fast Delivery Agent Reviews.csv")
        if os.path.exists(fname):
            print(f"Processing {fname}...")
            count = 0
            with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                random.shuffle(rows)
                for row in rows:
                    rating_val = row.get('Rating')
                    text_val = row.get('Reviews') or row.get('Review') or row.get('reviews')
                    if text_val and rating_val:
                        text = clean_text(text_val)
                        sentiment = get_sentiment_for_rating(rating_val)
                        if sentiment == "positive":
                            if write_row(writer, text, "positive_feedback", "positive", stats):
                                count += 1
                        elif sentiment == "negative":
                            lower_text = text.lower()
                            if any(k in lower_text for k in ["late", "delay", "time", "slow", "arrive"]):
                                if write_row(writer, text, "shipping_info", "negative", stats):
                                    count += 1
                            else:
                                if write_row(writer, text, "product_issue", "negative", stats):
                                    count += 1
                    if count >= LIMIT_PER_SOURCE_TYPE: break
            records_written += count
            
        # 7. User Contributions (Continuous Learning)
        fname = os.path.join(BASE_DIR, "user_contributions.csv")
        if os.path.exists(fname):
            print(f"Processing real user interactions {fname}...")
            count = 0
            with open(fname, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    text = clean_text(row.get('text'))
                    intent = row.get('intent')
                    sentiment = row.get('sentiment')
                    if write_row(writer, text, intent, sentiment, stats):
                        count += 1
            records_written += count

    print(f"\nDone! Total records written: {records_written}")
    print("Intent Distribution:")
    for intent, count in stats.items():
        if count > 0:
            print(f"  {intent}: {count}")

    print(f"\nDone! Total records written: {records_written}")
    print("Intent Distribution:")
    for intent, count in stats.items():
        print(f"  {intent}: {count}")

if __name__ == "__main__":
    generate_csv()
