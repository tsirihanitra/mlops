import streamlit as st
import requests
import json

st.set_page_config(page_title="Prédiction Qualité du Vin", page_icon="🍷", layout="centered")

st.title("🍷 Prédicteur de Qualité du Vin (MLOps)")
st.markdown("Cette interface interroge votre API de Machine Learning Flask en temps réel.")

API_URL = "http://app:5000/predict"

with st.sidebar:
    st.header("Paramètres du Vin")
    fixed_acidity = st.slider("Fixed Acidity", 4.0, 16.0, 8.0)
    volatile_acidity = st.slider("Volatile Acidity", 0.1, 2.0, 0.5)
    citric_acid = st.slider("Citric Acid", 0.0, 1.0, 0.25)
    residual_sugar = st.slider("Residual Sugar", 0.5, 16.0, 2.0)
    chlorides = st.slider("Chlorides", 0.01, 0.6, 0.08)
    free_sulfur_dioxide = st.slider("Free Sulfur Dioxide", 1.0, 72.0, 15.0)
    total_sulfur_dioxide = st.slider("Total Sulfur Dioxide", 6.0, 289.0, 46.0)
    density = st.slider("Density", 0.990, 1.004, 0.996)
    pH = st.slider("pH", 2.7, 4.0, 3.3)
    sulphates = st.slider("Sulphates", 0.3, 2.0, 0.65)
    alcohol = st.slider("Alcohol", 8.0, 15.0, 10.4)

st.subheader("Les caractéristiques choisies :")
data = [[
    fixed_acidity, volatile_acidity, citric_acid, residual_sugar, chlorides,
    free_sulfur_dioxide, total_sulfur_dioxide, density, pH, sulphates, alcohol
]]
st.write(data)

if st.button("🔮 Prédire la Qualité", type="primary"):
    with st.spinner("Interrogation du modèle en cours..."):
        try:
            response = requests.post("http://wine-prediction-app:5000/predict", json={"data": data})
            
            if response.status_code == 200:
                resultat = response.json().get("predictions", ["Erreur"])[0]
                if resultat == "Bon":
                    st.success(f"🍾 Le vin est prédit comme : **{resultat}** ! Santé !")
                else:
                    st.error(f"🍷 Le vin est prédit comme : **{resultat}**.")
            else:
                st.warning(f"Erreur de l'API (Status {response.status_code}): {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Impossible de contacter l'API Flask. Vérifiez que le conteneur 'wine-prediction-app' est bien démarré.")
