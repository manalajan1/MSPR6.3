# MSPr6.1 - Pipeline Données & Dashboard

**Table des matières**

- [Présentation](#présentation)
- [Structure du projet](#structure-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Pipeline ETL](#pipeline-etl)
- [API FastAPI](#api-fastapi)
- [Dashboard Streamlit](#dashboard-streamlit)
- [Bonnes pratiques](#bonnes-pratiques)
- [Dépannage rapide](#dépannage-rapide)

---

## Présentation

Ce projet met en place un **pipeline complet** pour télécharger, nettoyer, stocker et visualiser des données sur la COVID-19 et le Mpox. Les données brutes sont obtenues via Kaggle, nettoyées avec pandas, stockées dans PostgreSQL, exposées via une API FastAPI et visualisées dans un dashboard Streamlit.

---

## Structure du projet

```
MSPR6.1/
├── cleaned_data/                  # CSV nettoyés (cumul dernier jour du mois)
├── data/                          # CSV bruts téléchargés
├── mspr6.1/
│   ├── api/                       # FastAPI (api.py)
│   └── scripts/                   # Scripts : download, clean, store, dashboard
├── .env                           # Variables d'environnement
├── requirements.txt               # Dépendances Python
└── README.md                      # Ce fichier
```

---

## Prérequis

- Python 3.10+
- Git
- PostgreSQL 14+ (ou 16)
- Compte Kaggle (`kaggle.json` ou variables d'environnement)

---

## Installation

1. **Cloner le dépôt**
   ```bash
git clone https://github.com/MAHRAZ-Oussama/mspr6.1.git
cd mspr6.1
   ```
2. **Créer et activer l'environnement virtuel**
   ```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
   ```
3. **Installer les dépendances**
   ```bash
pip install -r requirements.txt
   ```

---

## Configuration

Créer un fichier `.env` à la racine (fourni) contenant :

```dotenv
DATABASE_URL=postgresql://mspr_user:Mspr6.1%40@localhost:5432/mspr_db
KAGGLE_USERNAME=<votre_kaggle_user>
KAGGLE_KEY=<votre_kaggle_key>
```

- Le mot de passe `Mspr6.1@` doit être encodé (`%40`).
- La base `mspr_db` et l'utilisateur `mspr_user` doivent exister.

---

## Pipeline ETL

1. **Téléchargement**
   ```bash
python mspr6.1/scripts/download_data.py
   ```
   - Télécharge les CSV via l'API Kaggle dans `data/`.

2. **Nettoyage**
   ```bash
python mspr6.1/scripts/clean_datasets.py
   ```
   - Conserve uniquement le dernier jour du mois par pays.
   - Ajoute la colonne `Total_Gueris`.
   - Écrit les CSV dans `cleaned_data/`.

3. **Stockage en base**
   ```bash
python mspr6.1/scripts/store_data.py
   ```
   - Insère les CSV nettoyés dans PostgreSQL (`covid19_daily`, `mpox`).

---

## API FastAPI

```bash
uvicorn mspr6.1.api.main:app --reload
```

- **Base URL** : `http://localhost:8000`
- **Swagger** : `http://localhost:8000/docs`
- **Endpoint principal** :
  - `GET /query?sql=<votre_SQL>` exécute la requête et retourne JSON.

---

## Dashboard Streamlit

```bash
streamlit run mspr6.1/scripts/dashboard.py
```

- **Affiche** les indicateurs globaux basés sur le cumul **dernier jour** par pays.
- **Comparaison** des courbes, carte choroplèthe, détails par pays.

---

## Bonnes pratiques

- Ne **pas** committer le `.env`, `data/` ou les dossiers d'environnement.
- Encoder tous les caractères spéciaux dans les URLs de connexion.
- Sécuriser l'API avant déploiement (auth, whitelist SQL, rate limit).

---

## Dépannage rapide

- **Connexion BDD** : `psql $DATABASE_URL`
- **Données manquantes** : vérifier `ls data/` et `ls cleaned_data/`.
- **Port occupé** : changer le port PostgreSQL ou utiliser `127.0.0.1`.

---

*Documentation rédigée par Oussama Mahraz – 22/Avril/2025*

