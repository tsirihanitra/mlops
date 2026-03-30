FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code et le modèle
COPY src/ ./src/

# Lancer le script
CMD ["python", "src/predict.py"]
```

---

**requirements.txt :**
```
numpy
pandas
scikit-learn
nltk
transformers