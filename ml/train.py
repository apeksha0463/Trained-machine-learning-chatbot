import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

import pandas as pd
import os

# --- LOAD CONSOLIDATED DATASET ---
csv_path = "chatbot_training_data.csv"
if not os.path.exists(csv_path):
    csv_path = "ml/chatbot_training_data.csv"

if os.path.exists(csv_path):
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    # Ensure no NaN values
    df = df.dropna(subset=['text', 'intent'])
    
    texts = df['text'].astype(str).tolist()
    labels = df['intent'].tolist()
    
    print(f"Loaded {len(texts)} samples from unified CSV.")
else:
    print(f"ERROR: {csv_path} not found!")
    exit(1)

# Training logic
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# Using balanced class weights to handle slight imbalances
model = LogisticRegression(class_weight='balanced', max_iter=1000)
model.fit(X, labels)

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

from sklearn.model_selection import cross_val_score
import numpy as np

# Cross-Validation for Accuracy
scores = cross_val_score(model, X, labels, cv=5)
mean_accuracy = np.mean(scores)

print("Model trained successfully!")
print(f"Mean Cross-Validation Accuracy: {mean_accuracy:.2%}")
print(f"Total samples: {len(texts)}")
print(f"Intent classes: {len(model.classes_)}")
