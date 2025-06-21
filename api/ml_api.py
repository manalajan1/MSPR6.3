from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

# Charger le modèle entraîné
model = joblib.load("scripts/model_covid_rf.joblib")

class PredictionRequest(BaseModel):
    total_deaths: int
    total_recovered: int

class PredictionResponse(BaseModel):
    prediction: int
    probability: float

@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    X = np.array([[req.total_deaths, req.total_recovered]])
    pred = model.predict(X)[0]
    proba = float(model.predict_proba(X)[0][1])
    return PredictionResponse(prediction=pred, probability=proba)
