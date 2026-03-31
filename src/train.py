import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

DATA_PATH = os.getenv('DATA_PATH', 'data/winequality-red.csv')
MODEL_DIR = 'src/model'

os.makedirs(MODEL_DIR, exist_ok=True)

print("Chargement des donnees...")
df = pd.read_csv(DATA_PATH, sep=';')

df['quality'] = (df['quality'] >= 6).astype(int)

X = df.drop('quality', axis=1)
y = df['quality']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Entrainement du modele...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

rf = RandomForestClassifier(n_estimators=300, random_state=42)
rf.fit(X_train_scaled, y_train)

acc = accuracy_score(y_test, rf.predict(X_test_scaled))
print(f"Accuracy : {acc:.4f}")

joblib.dump(rf,     os.path.join(MODEL_DIR, 'random_forest_wine.pkl'))
joblib.dump(scaler, os.path.join(MODEL_DIR, 'scaler_wine.pkl'))
print(f"Modele sauvegarde dans {MODEL_DIR}")