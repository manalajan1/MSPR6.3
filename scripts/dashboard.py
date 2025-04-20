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
        return pd.read_sql(f"SELECT * FROM {table_name};", con=engine)
    except Exception as e:
        st.error(f"Erreur SQL sur '{table_name}': {e}")
        return pd.DataFrame()

# --- Chargement depuis la BDD ---
covid_df = load_table("covid19_daily")
mpox_df  = load_table("mpox")
if covid_df.empty or mpox_df.empty:
    st.error("Aucune donnée chargée depuis la BDD. Vérifiez vos tables.")
    st.stop()

# --- Calculs globaux ---
global_cases     = int(covid_df["Total_Cases"].sum())
global_deaths    = int(covid_df["Total_Deaths"].sum())
global_survivors = int(covid_df["Total_Gueris"].sum())

# --- Indicateurs ---
st.markdown("## 🌍 Tableau de Bord COVID-19 & Mpox", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Total Cas",     f"{global_cases:,}")
col2.metric("Survivants",    f"{global_survivors:,}")
col3.metric("Décès",         f"{global_deaths:,}")
st.markdown("---")

# --- Disposition principale ---
left, mid, right = st.columns([1,2,1])

with left:
    st.subheader("📊 Comparaison des Pays")
    pays = covid_df["Country/Region"].unique()
    sel = st.multiselect("Pays :", pays, default=["France","Germany"])
    dfc = covid_df[covid_df["Country/Region"].isin(sel)]
    fig = px.line(dfc, x="Date", y="Total_Cases", color="Country/Region")
    st.plotly_chart(fig, use_container_width=True)

with mid:
    st.subheader("🗺️ Carte des Cas")
    fig = px.choropleth(covid_df,
                        locations="Country/Region",
                        locationmode="country names",
                        color="Total_Cases",
                        hover_name="Country/Region",
                        title="Distribution Géographique des Cas")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("⚙️ Détails par Pays")
    maladie = st.radio("Maladie :", ["COVID-19","Mpox"])
    df = covid_df if maladie=="COVID-19" else mpox_df
    pays_sel = st.selectbox("Pays :", df["Country/Region"].unique())
    filt = df[df["Country/Region"]==pays_sel]
    st.markdown(f"### Évolution des Cas ({pays_sel})")
    st.plotly_chart(px.line(filt, x="Date", y="Total_Cases"), use_container_width=True)
    st.markdown(f"### Évolution des Décès ({pays_sel})")
    st.plotly_chart(px.line(filt, x="Date", y="Total_Deaths"), use_container_width=True)
