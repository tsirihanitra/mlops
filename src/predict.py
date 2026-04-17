import pandas as pd
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
    """
    Effectue une prediction sur une liste d'echantillons.
    Chaque echantillon doit être une liste de 11 valeurs (les colonnes du vin).
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        raise FileNotFoundError("Le modele ou le scaler n'a pas été trouvé. Lancez d'abord train.py.")

    rf     = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    
    df     = pd.DataFrame(data, columns=COLONNES)
    scaled = scaler.transform(df)
    preds  = rf.predict(scaled)
    
    return ["Bon" if p == 1 else "Mauvais" for p in preds]

if __name__ == '__main__':
    # Exemple d'echantillons pour test
    echantillons = [
        [11.2, 0.28, 0.56, 1.9, 0.075, 17, 60, 0.9980, 3.16, 0.58, 9.8],
        [7.8,  0.88, 0.00, 2.6, 0.098, 25, 67, 0.9968, 3.20, 0.68, 9.8]
    ]
    
    try:
        resultats = predict(echantillons)
        for i, r in enumerate(resultats):
            print(f"Vin {i+1} : {r}")
    except Exception as e:
        print(f"Erreur lors de la prediction : {e}")