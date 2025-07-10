from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

# Charger le modèle entraîné
try:
    model = joblib.load("model_covid_rf.joblib")
except Exception as e:
    model = None
    print(f"Erreur lors du chargement du modèle : {e}")

class PredictionRequest(BaseModel):
    total_deaths: int
    total_recovered: int

class PredictionResponse(BaseModel):
    prediction: int
    probability: float

@app.get("/")
def root():
    return {"message": "API IA opérationnelle"}

@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    """
    Prédire si un pays dépasse 10 000 cas en fonction des décès et guérisons totaux.
    Retourne la classe prédite et la probabilité associée.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Modèle non chargé")
    try:
        X = np.array([[req.total_deaths, req.total_recovered]])
        pred = model.predict(X)[0]
        proba = float(model.predict_proba(X)[0][1])
        return PredictionResponse(prediction=pred, probability=proba)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))