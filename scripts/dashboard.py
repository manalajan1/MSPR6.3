import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine
from prophet import Prophet
from sklearn.metrics import mean_absolute_error
import plotly.graph_objs as go
import requests

# --- Modern CSS & Responsive ---
st.markdown(
    """
    <style>
    body, .main-header {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 1.1rem;
        background: #23272b;
    }
    .main-header {
        text-align: center;
        font-size: 2.7rem;
        margin-top: 1rem;
        font-weight: bold;
        color: #fff;
        letter-spacing: 1px;
    }
    .main-sub {
        text-align: center;
        font-size: 1.2rem;
        color: #e0e6ed;
        margin-bottom: 1.5rem;
    }
    .card, .kpi-card {
        background: linear-gradient(135deg, #2c3440 0%, #3a4252 100%);
        border-radius: 1rem;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(255,255,255,0.07);
        text-align: center;
        color: #fff;
    }
    .kpi-title {
        font-size: 1.1rem;
        color: #fff;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 2.1rem;
        font-weight: bold;
        color: #fff;
    }
    .kpi-desc {
        font-size: 0.95rem;
        color: #bbb;
        margin-top: 0.3rem;
    }
    .section-header {
        font-size: 1.5rem;
        margin-top: 2rem;
        font-weight: 600;
        color: #fff;
    }
    .stMetric-value {
        font-size: 1.3rem !important;
    }
    .stTabs [role="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
        background: #2c3440;
        border-radius: 8px 8px 0 0;
        margin-right: 0.5rem;
        padding: 0.7rem 1.5rem;
        border: none;
        outline: none;
        transition: background 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: #fff;
        color: #23272b;
    }
    .stDataFrame th, .stDataFrame td {
        font-size: 1rem;
        color: #fff;
        background: #2c3440;
    }
    *:focus {
        outline: 2px solid #fff !important;
        outline-offset: 2px;
    }
    @media (max-width: 900px) {
        .kpi-card { min-width: 120px; min-height: 90px; padding: 1rem 0.5rem; }
        .main-header { font-size: 2rem; }
        .section-header { font-size: 1.1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Header ---
st.markdown("""
<div class='main-header' style='background: linear-gradient(90deg, #23272b 0%, #1e3a5c 100%); border-radius: 1.2rem; padding: 1.2rem 0; margin-bottom: 0.5rem; box-shadow: 0 2px 8px rgba(30,58,92,0.10); color: #fff;'>
Dashboard COVID-19 &amp; Mpox
</div>
<div class='main-sub'>Analyse, prédiction et visualisation interactive pour tous. Sélectionnez vos filtres à gauche et naviguez par le menu ci-dessus.</div>
""", unsafe_allow_html=True)

# --- Menu horizontal (onglets) ---
tabs = st.tabs(["Accueil", "Visualisations", "Prédiction IA", "Tableau de données",  "À propos"])

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

all_countries = sorted(df_dates['country'].dropna().unique())
pays_sel = st.sidebar.multiselect("Pays", all_countries, default=all_countries[:3])

raw_df = covid_df if maladie == 'COVID-19' else mpox_df
mask = raw_df['country'].isin(pays_sel)
filtered_df = raw_df[mask]
latest_df = filtered_df.sort_values('date').groupby('country', as_index=False).last()

# --- Accueil / KPI ---
with tabs[0]:
    st.markdown("<div class='section-header'>Résumé des indicateurs clés</div>", unsafe_allow_html=True)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown("<div class='kpi-card'><div class='kpi-title'>Total Cas</div><div class='kpi-value'>{:,}</div><div class='kpi-desc'>Nombre cumulé de cas</div></div>".format(int(latest_df['total_cases'].sum())), unsafe_allow_html=True)
    with kpi2:
        st.markdown("<div class='kpi-card'><div class='kpi-title'>Guéris</div><div class='kpi-value'>{:,}</div><div class='kpi-desc'>Total des guérisons</div></div>".format(int(latest_df['total_recovered'].sum())), unsafe_allow_html=True)
    with kpi3:
        st.markdown("<div class='kpi-card'><div class='kpi-title'>Décès</div><div class='kpi-value'>{:,}</div><div class='kpi-desc'>Total des décès</div></div>".format(int(latest_df['total_deaths'].sum())), unsafe_allow_html=True)
    with kpi4:
        st.markdown("<div class='kpi-card'><div class='kpi-title'>Pays analysés</div><div class='kpi-value'>{}</div><div class='kpi-desc'>Pays sélectionnés</div></div>".format(latest_df['country'].nunique()), unsafe_allow_html=True)
    st.divider()
    st.caption("Ces indicateurs sont calculés sur tous les pays sélectionnés.")

# --- Visualisations avancées ---
with tabs[1]:
    st.markdown("<div class='section-header'>Carte et visualisations interactives</div>", unsafe_allow_html=True)
    visu_type = st.radio("Type de visualisation", ["Carte mondiale", "Comparaison des pays", "Détails par pays"], horizontal=True)
    custom_palette = ["#fff", "#f7b267", "#6c757d"]
    if visu_type == "Carte mondiale":
        metric = st.radio("Métrique à afficher", ["Décès", "Guéris"], horizontal=True)
        if metric == "Décès":
            color_col, scale, title = 'total_deaths', custom_palette, 'Décès par pays'
            colorbar_title = 'Décès'
        else:
            color_col, scale = 'total_recovered', ["#fff", "#7ed957", "#f7b267"]
            title = 'Guéris par pays'
            colorbar_title = 'Guéris'
        map_df = latest_df.copy()
        fig_map = px.choropleth(
            map_df,
            locations='country',
            locationmode='country names',
            color=color_col,
            hover_name='country',
            color_continuous_scale=scale,
            title=title,
            labels={color_col: colorbar_title},
            hover_data={
                'country': True,
                color_col: ':,',
                'total_cases': ':,' if 'total_cases' in map_df.columns else False,
                'total_recovered': ':,' if 'total_recovered' in map_df.columns else False,
                'total_deaths': ':,' if 'total_deaths' in map_df.columns else False
            },
            template='plotly',
            height=550
        )
        fig_map.update_geos(
            showcountries=True, countrycolor="#bdbdbd",
            showcoastlines=True, coastlinecolor="#bdbdbd",
            showframe=False,
            projection_type="natural earth",
            lataxis_range=[-60, 85]
        )
        fig_map.update_layout(
            margin={"r":0,"t":40,"l":0,"b":0},
            coloraxis_colorbar=dict(
                title=colorbar_title,
                tickformat=",.0f",
                thickness=18,
                len=0.6,
                yanchor="middle",
                y=0.5
            ),
            geo_bgcolor="#23272b",
            paper_bgcolor="#23272b",
            font_color="#fff",
            legend=dict(bgcolor="#2c3440", font=dict(color="#fff")),
            title_font=dict(color="#fff", size=22)
        )
        selected_country = st.selectbox("Focus sur un pays (optionnel)", ["Aucun"] + sorted(map_df['country'].unique()))
        if selected_country != "Aucun":
            fig_map.update_traces(
                selectedpoints=[map_df[map_df['country'] == selected_country].index[0]],
                selector=dict(type='choropleth'),
                marker_line_width=2.5,
                marker_line_color="#f7b267"
            )
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption("Carte mondiale interactive : survolez un pays pour voir les chiffres précis, sélectionnez un pays pour le mettre en avant, filtrez entre guérisons/décès. Palette harmonieuse, fond discret, responsive, accessible.")
    elif visu_type == "Comparaison des pays":
        countries = sorted(filtered_df['country'].dropna().unique())
        sel = st.multiselect("Sélectionner pays à comparer", countries, default=countries[:3])
        if sel:
            comp_df = filtered_df[filtered_df['country'].isin(sel)]
            fig = px.line(comp_df, x='date', y='total_cases', color='country', title='Évolution des cas',
                          color_discrete_sequence=custom_palette)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Courbe d'évolution des cas pour les pays sélectionnés.")
    elif visu_type == "Détails par pays":
        pays_unique = sorted(filtered_df['country'].unique())
        pays = st.selectbox("Pays", pays_unique)
        filt = filtered_df[filtered_df['country'] == pays]
        fig1 = px.area(filt, x='date', y='total_cases', title=f'Cas pour {pays}', color_discrete_sequence=["#f7b267"])
        fig2 = px.bar(filt, x='date', y='total_deaths', title=f'Décès pour {pays}', color_discrete_sequence=["#fff"])
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption(f"Détail des cas et décès pour {pays} sur tout l'historique.")

# --- Prédiction Prophet sur 3 mois & Prédiction IA RandomForest (API) ---
with tabs[2]:
    st.markdown("<div class='section-header'>Prédiction sur 3 mois (Prophet)</div>", unsafe_allow_html=True)
    st.info("Sélectionnez un pays et une variable à prédire. Le modèle Prophet prédit l'évolution sur 3 mois (données mensuelles).")

    pays_unique = sorted(raw_df['country'].unique())
    pays = st.selectbox("Pays à prédire", pays_unique)
    variable = st.selectbox(
        "Variable à prédire",
        ["total_cases", "total_deaths", "total_recovered"],
        format_func=lambda x: {"total_cases":"Total cas", "total_deaths":"Total décès", "total_recovered":"Total guéris"}[x]
    )

    # Prend toutes les données du pays sélectionné, sans filtre de période
    df_pred = raw_df[raw_df['country'] == pays][['date', variable]].dropna()
    df_pred = df_pred.rename(columns={'date': 'ds', variable: 'y'})
    df_pred = df_pred.sort_values('ds')

    if len(df_pred) < 12:
        st.warning("Pas assez de données pour entraîner Prophet (au moins 12 mois nécessaires).")
    else:
        with st.spinner("Calcul de la prédiction Prophet..."):
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
            model.fit(df_pred)
            # Prédire sur 3 mois (car données mensuelles)
            future = model.make_future_dataframe(periods=3, freq='MS')
            forecast = model.predict(future)
            # Lissage de la prédiction
            forecast['yhat_smooth'] = forecast['yhat'].rolling(window=3, min_periods=1).mean()

        # Calcul MAE sur l'historique (alignement des dates)
        merged = pd.merge(df_pred, forecast[['ds', 'yhat']], on='ds', how='inner')
        y_true = merged['y']
        y_pred = merged['yhat']
        mae = mean_absolute_error(y_true, y_pred)

        # Affichage Plotly : prédiction uniquement après la dernière date historique
        fig = go.Figure()
        # Historique
        fig.add_trace(go.Scatter(
            x=df_pred['ds'], y=df_pred['y'],
            mode='lines+markers', name='Historique'
        ))
        last_date = df_pred['ds'].max()
        # Prédiction (ligne pointillée)
        forecast_future = forecast[forecast['ds'] >= last_date]
        fig.add_trace(go.Scatter(
            x=forecast_future['ds'], y=forecast_future['yhat_smooth'],
            mode='lines', name='Prédiction lissée', line=dict(dash='dot', color='red')
        ))
        # Points de prédiction (en rouge)
        fig.add_trace(go.Scatter(
            x=forecast_future['ds'], y=forecast_future['yhat_smooth'],
            mode='markers', name='Points prédits', marker=dict(color='red', size=10, symbol='circle')
        ))

        # Colorer les labels des mois prédits en rouge
        all_dates = list(df_pred['ds']) + list(forecast_future['ds'])
        # Afficher un tick sur 2 pour plus de clarté
        step = 2
        tickvals = all_dates[::step]
        ticktext = [
            (f"<span style='color:red'>{d.strftime('%b %Y')}</span>" if d in list(forecast_future['ds']) else d.strftime('%b %Y'))
            for d in tickvals
        ]

        fig.update_layout(
            title=f"Prédiction sur 3 mois pour {pays} - {variable.replace('_',' ').capitalize()}<br>MAE historique : {mae:.2f}",
            xaxis_title="Date",
            yaxis_title=variable.replace('_',' ').capitalize(),
            legend=dict(bgcolor="#2c3440", font=dict(color="#fff")),
            plot_bgcolor="#23272b",
            paper_bgcolor="#23272b",
            font_color="#fff",
            xaxis=dict(
                tickvals=tickvals,
                ticktext=ticktext,
                tickangle=45,  # Incline les labels pour la lisibilité
                tickfont=dict(size=11),
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Courbe historique (plein), prédiction Prophet lissée sur 3 mois (pointillés rouges), points prédits en rouge. Les mois prédits sont affichés en rouge sur l'axe horizontal.)")

    # --- Prédiction IA RandomForest (API) ---
    st.markdown("<div class='section-header'>Prédiction IA RandomForest (API)</div>", unsafe_allow_html=True)
    st.info("Entrez le nombre total de décès et de guéris pour obtenir la prédiction IA (modèle RandomForest).")

    col1, col2 = st.columns(2)
    with col1:
        total_deaths = st.number_input("Total décès", min_value=0, value=0)
    with col2:
        total_recovered = st.number_input("Total guéris", min_value=0, value=0)

    if st.button("Prédire (API IA)"):
        data = {"total_deaths": total_deaths, "total_recovered": total_recovered}
        try:
            response = requests.post("http://127.0.0.1:8000/predict", json=data)
            if response.status_code == 200:
                result = response.json()
                label = "Plus de 10 000 cas" if result["prediction"] == 1 else "Moins de 10 000 cas"
                st.success(f"Prédiction IA : {label} (proba : {result['probability']:.2f})")
            else:
                st.error(f"Erreur API IA : {response.text}")
        except Exception as e:
            st.error(f"Erreur de connexion à l'API IA : {e}")

# --- Tableau de données ---
with tabs[3]:
    st.markdown("<div class='section-header'>Tableau de données filtrées</div>", unsafe_allow_html=True)
    st.dataframe(filtered_df, use_container_width=True, height=400)
    st.download_button("Exporter les données filtrées (CSV)", filtered_df.to_csv(index=False), "donnees_filtrees.csv")



# --- À propos / Aide ---
with tabs[4]:
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
    
    