import streamlit as st
import requests

st.set_page_config(page_title="Dashboard IA Covid", layout="wide")
st.title("Dashboard IA Covid")

menu = st.sidebar.radio("Navigation", ["Prédiction IA", "Statistiques", "Visualisations"])

if menu == "Prédiction IA":
    st.header("Prédiction IA (RandomForest)")
    deaths = st.number_input("Total Deaths", min_value=0, value=100)
    recovered = st.number_input("Total Recovered", min_value=0, value=1000)
    if st.button("Prédire"):        
        data = {"total_deaths": deaths, "total_recovered": recovered}
        try:
            r = requests.post("http://localhost:8000/predict", json=data)
            if r.status_code == 200:
                res = r.json()
                st.success(f"Prédiction : {'> 10 000 cas' if res['prediction'] else '<= 10 000 cas'} (proba : {res['probability']:.2f})")
            else:
                st.error("Erreur API : " + r.text)
        except Exception as e:
            st.error(f"Erreur de connexion à l'API : {e}")

elif menu == "Statistiques":
    st.header("Statistiques globales")
    st.write("À compléter avec vos analyses statistiques.")

elif menu == "Visualisations":
    st.header("Visualisations")
    st.write("À compléter avec vos graphiques et cartes.")
