
import csv
import os
import random

# Output to parent directory (ml/ecommerce_dataset.txt)
output_file = "../ecommerce_dataset.txt"
data_dir = "."

print(f"Generating {output_file} from datasets in {os.getcwd()}...")

def clean_text(text):
    if not text: return ""
    return text.replace("\n", " ").replace("\r", " ").strip()

with open(output_file, "w", encoding="utf-8") as outfile:
    
    # 1. Include the generated intents file
    if os.path.exists("chatbot_intents.csv"):
        print("Processing chatbot_intents.csv...")
        with open("chatbot_intents.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                intent = row.get('intent')
                text = clean_text(row.get('text'))
                if intent and text:
                    outfile.write(f"__label__{intent} {text}\n")
                    count += 1
            print(f"  Added {count} samples.")

    # 2. Books Dataset -> product_search, price_query
    fname = "Best Selling Books- Buy Products Online at Best Price in India - All Categories _ Flipkart.com.csv"
    if os.path.exists(fname):
        print(f"Processing {fname}...")
        try:
            with open(fname, "r", encoding="utf-8", errors='ignore') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    item = clean_text(row.get('Item'))
                    if item:
                        # Add a search query
                        outfile.write(f"__label__product_search I want to buy {item}\n")
                        # Add a price query
                        outfile.write(f"__label__price_query How much is {item}\n")
                        count += 2
                        if count > 2000: break # Limit to avoid over-representation
                print(f"  Added {count} samples.")
        except Exception as e:
            print(f"  Error: {e}")

    # 3. Cosmetics Dataset -> product_search, product_details
    fname = "E-commerce  cosmetic dataset.csv"
    if os.path.exists(fname):
        print(f"Processing {fname}...")
        try:
            with open(fname, "r", encoding="utf-8", errors='ignore') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    prod = clean_text(row.get('product_name'))
                    if prod:
                        outfile.write(f"__label__product_search looking for {prod}\n")
                        outfile.write(f"__label__product_details details about {prod}\n")
                        count += 2
                        if count > 2000: break
                print(f"  Added {count} samples.")
        except Exception as e:
            print(f"  Error: {e}")

    # 4. Fashion Dataset -> product_search
    fname = "FashionDataset.csv"
    if os.path.exists(fname):
        print(f"Processing {fname}...")
        try:
            with open(fname, "r", encoding="utf-8", errors='ignore') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    brand = clean_text(row.get('BrandName'))
                    if brand:
                        outfile.write(f"__label__product_search show me {brand} clothes\n")
                        count += 1
                        if count > 1000: break
                print(f"  Added {count} samples.")
        except Exception as e:
            print(f"  Error: {e}")

    # 5. Delivery Reviews -> positive_feedback, product_issue, delivery_query
    fname = "Fast Delivery Agent Reviews.csv"
    if os.path.exists(fname):
        print(f"Processing {fname}...")
        try:
            with open(fname, "r", encoding="utf-8", errors='ignore') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    # Guessing column names based on head
                    # "Agent Name,Rating,Reviews" (Assuming 'Reviews' based on standard datasets)
                    # Use .get() with fallback if column case/name varies
                    rating = row.get('Rating')
                    review = row.get('Reviews') or row.get('Review') or row.get('reviews')
                    
                    if rating and review:
                        review = clean_text(review)
                        try:
                            r = float(rating)
                            if r >= 4.5:
                                outfile.write(f"__label__positive_feedback {review}\n")
                                count += 1
                            elif r <= 2.5:
                                if "late" in review.lower() or "delivery" in review.lower() or "time" in review.lower():
                                    outfile.write(f"__label__delivery_query {review}\n")
                                else:
                                    outfile.write(f"__label__product_issue {review}\n")
                                count += 1
                        except:
                            continue
                        if count > 2000: break
                print(f"  Added {count} samples.")
        except Exception as e:
            print(f"  Error: {e}")

print("Done generating dataset.")
