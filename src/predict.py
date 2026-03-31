import os
import pickle
import nltk

nltk.download('punkt')

MODEL_PATH = os.getenv('MODEL_PATH', 'src/model/model.pkl')

def load_model(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def preprocess(text):import pandas as pd
import joblib
import os

MODEL_PATH  = os.getenv('MODEL_PATH',  'src/model/random_forest_wine.pkl')
SCALER_PATH = os.getenv('SCALER_PATH', 'src/model/scaler_wine.pkl')

COLONNES = [
    'fixed acidity', 'volatile acidity', 'citric acid',
    'residual sugar', 'chlorides', 'free sulfur dioxide',
    'total sulfur dioxide', 'density', 'pH', 'sulphates', 'alcohol'
]

def predict(data: list):
    rf     = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    df     = pd.DataFrame(data, columns=COLONNES)
    scaled = scaler.transform(df)
    preds  = rf.predict(scaled)
    return ["Bon" if p == 1 else "Mauvais" for p in preds]

if __name__ == '__main__':
    echantillons = [
        [11.2, 0.28, 0.56, 1.9, 0.075, 17, 60, 0.9980, 3.16, 0.58, 9.8],
        [7.8,  0.88, 0.00, 2.6, 0.098, 25, 67, 0.9968, 3.20, 0.68, 9.8]
    ]
    resultats = predict(echantillons)
    for i, r in enumerate(resultats):
        print(f"Vin {i+1} : {r}")
    tokens = nltk.word_tokenize(text.lower())
    return ' '.join(tokens)

def predict(text):
    model = load_model(MODEL_PATH)
    cleaned = preprocess(text)
    result = model.predict([cleaned])
    return result[0]

if __name__ == '__main__':
    sample = "Votre texte à analyser ici"
    print(f"Texte : {sample}")
    print(f"Résultat : {predict(sample)}")