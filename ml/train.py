import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

texts = [
    "hello",
    "hi",
    "order 72",
    "show my order",
    "track order",
    "thanks",
    "bye"
]

labels = [
    "greeting",
    "greeting",
    "get_order",
    "get_order",
    "get_order",
    "thanks",
    "goodbye"
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("Model trained")
