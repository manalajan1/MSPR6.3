# dashboard.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine

# -----------------------------------------------------------------------------
# Configuration de la page
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Dashboard COVID-19 & Mpox", layout="wide")

# -----------------------------------------------------------------------------
# Chargement de la configuration
# -----------------------------------------------------------------------------
load_dotenv()  # lit le .env à la racine ou dans env/
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.error("La variable d'environnement DATABASE_URL n'a pas été trouvée.")
    st.stop()

# -----------------------------------------------------------------------------
# Création du moteur SQLAlchemy
# -----------------------------------------------------------------------------
engine = create_engine(DATABASE_URL)

# -----------------------------------------------------------------------------
# Fonctions de chargement avec cache
# -----------------------------------------------------------------------------
@st.cache_data
def load_df_from_db(table_name: str) -> pd.DataFrame:
    query = f"SELECT * FROM {table_name};"
    try:
        df = pd.read_sql(query, con=engine)
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement de la table '{table_name}' : {e}")
        return pd.DataFrame()

# -----------------------------------------------------------------------------
# Chargement des données depuis la BDD
# -----------------------------------------------------------------------------
covid_df = load_df_from_db("covid19_daily")
mpox_df  = load_df_from_db("mpox")

# Vérifier que les DataFrames ne sont pas vides
if covid_df.empty or mpox_df.empty:
    st.error("Impossible de charger les données depuis la base PostgreSQL. Vérifiez vos tables.")
    st.stop()

# -----------------------------------------------------------------------------
# Calculs globaux (exemple basé sur COVID-19)
# -----------------------------------------------------------------------------
global_cases     = int(covid_df["Total_Cases"].sum())
global_deaths    = int(covid_df["Total_Deaths"].sum())
global_survivors = int(covid_df["Total_Gueris"].sum())

# -----------------------------------------------------------------------------
# Affichage des indicateurs globaux
# -----------------------------------------------------------------------------
st.markdown("<h3 style='text-align: center; margin-bottom: 5px;'>🌍 Tableau de Bord COVID-19 & Mpox</h3>", unsafe_allow_html=True)

with st.container():
    col1, col2, col3 = st.columns(3)
    col1.metric("🌍 Total Cas", f"{global_cases:,}")
    col2.metric("✅ Survivants", f"{global_survivors:,}")
    col3.metric("⚠️ Décès", f"{global_deaths:,}")

st.markdown("---")

# -----------------------------------------------------------------------------
# Disposition principale : Comparaison, Carte, Détails par pays
# -----------------------------------------------------------------------------
with st.container():
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    
    # 1. Comparaison des pays
    with col_left:
        st.subheader("📊 Comparaison des Pays")
        countries = covid_df["Country/Region"].unique()
        selected_countries = st.multiselect("Sélectionnez des pays :", countries, default=["France", "Germany"])
        comp_df = covid_df[covid_df["Country/Region"].isin(selected_countries)]
        fig_comparison = px.line(
            comp_df,
            x="Date",
            y="Total_Cases",
            color="Country/Region",
            title="Évolution des Cas"
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # 2. Carte des cas
    with col_mid:
        st.subheader("🗺️ Carte des Cas")
        fig_map = px.choropleth(
            covid_df,
            locations="Country/Region",
            locationmode="country names",
            color="Total_Cases",
            hover_name="Country/Region",
            color_continuous_scale="Blues",
            title="Distribution Géographique des Cas"
        )
        st.plotly_chart(fig_map, use_container_width=True)
    
    # 3. Détails par pays
    with col_right:
        st.subheader("⚙️ Détails par Pays")
        disease = st.selectbox("Sélectionnez la maladie :", ["COVID-19", "Mpox"])
        df = covid_df if disease == "COVID-19" else mpox_df
        country = st.selectbox("Sélectionnez un pays :", df["Country/Region"].unique())
        filtered_df = df[df["Country/Region"] == country]
        
        # Graphique Cas
        st.markdown(f"### 📈 Évolution des Cas pour {country}")
        fig_cases = px.line(filtered_df, x="Date", y="Total_Cases")
        st.plotly_chart(fig_cases, use_container_width=True)
        
        # Graphique Décès
        st.markdown(f"### 📈 Évolution des Décès pour {country}")
        fig_deaths = px.line(filtered_df, x="Date", y="Total_Deaths")
        st.plotly_chart(fig_deaths, use_container_width=True)
