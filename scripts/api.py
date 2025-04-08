import os
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd

# Charger les variables d'environnement
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise Exception("DATABASE_URL manquant dans le fichier .env")

# Créer le moteur SQLAlchemy
engine = create_engine(DATABASE_URL)

app = FastAPI(title="API d'accès aux données de MSPr")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API MSPr"}

@app.get("/query")
def execute_query(sql: str = Query(..., description="Votre requête SQL à exécuter")):
    """
    Exécute une requête SQL passée en paramètre et retourne les résultats sous forme de JSON.
    Attention : cette API doit être sécurisée en production (exemple, limitation des requêtes, authentification, etc.)
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            # Récupère tous les résultats
            columns = result.keys()
            rows = result.fetchall()
            # Transformer le résultat en liste de dictionnaires
            data = [dict(zip(columns, row)) for row in rows]
            return {"columns": columns, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de l'exécution de la requête : {str(e)}")
