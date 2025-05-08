import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- Config Streamlit ---
st.set_page_config(page_title="Dashboard COVID-19 & Mpox", layout="wide", initial_sidebar_state="expanded")

# --- Styles CSS personnalisés ---
st.markdown(
    """
    <style>
    .main-header {
        text-align: center;
        font-size: 2.5rem;
        margin-top: 1rem;
        font-weight: bold;
    }

    .metric-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 1rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    .section-header {
        font-size: 1.75rem;
        margin-top: 2rem;
        font-weight: 600;
    }

    .stMetric-value {
        font-size: 1.5rem !important;
    }

    /* Sidebar custom background */
    [data-testid="stSidebar"] {
        background-color: #1e1e1e !important;
        color: white !important;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
    }

    .stSidebar label, .stRadio label, .stSelectbox label {
        color: white !important;
        font-weight: 500;
    }

    .stSelectbox, .stRadio, .stMultiselect {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 0.5rem;
        color: white;
    }

    .stSelectbox div, .stRadio div, .stMultiselect div {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar controls ---
st.sidebar.title(" Filtres et options")
maladie = st.sidebar.radio("Maladie:", ["COVID-19", "Mpox"], index=0)
visu_type = st.sidebar.selectbox("Visualisation:", ["Carte des cas", "Comparaison des pays", "Détails par pays"], index=0)

# --- Charger .env et créer le moteur ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.sidebar.error("DATABASE_URL introuvable")
    st.stop()
engine = create_engine(DATABASE_URL)

# --- Fonction cache pour charger les tables ---
@st.cache_data
def load_table(table_name: str) -> pd.DataFrame:
    df = pd.read_sql(f"SELECT * FROM {table_name};", con=engine)
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    for col in df.columns:
        if col.startswith('country'):
            df.rename(columns={col: 'country'}, inplace=True)
            break
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

# --- Chargement des données ---
covid_df = load_table('covid19_daily')
mpox_df  = load_table('mpox')
raw_df = covid_df if maladie == 'COVID-19' else mpox_df
latest_df = raw_df.sort_values('date').groupby('country', as_index=False).last()

# --- Header ---
st.markdown(f"<div class='main-header'>Dashboard {maladie}</div>", unsafe_allow_html=True)

# --- Indicateurs globaux stylés ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='metric-box' style='border-left: 5px solid orange;'>", unsafe_allow_html=True)
    st.metric("Total Cas", f"{int(latest_df['total_cases'].sum()):,}")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-box' style='border-left: 5px solid green;'>", unsafe_allow_html=True)
    st.metric("Gueris", f"{int(latest_df['total_gueris'].sum()):,}")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='metric-box' style='border-left: 5px solid red;'>", unsafe_allow_html=True)
    st.metric("Deces", f"{int(latest_df['total_deaths'].sum()):,}")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- Visualisation ---
if visu_type == "Comparaison des pays":
    st.markdown("<div class='section-header'>Comparaison des pays</div>", unsafe_allow_html=True)
    countries = sorted(raw_df['country'].dropna().unique())
    sel = st.multiselect("Sélectionner pays", countries, default=countries[:3])
    if sel:
        comp_df = raw_df[raw_df['country'].isin(sel)]
        fig = px.line(comp_df, x='date', y='total_cases', color='country', title='Évolution des cas')
        st.plotly_chart(fig, use_container_width=True)

elif visu_type == "Détails par pays":
    st.markdown("<div class='section-header'>Détails par pays</div>", unsafe_allow_html=True)
    pays_sel = st.selectbox("Pays", sorted(raw_df['country'].unique()))
    filt = raw_df[raw_df['country'] == pays_sel]
    fig1 = px.area(filt, x='date', y='total_cases', title=f'Cas pour {pays_sel}')
    fig2 = px.bar(filt, x='date', y='total_deaths', title=f'Deces pour {pays_sel}')
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.markdown("<div class='section-header'>Carte des cas</div>", unsafe_allow_html=True)
    metric = st.radio("Métrique", ["Deces", "Gueris"], horizontal=True)
    if metric == "Deces":
        color_col, scale, title = 'total_deaths', 'Reds', 'Décès par pays'
    else:
        color_col, scale, title = 'total_gueris', 'Greens', 'Guéris par pays'
    fig_map = px.choropleth(latest_df, locations='country', locationmode='country names',
                            color=color_col, hover_name='country',
                            color_continuous_scale=scale, title=title)
    st.plotly_chart(fig_map, use_container_width=True)
