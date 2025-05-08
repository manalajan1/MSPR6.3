# clean_and_standardize.py

import os
import pandas as pd

# Répertoires de données
base_dir   = os.getcwd()
data_dir   = os.path.join(base_dir, "data")
output_dir = os.path.join(base_dir, "cleaned_data")
os.makedirs(output_dir, exist_ok=True)

def clean_and_standardize(file_path, output_name, columns_map, relevant_columns, continents=None):
    """
    Nettoie et standardise le fichier CSV :
    - Conserve les colonnes pertinentes.
    - Remplace les valeurs manquantes par 0.
    - Renomme les colonnes selon columns_map.
    - Ajoute 'total_recovered' = total_cases - total_deaths.
    - Filtre pour le dernier jour du mois par pays.
    - Ajoute une colonne 'id' auto-incrémentée.
    """
    df = pd.read_csv(file_path)
    print(f"Nettoyage : {file_path}")

    # Sélection + valeurs manquantes
    df = df[relevant_columns].fillna(0)

    # Renommage initial
    df.rename(columns=columns_map, inplace=True)

    # Harmonisation du nom du pays
    if 'Country/Region' in df.columns:
        df.rename(columns={'Country/Region': 'country_region'}, inplace=True)

    # Conversion de la date
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)

    # Calcul uniformisé total_recovered
    df['total_recovered'] = df['total_cases'] - df['total_deaths']

    # Exclusion des continents si demandé
    if continents and 'country_region' in df.columns:
        df = df[~df['country_region'].isin(continents)]

    # Garder le dernier jour du mois
    df['year_month'] = df['date'].dt.to_period('M')
    df = df.sort_values('date').groupby(['country_region','year_month'], as_index=False).last()
    df.drop(columns=['year_month'], inplace=True)

    # ID auto-incrémenté
    df.insert(0, 'id', range(1, len(df) + 1))

    # Sauvegarde
    out_path = os.path.join(output_dir, output_name)
    df.to_csv(out_path, index=False)
    print(f"Enregistré : {out_path}")
    return df

# Continents à exclure (exemple)
continents_to_exclude = ["Africa","Asia","Europe","North America","South America","Oceania","Antarctica"]

# Mapping et colonnes COVID
columns_map_covid = {
    'date': 'date',
    'country': 'Country/Region',
    'cumulative_total_cases': 'total_cases',
    'cumulative_total_deaths': 'total_deaths'
}
relevant_covid = ['date','country','cumulative_total_cases','cumulative_total_deaths']

# Mapping et colonnes Mpox
columns_map_mpox = {
    'date': 'date',
    'location': 'Country/Region',
    'total_cases': 'total_cases',
    'total_deaths': 'total_deaths'
}
relevant_mpox = ['date','location','total_cases','total_deaths']

# Fichiers sources
covid_file = os.path.join(data_dir, 'worldometer_coronavirus_daily_data.csv')
mpox_file  = os.path.join(data_dir, 'owid-monkeypox-data.csv')

# Exécution
clean_and_standardize(covid_file, 'cleaned_covid19_daily_dataset.csv', columns_map_covid, relevant_covid, continents_to_exclude)
clean_and_standardize(mpox_file,  'cleaned_mpox_dataset.csv',                         columns_map_mpox,   relevant_mpox,   continents_to_exclude)
