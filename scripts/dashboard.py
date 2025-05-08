# mspr6.1/scripts/dashboard.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- Config Streamlit ---
st.set_page_config(page_title="Dashboard COVID-19 & Mpox", layout="wide")

# --- Styles CSS personnalisés ---
st.markdown(
    """
    <style>
    .main-header { text-align: center; font-size: 2.5rem; margin-top: 1rem; }
    .metric-box { background: #f9fafb; border-radius: 0.75rem; padding: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .section-header { font-size: 1.5rem; margin-top: 1rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Charger .env et créer le moteur ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.error(" La variable DATABASE_URL n'a pas été trouvée dans .env")
    st.stop()
engine = create_engine(DATABASE_URL)

# --- Fonction cache pour charger les tables ---
@st.cache_data
def load_table(table_name: str) -> pd.DataFrame:
    df = pd.read_sql(f"SELECT * FROM {table_name};", con=engine)
    for col in df.columns:
        if col.lower().replace('_','').startswith('country'):
            df.rename(columns={col:'Country'}, inplace=True)
            break
    for col in df.columns:
        if col.lower()=='date':
            df['Date']=pd.to_datetime(df[col], errors='coerce')
            break
    return df

# --- Chargement des données ---
covid_df = load_table('covid19_daily')
mpox_df  = load_table('mpox')
if covid_df.empty or mpox_df.empty:
    st.error("Aucune donnée chargée depuis la BDD. Vérifiez vos tables.")
    st.stop()

# --- Sélection de la maladie ---
maladie = st.radio(
    "Sélectionnez la maladie :",
    ["COVID-19", "Mpox"],
    horizontal=True,
    label_visibility="collapsed"
)
raw_df = covid_df if maladie=='COVID-19' else mpox_df

# --- Dernier cumul par pays ---
latest_df = raw_df.sort_values('Date').groupby('Country', as_index=False).last()

# --- Indicateurs globaux ---
title_html = f"<div class='main-header'> Tableau de Bord  {maladie}</div>"
st.markdown(title_html, unsafe_allow_html=True)

total_col1, total_col2, total_col3 = st.columns(3)
with total_col1:
    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
    st.metric("Total Cas", f"{int(latest_df['Total_Cases'].sum()):,}")
    st.markdown("</div>", unsafe_allow_html=True)
with total_col2:
    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
    st.metric("Survivants", f"{int(latest_df['Total_Gueris'].sum()):,}")
    st.markdown("</div>", unsafe_allow_html=True)
with total_col3:
    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
    st.metric("Décès", f"{int(latest_df['Total_Deaths'].sum()):,}")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- Choix du type de visualisation ---
visu_type = st.selectbox(
    " Choisissez la visualisation :",
    ["Carte des cas", "Comparaison des pays", "Détails par pays"],
    index=0
)

# --- Affichage conditionnel ---
if visu_type == "Comparaison des pays":
    st.markdown("<div class='section-header'> Comparaison des pays</div>", unsafe_allow_html=True)
    countries = sorted(raw_df['Country'].dropna().unique())
    sel = st.multiselect("Pays :", countries, default=countries[:2])
    if sel:
        comp_df = raw_df[raw_df['Country'].isin(sel)]
        fig = px.line(comp_df, x='Date', y='Total_Cases', color='Country', title='Évolution des cas')
        st.plotly_chart(fig, use_container_width=True)
elif visu_type == "Détails par pays":
    st.markdown("<div class='section-header'> Détails par pays</div>", unsafe_allow_html=True)
    pays_sel = st.selectbox("Pays :", sorted(raw_df['Country'].unique()))
    filt = raw_df[raw_df['Country']==pays_sel]
    st.plotly_chart(px.line(filt, x='Date', y='Total_Cases', title=f'Cas pour {pays_sel}'), use_container_width=True)
    st.plotly_chart(px.line(filt, x='Date', y='Total_Deaths', title=f'Décès pour {pays_sel}'), use_container_width=True)
else:
    st.markdown("<div class='section-header'> Carte des cas</div>", unsafe_allow_html=True)
    # Choix métrique carte
    metric = st.radio("Métrique :", ["Décès", "Guéris"], horizontal=True)
    if metric == "Décès":
        color_col = 'Total_Deaths'
        scale = 'Reds'
        title = 'Cartographie des décès par pays'
    else:
        color_col = 'Total_Gueris'
        scale = 'Greens'
        title = 'Cartographie des guérisons par pays'

    fig_map = px.choropleth(
        latest_df,
        locations='Country',
        locationmode='country names',
        color=color_col,
        hover_name='Country',
        color_continuous_scale=scale,
        title=title
    )
    st.plotly_chart(fig_map, use_container_width=True)

