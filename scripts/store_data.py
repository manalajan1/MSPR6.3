import os
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("La variable DATABASE_URL est manquante")

engine = create_engine(DATABASE_URL)
cleaned_dir = os.path.join(os.getcwd(), "cleaned_data")

# Covid
covid_path = os.path.join(cleaned_dir, "cleaned_covid19_daily_dataset.csv")
df_covid = pd.read_csv(covid_path)
print(f"Injection COVID depuis {covid_path}…")

# Renommer les colonnes pour correspondre à la BDD
rename_covid = {
    "Country/Region": "country_region",
    "country": "country_region",
    "date": "date",
    "total_cases": "total_cases",
    "total_deaths": "total_deaths",
    "total_recovered": "total_recovered",
    "total_gueris": "total_recovered",
    "id": "id"
}
df_covid = df_covid.rename(columns=rename_covid)
# Garder uniquement les colonnes attendues
covid_cols = ["country_region", "date", "total_cases", "total_deaths", "total_recovered"]
df_covid = df_covid[covid_cols]

try:
    df_covid.to_sql(
        "covid19_daily",
        engine,
        if_exists="append",
        index=False,
    )
    print(f" {len(df_covid)} lignes insérées dans covid19_daily")
except Exception as e:
    print(f" Erreur insertion covid19_daily : {e}")

# Mpox
mpox_path = os.path.join(cleaned_dir, "cleaned_mpox_dataset.csv")
df_mpox = pd.read_csv(mpox_path)
print(f"\nInjection MPOX depuis {mpox_path}…")

# Renommer les colonnes pour correspondre à la BDD
rename_mpox = {
    "Country/Region": "country_region",
    "country": "country_region",
    "date": "date",
    "total_cases": "total_cases",
    "total_deaths": "total_deaths",
    "total_recovered": "total_recovered",
    "total_gueris": "total_recovered",
    "id": "id"
}
df_mpox = df_mpox.rename(columns=rename_mpox)
# Garder uniquement les colonnes attendues
mpox_cols = ["country_region", "date", "total_cases", "total_deaths", "total_recovered"]
df_mpox = df_mpox[mpox_cols]

try:
    df_mpox.to_sql(
        "mpox",
        engine,
        if_exists="append",
        index=False,
    )
    print(f"{len(df_mpox)} lignes insérées dans mpox")
except Exception as e:
    print(f"Erreur insertion mpox : {e}")

print("\nStockage terminé.")
