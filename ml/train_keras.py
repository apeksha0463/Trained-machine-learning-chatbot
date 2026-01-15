import pandas as pd
import os
import numpy as np
import re
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Bidirectional, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle

# ---------------------------
# 1. LOAD DATA (Fast Repair Mode)
# ---------------------------
def load_data(path, limit=2000):
    # Try train_small.txt first as it's cleaner
    if not os.path.exists(path):
        path = "data/train_small.txt"
    if not os.path.exists(path):
        print("❌ Data file not found!")
        return [], []
        
    texts, labels = [], []
    with open(path, "r", encoding="utf-16", errors="ignore") as f:
        for i, line in enumerate(f):
            if i >= limit: break
            if "__label__" in line:
                parts = line.strip().split(" ", 1)
                label = int(parts[0].replace("__label__", ""))
                text = parts[1]
                texts.append(text)
                labels.append(label)
    return texts, labels

texts, ratings = load_data("data/train_small.txt")

# ---------------------------
# 2. MAP TO SENTIMENT
# ---------------------------
def map_sentiment(r):
    if r <= 2:
        return "negative"
    elif r == 3:
        return "neutral"
    else:
        return "positive"

sentiments = [map_sentiment(r) for r in ratings]

# ---------------------------
# 3. CLEAN TEXT
# ---------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z ]", "", text)
    return text

texts = [clean_text(t) for t in texts]

# ---------------------------
# 4. TOKENIZATION
# ---------------------------
tokenizer = Tokenizer(num_words=30000, oov_token="<OOV>")
tokenizer.fit_on_texts(texts)

sequences = tokenizer.texts_to_sequences(texts)
MAX_LEN = 100 # Synchronized with ml_service.py
X = pad_sequences(sequences, maxlen=MAX_LEN)

# ---------------------------
# 5. ENCODE LABELS
# ---------------------------
encoder = LabelEncoder()
y = encoder.fit_transform(sentiments)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------------------
# 6. BUILD MODEL (RECRUITER LEVEL)
# ---------------------------
model = Sequential([
    Embedding(30000, 128, input_length=MAX_LEN),
    Bidirectional(LSTM(64, return_sequences=True)),
    Dropout(0.3),
    Bidirectional(LSTM(32)),
    Dense(32, activation="relu"),
    Dropout(0.3),
    Dense(3, activation="softmax")
])

model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer="adam",
    metrics=["accuracy"]
)

model.summary()

# ---------------------------
# 7. TRAIN
# ---------------------------
model.fit(
    X_train,
    y_train,
    epochs=5,
    batch_size=128,
    validation_data=(X_test, y_test)
)

# ---------------------------
# 8. SAVE EVERYTHING (Correct Paths)
# ---------------------------
# Model goes to root for app.py
model.save("../sentiment_model.keras")

# Tokenizer and Encoder go to ml/ for MLService
with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

with open("../sentiment_label_encoder.pkl", "wb") as f:
    # Renamed to match ml_service.py expected name
    pickle.dump(encoder, f)

print("✅ Sentiment model repaired and synchronized!")
