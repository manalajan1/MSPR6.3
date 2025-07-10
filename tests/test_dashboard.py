import requests

def test_dashboard_home():
    response = requests.get("http://localhost:8501")
    assert response.status_code == 200
    assert "COVID" in response.text or "Streamlit" in response.text