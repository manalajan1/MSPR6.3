# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Dashboard COVID-19 & Mpox", layout="wide")

# Fonction de chargement avec cache pour éviter des rechargements inutiles
@st.cache_data
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier {file_path}: {e}")
        return pd.DataFrame()

# Charger les datasets nettoyés à partir du dossier "cleaned_data"
covid_df = load_data("cleaned_data/cleaned_covid19_daily_dataset.csv")
mpox_df = load_data("cleaned_data/cleaned_mpox_dataset.csv")

# Vérifier que les DataFrames ne sont pas vides
if covid_df.empty or mpox_df.empty:
    st.error("Un ou plusieurs fichiers de données ne peuvent être chargés. Veuillez vérifier le dossier 'cleaned_data'.")
    st.stop()

# Calculs globaux (exemple basé sur COVID)
global_cases = covid_df["Total_Cases"].sum()
global_deaths = covid_df["Total_Deaths"].sum()
global_survivors = covid_df["Total_Gueris"].sum()  # Ici on utilise la colonne Total_Gueris

# Titre principal
st.markdown("<h3 style='text-align: center; margin-bottom: 5px;'>🌍 Tableau de Bord COVID-19 & Mpox</h3>", unsafe_allow_html=True)

# Indicateurs globaux
with st.container():
    col1, col2, col3 = st.columns(3)
    col1.markdown(
        f"<div style='text-align: center; padding: 3px; border-radius: 8px; background-color: #f0f2f6;'>"
        f"<h6 style='color: orange; margin-bottom: 0;'>🌍 Total Cas</h6>"
        f"<h5 style='color: orange; margin-top: 0;'>{global_cases:,}</h5>"
        f"</div>", unsafe_allow_html=True)
    
    col2.markdown(
        f"<div style='text-align: center; padding: 3px; border-radius: 8px; background-color: #f0f2f6;'>"
        f"<h6 style='color: green; margin-bottom: 0;'>✅ Survivants</h6>"
        f"<h5 style='color: green; margin-top: 0;'>{global_survivors:,}</h5>"
        f"</div>", unsafe_allow_html=True)
    
    col3.markdown(
        f"<div style='text-align: center; padding: 3px; border-radius: 8px; background-color: #f0f2f6;'>"
        f"<h6 style='color: red; margin-bottom: 0;'>⚠️ Décès</h6>"
        f"<h5 style='color: red; margin-top: 0;'>{global_deaths:,}</h5>"
        f"</div>", unsafe_allow_html=True)

st.markdown("---")

# Disposition principale
with st.container():
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    
    # Comparaison des pays
    with col_left:
        st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>📊 Comparaison des Pays</h4>", unsafe_allow_html=True)
        selected_countries = st.multiselect("Sélectionnez des pays :", covid_df["Country/Region"].unique(), default=["France", "Germany"])
        comp_df = covid_df[covid_df["Country/Region"].isin(selected_countries)]
        fig_comparison = px.line(comp_df, x="Date", y="Total_Cases", color="Country/Region", title="Évolution des Cas")
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Carte des cas
    with col_mid:
        st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>🗺️ Carte des Cas</h4>", unsafe_allow_html=True)
        disease_map = px.choropleth(covid_df,
                                    locations="Country/Region",
                                    locationmode="country names",
                                    color="Total_Cases",
                                    hover_name="Country/Region",
                                    color_continuous_scale="Blues",
                                    title="Distribution Géographique des Cas")
        st.plotly_chart(disease_map, use_container_width=True)
    
    # Paramètres et graphiques détaillés
    with col_right:
        st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>⚙️ Détails par Pays</h4>", unsafe_allow_html=True)
        disease = st.radio("Sélectionnez la maladie :", ["COVID-19", "Mpox"], horizontal=False)
        df = covid_df if disease == "COVID-19" else mpox_df
        selected_country = st.selectbox("Sélectionnez un pays :", df["Country/Region"].unique())
        filtered_df = df[df["Country/Region"] == selected_country]
        
        st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>📈 Évolution des Cas</h4>", unsafe_allow_html=True)
        fig_cases = px.line(filtered_df, x="Date", y="Total_Cases", title=f"Cas pour {selected_country}")
        fig_cases.update_traces(line=dict(color="blue"))
        st.plotly_chart(fig_cases, use_container_width=True)
        
        st.markdown("<h4 style='text-align: center; margin-bottom: 10px;'>📈 Évolution des Décès</h4>", unsafe_allow_html=True)
        fig_deaths = px.line(filtered_df, x="Date", y="Total_Deaths", title=f"Décès pour {selected_country}")
        fig_deaths.update_traces(line=dict(color="red"))
        st.plotly_chart(fig_deaths, use_container_width=True)
