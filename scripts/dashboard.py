import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine
import requests

# --- Modern CSS & Responsive ---
st.markdown(
    """
    <style>
    body, .main-header {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 1.1rem;
    }
    .main-header {
        text-align: center;
        font-size: 2.7rem;
        margin-top: 1rem;
        font-weight: bold;
        color: #1976d2;
    }
    .main-sub {
        text-align: center;
        font-size: 1.2rem;
        color: #444;
        margin-bottom: 1.5rem;
    }
    .card {
        background: #f5f7fa;
        border-radius: 1rem;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        text-align: center;
    }
    .section-header {
        font-size: 1.5rem;
        margin-top: 2rem;
        font-weight: 600;
        color: #1976d2;
    }
    .stMetric-value {
        font-size: 1.3rem !important;
    }
    .stTabs [role="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1976d2;
        background: #f5f7fa;
        border-radius: 8px 8px 0 0;
        margin-right: 0.5rem;
        padding: 0.7rem 1.5rem;
        border: none;
        outline: none;
    }
    .stTabs [aria-selected="true"] {
        background: #1976d2;
        color: #fff;
    }
    *:focus {
        outline: 2px solid #1976d2 !important;
        outline-offset: 2px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Header ---
st.markdown("""
<div class='main-header'>Dashboard COVID-19 &amp; Mpox</div>
<div class='main-sub'>Analyse, prédiction et visualisation interactive pour tous. Sélectionnez vos filtres à gauche et naviguez par le menu ci-dessus.</div>
""", unsafe_allow_html=True)

# --- Menu horizontal (onglets) ---
tabs = st.tabs(["Accueil", "Visualisations", "Prédiction IA", "À propos"])

# --- Sidebar (Filtres principaux) ---
st.sidebar.title("Filtres principaux")
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.sidebar.error("DATABASE_URL introuvable")
    st.stop()
engine = create_engine(DATABASE_URL)

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

covid_df = load_table('covid19_daily')
mpox_df  = load_table('mpox')

maladie = st.sidebar.radio("Maladie", ["COVID-19", "Mpox"], index=0)
df_dates = covid_df if maladie == "COVID-19" else mpox_df
min_date = df_dates['date'].min().date()
max_date = df_dates['date'].max().date()
periode = st.sidebar.date_input("Période", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(periode, tuple) and len(periode) == 2:
    date_debut, date_fin = periode
else:
    date_debut, date_fin = min_date, max_date
all_countries = sorted(df_dates['country'].dropna().unique())
pays_sel = st.sidebar.multiselect("Pays", all_countries, default=all_countries[:3])

raw_df = covid_df if maladie == 'COVID-19' else mpox_df
mask = (
    (raw_df['date'] >= pd.to_datetime(date_debut)) &
    (raw_df['date'] <= pd.to_datetime(date_fin)) &
    (raw_df['country'].isin(pays_sel))
)
filtered_df = raw_df[mask]
latest_df = filtered_df.sort_values('date').groupby('country', as_index=False).last()

# --- Accueil ---
with tabs[0]:
    st.markdown("<div class='section-header'>Indicateurs globaux</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("Total Cas", f"{int(latest_df['total_cases'].sum()):,}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("Guéris", f"{int(latest_df['total_recovered'].sum()):,}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("Décès", f"{int(latest_df['total_deaths'].sum()):,}")
        st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    st.caption("Ces indicateurs sont calculés sur la période et les pays sélectionnés.")

# --- Visualisations ---
with tabs[1]:
    st.markdown("<div class='section-header'>Visualisations interactives</div>", unsafe_allow_html=True)
    visu_type = st.radio("Type de visualisation", ["Carte des cas", "Comparaison des pays", "Détails par pays"], horizontal=True)
    if visu_type == "Comparaison des pays":
        countries = sorted(filtered_df['country'].dropna().unique())
        sel = st.multiselect("Sélectionner pays à comparer", countries, default=countries[:3])
        if sel:
            comp_df = filtered_df[filtered_df['country'].isin(sel)]
            fig = px.line(comp_df, x='date', y='total_cases', color='country', title='Évolution des cas',
                          color_discrete_sequence=px.colors.qualitative.Set1)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Courbe d'évolution des cas pour les pays sélectionnés.")
    elif visu_type == "Détails par pays":
        pays_unique = sorted(filtered_df['country'].unique())
        pays = st.selectbox("Pays", pays_unique)
        filt = filtered_df[filtered_df['country'] == pays]
        fig1 = px.area(filt, x='date', y='total_cases', title=f'Cas pour {pays}', color_discrete_sequence=['#1976d2'])
        fig2 = px.bar(filt, x='date', y='total_deaths', title=f'Décès pour {pays}', color_discrete_sequence=['#d32f2f'])
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption(f"Détail des cas et décès pour {pays} sur la période sélectionnée.")
    else:
        metric = st.radio("Métrique", ["Décès", "Guéris"], horizontal=True)
        if metric == "Décès":
            color_col, scale, title = 'total_deaths', 'Reds', 'Décès par pays'
        else:
            color_col, scale, title = 'total_recovered', 'Greens', 'Guéris par pays'
        fig_map = px.choropleth(latest_df, locations='country', locationmode='country names',
                                color=color_col, hover_name='country',
                                color_continuous_scale=scale, title=title)
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption("Carte mondiale des cas cumulés sur la période et les pays sélectionnés.")

# --- Fonction prédiction batch (API IA) ---
def predict_batch(df):
    url = "http://localhost:8000/predict"
    preds = []
    for _, row in df.iterrows():
        data = {
            "total_deaths": int(row.get("total_deaths", 0)),
            "total_recovered": int(row.get("total_recovered", 0))
        }
        try:
            r = requests.post(url, json=data, timeout=2)
            if r.status_code == 200:
                res = r.json()
                preds.append(res["probability"])
            else:
                preds.append(None)
        except Exception:
            preds.append(None)
    return preds

# --- Prédiction IA ---
with tabs[2]:
    st.markdown("<div class='section-header'>Prédiction IA interactive</div>", unsafe_allow_html=True)
    st.info("Lancez la prédiction IA sur la période et les pays sélectionnés. Les résultats sont expliqués de façon simple.")
    pred_df = latest_df.copy()
    if len(pred_df) == 0:
        st.warning("Aucune donnée à prédire pour la période et les pays sélectionnés.")
    else:
        if st.button("Lancer la prédiction IA", type="primary"):
            with st.spinner("Calcul des prédictions IA..."):
                pred_df["proba_pred"] = predict_batch(pred_df)
            if pred_df["proba_pred"].notnull().any() and (pred_df["proba_pred"].dropna() != None).any():
                fig_pred = px.bar(
                    pred_df, x="country", y="proba_pred",
                    title="Probabilité d'avoir > 10 000 cas (par pays)",
                    labels={"proba_pred": "Proba prédite"},
                    color="proba_pred",
                    color_continuous_scale=px.colors.sequential.Blues,
                    hover_data={"country": True, "proba_pred": ':.2f'}
                )
                st.plotly_chart(fig_pred, use_container_width=True)
                st.caption("Ce graphique montre la probabilité prédite par l'IA d'avoir plus de 10 000 cas pour chaque pays sélectionné. Plus la barre est foncée, plus le risque est élevé.")
                for _, row in pred_df.iterrows():
                    if pd.notnull(row["proba_pred"]):
                        st.write(f"{row['country']} : {row['proba_pred']*100:.1f}% de chances d'avoir > 10 000 cas")
                st.download_button("Télécharger les prédictions IA (CSV)", pred_df.to_csv(index=False), "predictions_ia.csv")
            else:
                st.error("Aucune prédiction IA n'a pu être calculée (API non disponible ou erreur de données).")

# --- À propos / Aide ---
with tabs[3]:
    st.markdown("<div class='section-header'>À propos & Aide</div>", unsafe_allow_html=True)
    st.write("""
    - **Dashboard développé pour l'analyse et la prédiction COVID-19 & Mpox**
    - **Design responsive** : fonctionne sur ordinateur, tablette, mobile
    - **Accessibilité** : navigation clavier, contraste élevé, polices lisibles
    - **Graphiques interactifs** : zoom, export, tooltips
    - **Prédictions IA** : explications simples, code couleur, export CSV
    - **Contact** : [Votre email ou lien GitHub]
    """)
    st.info("Pour toute question ou suggestion, contactez l'équipe projet.")
