
import os
import pandas as pd

# Répertoires de données
base_dir = os.getcwd()
data_dir = os.path.join(base_dir, "data")
output_dir = os.path.join(base_dir, "cleaned_data")
os.makedirs(output_dir, exist_ok=True)

# Fonction de nettoyage et d'ajout de l'ID
def clean_and_standardize(file_path, output_name, columns_map, relevant_columns, continents=None):
    """
    Nettoie et standardise le fichier CSV :
    - Conserve les colonnes pertinentes.
    - Remplace les valeurs manquantes par 0.
    - Renomme les colonnes selon columns_map.
    - Ajoute 'Total_Gueris' = Total_Cases - Total_Deaths.
    - Filtre pour le dernier jour du mois par pays.
    - Ajoute une colonne 'id' auto-incrémentée.
    """
    # Lecture
    df = pd.read_csv(file_path)
    print(f"Nettoyage : {file_path}")

    # Sélection des colonnes
    df = df[relevant_columns]
    df.fillna(0, inplace=True)
    df.rename(columns=columns_map, inplace=True)

    # Conversion date
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)

    # Calcul Total_Gueris
    df['Total_Gueris'] = df['Total_Cases'] - df['Total_Deaths']

    # Exclusion continents
    if continents and 'Country/Region' in df.columns:
        df = df[~df['Country/Region'].isin(continents)]

    # Filtre dernier jour du mois
    df['YearMonth'] = df['Date'].dt.to_period('M')
    df = df.sort_values('Date')
    df = df.groupby(['Country/Region','YearMonth'], as_index=False).last()
    df.drop(columns=['YearMonth'], inplace=True)

    # Ajout de l'ID unique
    df.insert(0, 'id', range(1, len(df) + 1))

    # Sauvegarde
    out_path = os.path.join(output_dir, output_name)
    df.to_csv(out_path, index=False)
    print(f"Enregistré : {out_path}")
    return df

# Exclusion continents
continents_to_exclude = ["Africa","Asia","Europe","North America","South America","Oceania","Antarctica"]

# Mapping COVID
columns_map_covid_daily = {
    'date':'Date', 'country':'Country/Region',
    'cumulative_total_cases':'Total_Cases','cumulative_total_deaths':'Total_Deaths'
}
relevant_columns_covid_daily = ['date','country','cumulative_total_cases','cumulative_total_deaths']

# Mapping Mpox
columns_map_mpox = {
    'date':'Date','location':'Country/Region',
    'total_cases':'Total_Cases','total_deaths':'Total_Deaths'
}
relevant_columns_mpox = ['date','location','total_cases','total_deaths']

# Fichiers bruts
covid_file = os.path.join(data_dir,'worldometer_coronavirus_daily_data.csv')
mpox_file  = os.path.join(data_dir,'owid-monkeypox-data.csv')

# Exécution
clean_and_standardize(covid_file,'cleaned_covid19_daily_dataset.csv',columns_map_covid_daily,relevant_columns_covid_daily,continents_to_exclude)
clean_and_standardize(mpox_file,'cleaned_mpox_dataset.csv',columns_map_mpox,relevant_columns_mpox,continents_to_exclude)
