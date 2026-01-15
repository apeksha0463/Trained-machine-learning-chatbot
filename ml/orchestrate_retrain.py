import os
import csv
from pymongo import MongoClient
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

def fetch_and_prepare_data():
    """
    Fetches logged interactions from MongoDB and prepares them for training.
    Logs are combined with the static synthetic data.
    """
    try:
        client = MongoClient(os.getenv("MONGODB_URI"))
        db = client.get_database()
        interactions_col = db["user_interactions"]
        
        # Get all interactions (could add date filters here for daily training)
        interactions = list(interactions_col.find())
        print(f"📊 Found {len(interactions)} user interactions in DB")
        
        if not interactions:
            print("⚠️ No new interactions found to retrain.")
            return False

        # Prepare new data for generate_training_csv.py to consume
        # We'll save them to a temporary CSV that the aggregator can pick up
        output_path = os.path.join("ml", "data", "user_contributions.csv")
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["text", "intent", "sentiment"])
            writer.writeheader()
            for inter in interactions:
                # We only want to learn from reasonably long messages
                if len(inter['text']) > 3:
                    writer.writerow({
                        "text": inter['text'],
                        "intent": inter['intent'],
                        "sentiment": inter['sentiment']
                    })
        print(f"✅ Saved {len(interactions)} interactions to user_contributions.csv")
        return True
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return False

def run_retrain():
    """
    Executes the standard training pipeline.
    """
    print("🚀 Starting retraining pipeline...")
    
    # 1. Regenerate synthetic data (ensures base quality)
    subprocess.run(["python", "ml/data/generate_intents.py"], check=True)
    
    # 2. Re-aggregate all data (Aggregator must be updated to include user_contributions.csv)
    subprocess.run(["python", "ml/data/generate_training_csv.py"], check=True)
    
    # 3. Retrain model
    subprocess.run(["python", "ml/train.py"], check=True)
    
    print("✅ Model retraining complete!")

if __name__ == "__main__":
    if fetch_and_prepare_data():
        run_retrain()
