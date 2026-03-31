import pandas as pd

COLONNES = [
    'fixed acidity', 'volatile acidity', 'citric acid',
    'residual sugar', 'chlorides', 'free sulfur dioxide',
    'total sulfur dioxide', 'density', 'pH', 'sulphates', 'alcohol'
]

def test_colonnes():
    data = [[11.2, 0.28, 0.56, 1.9, 0.075, 17, 60, 0.9980, 3.16, 0.58, 9.8]]
    df = pd.DataFrame(data, columns=COLONNES)
    assert df.shape == (1, 11)
    print("Test colonnes : OK")

def test_valeurs():
    data = [[11.2, 0.28, 0.56, 1.9, 0.075, 17, 60, 0.9980, 3.16, 0.58, 9.8]]
    df = pd.DataFrame(data, columns=COLONNES)
    assert df['alcohol'].values[0] == 9.8
    print("Test valeurs : OK")

if __name__ == '__main__':
    test_colonnes()
    test_valeurs()
    print("Tous les tests passent !")