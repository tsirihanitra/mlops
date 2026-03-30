import os
import pickle
import nltk

nltk.download('punkt')

MODEL_PATH = os.getenv('MODEL_PATH', 'src/model/model.pkl')

def load_model(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def preprocess(text):
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