# store_data.py
import os
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Récupérer l'URL de connexion
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise Exception("La variable d'environnement DATABASE_URL n'a pas été trouvée")

# Créer le moteur SQLAlchemy
engine = create_engine(DATABASE_URL)

# Dossier contenant les fichiers nettoyés
cleaned_data_dir = os.path.join(os.getcwd(), "cleaned_data")

# Liste des fichiers nettoyés et leurs noms de tables associées
datasets = {
    'cleaned_covid19_daily_dataset.csv': 'covid19_daily',
    'cleaned_mpox_dataset.csv': 'mpox'
}

for file_name, table_name in datasets.items():
    file_path = os.path.join(cleaned_data_dir, file_name)
    print(f"Chargement du fichier {file_path}...")
    
    # Lire le CSV dans un DataFrame pandas
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        continue
    
    # Vous pouvez éventuellement effectuer des ajustements supplémentaires ici
    
    # Stocker dans la base de données, remplacer la table si elle existe déjà
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Table '{table_name}' créée dans PostgreSQL avec {len(df)} enregistrements.")
    except Exception as e:
        print(f"Erreur lors de l'insertion de la table {table_name}: {e}")

print("Stockage terminé.")
