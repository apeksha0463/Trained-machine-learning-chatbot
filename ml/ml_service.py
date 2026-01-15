import pickle
import re
import numpy as np
import os
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class MLService:
    def __init__(self):
        base_path = os.path.dirname(__file__)
        root_path = os.path.join(base_path, "..")
        
        self.intent_model = None
        self.intent_vectorizer = None
        self.sentiment_model = None
        self.sentiment_tokenizer = None
        self.sentiment_encoder = None
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # 1. Load Intent Model
        try:
            model_path = os.path.join(base_path, "model.pkl")
            vec_path = os.path.join(base_path, "vectorizer.pkl")
            if os.path.exists(model_path) and os.path.exists(vec_path):
                with open(model_path, "rb") as f:
                    self.intent_model = pickle.load(f)
                with open(vec_path, "rb") as f:
                    self.intent_vectorizer = pickle.load(f)
                print("✅ Intent model loaded")
            else:
                print("⚠️ Intent model files not found")
        except Exception as e:
            print(f"❌ Error loading intent model: {e}")

        # 2. Load Sentiment Model (Keras)
        try:
            # Try .keras first, then .h5 if available
            keras_path = os.path.join(root_path, "sentiment_model.keras")
            h5_path = os.path.join(root_path, "sentiment_model.h5")
            
            target_model_path = None
            if os.path.exists(keras_path): target_model_path = keras_path
            elif os.path.exists(h5_path): target_model_path = h5_path
            
            if target_model_path:
                self.sentiment_model = load_model(target_model_path)
                print(f"✅ Sentiment model ({os.path.basename(target_model_path)}) loaded")
            
            tok_path = os.path.join(base_path, "tokenizer.pkl")
            enc_path = os.path.join(root_path, "sentiment_label_encoder.pkl")
            
            if os.path.exists(tok_path):
                with open(tok_path, "rb") as f:
                    self.sentiment_tokenizer = pickle.load(f)
            if os.path.exists(enc_path):
                with open(enc_path, "rb") as f:
                    self.sentiment_encoder = pickle.load(f)
                    
            if self.sentiment_model and self.sentiment_tokenizer and self.sentiment_encoder:
                print("✅ Sentiment components fully initialized")
        except Exception as e:
            print(f"❌ Error loading sentiment components: {e}")

    def predict_intent(self, message):
        if not message: return "unknown"
        try:
            if not self.intent_vectorizer or not self.intent_model:
                return "unknown"
            X = self.intent_vectorizer.transform([message.lower()])
            probabilities = self.intent_model.predict_proba(X)[0]
            if max(probabilities) < 0.15: return "unknown"
            return self.intent_model.predict(X)[0]
        except:
            return "unknown"

    def predict_sentiment(self, message):
        if not message: return "neutral"
        lower_msg = message.strip().lower()
        
        # Priority 0: Common Neutral/Positive Greetings & Phrases Whitelist
        # This prevents common words from being skewed by noisy LSTM training data
        neutral_words = {
            "hello", "hi", "hey", "hola", "greetings", "morning", "afternoon", "evening",
            "mind blowing", "perfect", "suits", "amazing", "wonderful", "excellent"
        }
        
        # Check for positive keywords first
        if any(w in lower_msg for w in ["mind blowing", "perfect", "suits", "amazing"]):
            return "positive"
            
        if lower_msg in neutral_words:
            return "neutral"
        
        # Priority 1: Try Neural Model (if components exist)
        try:
            if self.sentiment_model and self.sentiment_tokenizer and self.sentiment_encoder:
                clean_msg = re.sub(r"[^a-zA-Z ]", "", message.lower())
                seq = self.sentiment_tokenizer.texts_to_sequences([clean_msg])
                if seq and len(seq[0]) > 0:
                    X = pad_sequences(seq, maxlen=100)
                    pred = self.sentiment_model.predict(X, verbose=0)
                    idx = np.argmax(pred)
                    return self.sentiment_encoder.inverse_transform([idx])[0]
        except Exception as e:
            print(f"DEBUG: Neural sentiment fail: {e}")
        
        # Priority 2: VADER Fallback
        try:
            scores = self.sentiment_analyzer.polarity_scores(message)
            if scores['compound'] <= -0.05: return "negative"
            if scores['compound'] >= 0.05: return "positive"
        except Exception as e:
            print(f"DEBUG: VADER fail: {e}")
            
        return "neutral"
