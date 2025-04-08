import os
import pandas as pd

# Répertoires de données
data_dir = os.path.join(os.getcwd(), "data")
output_dir = os.path.join(os.getcwd(), "cleaned_data")
os.makedirs(output_dir, exist_ok=True)

def clean_and_standardize(file_path, output_name, columns_map, relevant_columns, continents=None):
    """
    Nettoie et standardise le fichier CSV.
    
    - Conserve uniquement les colonnes pertinentes.
    - Remplace les valeurs manquantes par 0.
    - Renomme les colonnes selon columns_map.
    - Ajoute une colonne 'Total_Gueris' calculée comme (Total_Cases - Total_Deaths).
    - Supprime les doublons.
    - Exclut les lignes correspondant aux continents (si la colonne 'Country/Region' est présente).
    - Filtre pour ne conserver que la ligne correspondant au dernier jour du mois pour chaque pays.
    """
    df = pd.read_csv(file_path)
    print(f"Nettoyage du fichier : {file_path}")
    
    # Diagnostic initial des colonnes
    print("Colonnes présentes :", df.columns.tolist())
    
    # Conserver uniquement les colonnes pertinentes
    df = df[relevant_columns]
    
    # Remplacer les valeurs manquantes par 0
    df.fillna(0, inplace=True)
    
    # Renommer les colonnes
    df.rename(columns=columns_map, inplace=True)
    
    # Conversion de la colonne Date en datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    if df['Date'].isna().sum() > 0:
        print("Attention : certaines dates n'ont pas pu être converties et seront ignorées.")
    
    # Ajout de la colonne 'Total_Gueris'
    # On fait l'hypothèse que le nombre de guéris est égal aux cas cumulés moins les décès cumulés
    if 'Total_Cases' in df.columns and 'Total_Deaths' in df.columns:
        df['Total_Gueris'] = df['Total_Cases'] - df['Total_Deaths']
    
    # Supprimer les doublons
    df.drop_duplicates(inplace=True)
    
    # Exclure les lignes correspondant aux continents si nécessaire
    if continents and 'Country/Region' in df.columns:
        initial_count = df.shape[0]
        df = df[~df['Country/Region'].isin(continents)]
        removed = initial_count - df.shape[0]
        print(f"{removed} lignes correspondant aux continents ont été supprimées.")
    
    # Filtrer pour ne conserver que la ligne correspondant au dernier jour disponible du mois pour chaque pays
    # On crée une colonne temporaire représentant l'année et le mois
    df['YearMonth'] = df['Date'].dt.to_period('M')
    
    before_grouping = df.shape[0]
    df = df.sort_values('Date').groupby(['Country/Region', 'YearMonth'], as_index=False).last()
    after_grouping = df.shape[0]
    print(f"Filtrage par dernier jour du mois : lignes avant regroupement = {before_grouping}, après = {after_grouping}")
    
    # Suppression de la colonne temporaire 'YearMonth'
    df.drop(columns=['YearMonth'], inplace=True)
    
    # Sauvegarder le dataset nettoyé
    output_path = os.path.join(output_dir, output_name)
    df.to_csv(output_path, index=False)
    print(f"Fichier nettoyé sauvegardé dans : {output_path}")
    
    return df

# Liste de continents à exclure (à adapter selon vos besoins)
continents_to_exclude = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania", "Antarctica"]

# Mapping pour le dataset COVID (données journalières)
columns_map_covid_daily = {
    'date': 'Date',
    'country': 'Country/Region',
    'cumulative_total_cases': 'Total_Cases',
    'cumulative_total_deaths': 'Total_Deaths'
}

# Mapping pour le dataset Mpox
columns_map_mpox = {
    'date': 'Date',
    'location': 'Country/Region',
    'total_cases': 'Total_Cases',
    'total_deaths': 'Total_Deaths'
}

# Colonnes pertinentes pour chaque dataset
relevant_columns_covid_daily = ['date', 'country', 'cumulative_total_cases', 'cumulative_total_deaths']
relevant_columns_mpox = ['date', 'location', 'total_cases', 'total_deaths']

# Fichiers d'entrée (assurez-vous que ces fichiers existent dans le dossier "data")
covid_input_file = os.path.join(data_dir, 'worldometer_coronavirus_daily_data.csv')
mpox_input_file = os.path.join(data_dir, 'owid-monkeypox-data.csv')

# Lancer le nettoyage et la standardisation en excluant les continents et en filtrant pour le dernier jour de chaque mois
clean_and_standardize(covid_input_file, 'cleaned_covid19_daily_dataset.csv', columns_map_covid_daily, relevant_columns_covid_daily, continents=continents_to_exclude)
clean_and_standardize(mpox_input_file, 'cleaned_mpox_dataset.csv', columns_map_mpox, relevant_columns_mpox, continents=continents_to_exclude)
