from src.predict import preprocess

def test_preprocess():
    result = preprocess("Bonjour le Monde")
    assert result == "bonjour le monde"
    print("Test OK")

if __name__ == '__main__':
    test_preprocess()