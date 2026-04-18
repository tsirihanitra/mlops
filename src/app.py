from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os

app = Flask(__name__)

MODEL_PATH  = os.getenv('MODEL_PATH',  'src/model/random_forest_wine.pkl')
SCALER_PATH = os.getenv('SCALER_PATH', 'src/model/scaler_wine.pkl')

COLONNES = [
    'fixed acidity', 'volatile acidity', 'citric acid',
    'residual sugar', 'chlorides', 'free sulfur dioxide',
    'total sulfur dioxide', 'density', 'pH', 'sulphates', 'alcohol'
]

rf     = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model': 'wine-quality'})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json.get('data')
    df      = pd.DataFrame(data, columns=COLONNES)
    scaled  = scaler.transform(df)
    preds   = rf.predict(scaled)
    results = ["Bon" if p == 1 else "Mauvais" for p in preds]
    return jsonify({'predictions': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
