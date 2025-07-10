import pytest
import requests

@pytest.mark.skip(reason="API non démarrée ou modèle IA manquant en CI")
def test_predict():
    response = requests.post("http://localhost:8000/predict", json={
        "country": "France",
        "date": "2020-03-01",
        "total_cases": 100,
        "total_deaths": 2,
        "total_recovered": 10
    })
    assert response.status_code == 200