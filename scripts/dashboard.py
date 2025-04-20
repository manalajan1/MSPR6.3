
# mspr6.1/scripts/dashboard.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- Config Streamlit ---
st.set_page_config(page_title="Dashboard COVID-19 & Mpox", layout="wide")

# --- Charger .env et créer le moteur ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.error("🚨 La variable DATABASE_URL n'a pas été trouvée dans .env")
    st.stop()
engine = create_engine(DATABASE_URL)

# --- Fonction cache pour charger les tables ---
@st.cache_data
def load_table(table_name: str) -> pd.DataFrame:
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name};", con=engine)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        st.error(f"Erreur SQL sur '{table_name}': {e}")
        return pd.DataFrame()

# --- Chargement depuis la BDD ---
covid_df = load_table("covid19_daily")
mpox_df  = load_table("mpox")
if covid_df.empty or mpox_df.empty:
    st.error("Aucune donnée chargée depuis la BDD. Vérifiez vos tables.")
    st.stop()

# --- Choix de la maladie et préparation des données ---
maladie = st.radio("Sélectionnez la maladie :", ["COVID-19", "Mpox"], horizontal=True)
df = covid_df if maladie == "COVID-19" else mpox_df

# Table des dernières valeurs par pays pour calculs globaux et carte
df_latest = (
    df.sort_values('Date')
      .groupby('Country/Region', as_index=False)
      .last()
)

# --- Calculs globaux ---
global_cases     = int(df_latest["Total_Cases"].sum())
global_deaths    = int(df_latest["Total_Deaths"].sum())
global_survivors = int(df_latest["Total_Gueris"].sum())

# --- Affichage des indicateurs globaux ---
st.markdown(f"## 🌍 Tableau de Bord {maladie}", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Total Cas",  f"{global_cases:,}")
col2.metric("Survivants", f"{global_survivors:,}")
col3.metric("Décès",      f"{global_deaths:,}")
st.markdown("---")

# --- Disposition principale : comparaison, carte, détails ---
left, mid, right = st.columns([1, 2, 1])

with left:
    st.subheader("📊 Comparaison des pays")
    pays = df["Country/Region"].unique()
    sel = st.multiselect("Pays :", pays, default=[pays[0], pays[1] if len(pays)>1 else pays[0]])
    comp_df = df[df["Country/Region"].isin(sel)]
    fig = px.line(
        comp_df,
        x="Date",
        y="Total_Cases",
        color="Country/Region",
        title="Évolution des cas"
    )
    st.plotly_chart(fig, use_container_width=True)

with mid:
    st.subheader("🗺️ Carte des cas")
    fig_map = px.choropleth(
        df_latest,
        locations="Country/Region",
        locationmode="country names",
        color="Total_Cases",
        hover_name="Country/Region",
        color_continuous_scale="Blues",
        title="Distribution géographique des derniers cas"
    )
    st.plotly_chart(fig_map, use_container_width=True)

with right:
    st.subheader("⚙️ Détails par pays")
    pays_sel = st.selectbox("Pays :", df["Country/Region"].unique())
    filt = df[df["Country/Region"] == pays_sel]

    st.markdown(f"### 📈 Évolution des cas pour {pays_sel}")
    fig_cases = px.line(filt, x="Date", y="Total_Cases", title="Cas")
    st.plotly_chart(fig_cases, use_container_width=True)

    st.markdown(f"### 📈 Évolution des décès pour {pays_sel}")
    fig_deaths = px.line(filt, x="Date", y="Total_Deaths", title="Décès")
    st.plotly_chart(fig_deaths, use_container_width=True)


