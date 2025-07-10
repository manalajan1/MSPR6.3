# MSPR Bloc 3 – Projet COVID

## Table des matières
- [Présentation](#présentation)
- [Structure du projet](#structure-du-projet)
- [Diagramme UML](#diagramme-uml)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Pipeline ETL](#pipeline-etl)
- [API FastAPI](#api-fastapi)
- [Dashboard Streamlit](#dashboard-streamlit)
- [Tests unitaires et fonctionnels](#tests-unitaires-et-fonctionnels)
- [Intégration continue (CI/CD)](#intégration-continue-cicd)
- [Supervision et logs](#supervision-et-logs)
- [Déploiement](#déploiement)
- [Procédures de sauvegarde/restauration](#procédures-de-sauvegarderestauration)
- [Procédure de rollback](#procédure-de-rollback)
- [Bonnes pratiques](#bonnes-pratiques)
- [Dépannage rapide](#dépannage-rapide)

---

## Présentation

Ce projet met en place un **pipeline complet** pour télécharger, nettoyer, stocker et visualiser des données sur la COVID-19 et le Mpox.  
Les données brutes sont obtenues via Kaggle, nettoyées avec pandas, stockées dans PostgreSQL, exposées via une API FastAPI et visualisées dans un dashboard Streamlit.

---

## Structure du projet

```
mspr6.1/
├── cleaned_data/                  # CSV nettoyés (dernier jour du mois)
├── data/                          # CSV bruts téléchargés
├── mspr6.1/
│   ├── api/                       # FastAPI (main.py)
│   └── scripts/                   # Scripts : download, clean, store, dashboard, ml_pipeline
├── .env                           # Variables d'environnement
├── requirements.txt               # Dépendances Python
├── docker-compose.yml             # Orchestration Docker
├── Dockerfile                     # Image principale
├── docs/
│   ├── api.md                     # Documentation technique API
│   ├── dashboard.md               # Documentation dashboard
│   └── uml.png                    # Diagramme UML
├── tests/                         # Tests unitaires et fonctionnels
│   ├── test_api.py
│   └── test_utils.py
└── README.md                      # Ce fichier
```

---

## Diagramme UML

Le diagramme UML du projet (pipeline, API, dashboard, base de données) est disponible dans :  
`docs/uml.png`

---

## Prérequis

- Python 3.10+
- Docker & Docker Compose
- Git
- PostgreSQL 14+ (ou via Docker)
- Compte Kaggle (`kaggle.json` ou variables d'environnement)

---

## Installation

1. **Cloner le dépôt**
   ```sh
   git clone https://github.com/MAHRAZ-Oussama/mspr6.1.git
   cd mspr6.1
   ```
2. **Créer et activer l'environnement virtuel**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate   # Windows : .venv\Scripts\activate
   ```
3. **Installer les dépendances**
   ```sh
   pip install -r requirements.txt
   ```

---

## Configuration

Créer un fichier `.env` à la racine contenant :

```dotenv
DATABASE_URL=postgresql://postgres:postgres@db:5432/mspr_db
KAGGLE_USERNAME=<votre_kaggle_user>
KAGGLE_KEY=<votre_kaggle_key>
```

---

## Pipeline ETL

1. **Téléchargement**
   ```sh
   python mspr6.1/scripts/download_data.py
   ```
   - Télécharge les CSV via l'API Kaggle dans `data/`.

2. **Nettoyage**
   ```sh
   python mspr6.1/scripts/clean_datasets.py
   ```
   - Conserve uniquement le dernier jour du mois par pays.
   - Ajoute la colonne `Total_Gueris`.
   - Écrit les CSV dans `cleaned_data/`.

3. **Stockage en base**
   ```sh
   python mspr6.1/scripts/store_data.py
   ```
   - Insère les CSV nettoyés dans PostgreSQL (`covid19_daily`, `mpox`).

4. **Entraînement modèle IA**
   ```sh
   docker-compose run ml-pipeline
   ```
   - Entraîne le modèle, sauvegarde `model_covid_rf.joblib` et exporte les résultats dans `rf_test_results.csv`.

---

## API FastAPI

```sh
uvicorn mspr6.1.api.main:app --reload
```

- **Base URL** : `http://localhost:8000`
- **Swagger** : `http://localhost:8000/docs`
- **Endpoint principal** :
  - `POST /predict` : Prédiction à partir des données envoyées.
  - Voir la documentation détaillée dans `docs/api.md`.

---

## Dashboard Streamlit

```sh
streamlit run mspr6.1/scripts/dashboard.py
```

- **Affiche** les indicateurs globaux basés sur le cumul **dernier jour** par pays.
- **Comparaison** des courbes, carte choroplèthe, détails par pays.
- Voir la documentation détaillée dans `docs/dashboard.md`.

---

## Tests unitaires et fonctionnels

- Les tests sont dans le dossier `tests/`.
- **Lancer tous les tests** :
  ```sh
  pytest tests/
  ```

---

## Intégration continue (CI/CD)

- Un workflow GitHub Actions est disponible dans `.github/workflows/ci.yml`.
- À chaque push ou pull request, les tests sont lancés automatiquement.

---

## Supervision et logs

- **Pipeline et API** : Utilisent la librairie Python `logging` pour générer des logs (voir début de chaque script principal).
- **Dashboard** : Logs dans la console (optionnel : intégrer Sentry).
- **MLFlow ou TensorBoard** : (optionnel) pour le suivi des entraînements.
- **En cas d’erreur critique** : possibilité d’automatiser la création d’une issue GitHub (bonus).

---

## Déploiement

### Docker Compose (local)
```sh
docker-compose up
```
- Tous les services (db, API, dashboard, pipeline) sont lancés.

### Kubernetes (optionnel)
- Des fichiers YAML peuvent être ajoutés dans `k8s/` pour déploiement sur Minikube.

---

## Procédures de sauvegarde/restauration

**Sauvegarde de la base**
```sh
docker exec mspr61-db-1 pg_dump -U postgres mspr_db > sauvegarde.sql
```

**Restauration**
```sh
docker cp sauvegarde.sql mspr61-db-1:/sauvegarde.sql
docker exec -it mspr61-db-1 psql -U postgres -d mspr_db -f /sauvegarde.sql
```

---


## Procédure de Pull Request (PR) et résolution de bug

1. **Créer une branche** dédiée à la correction ou à la nouvelle fonctionnalité :
   ```sh
   git checkout -b fix/nom-du-bug
   ```
2. **Faire les modifications** et **ajouter des tests** si besoin.
3. **Pousser la branche** sur le dépôt distant :
   ```sh
   git push origin fix/nom-du-bug
   ```
4. **Créer une Pull Request** sur GitHub, décrire le problème et la solution.
5. **Attendre la revue** et la validation d’un autre membre de l’équipe.
6. **Fusionner** la PR après validation et vérifier que la CI passe.

## Procédure de rollback

1. Lister les images Docker :
   ```sh
   docker images
   ```
2. Relancer l’avant-dernière image :
   ```sh
   docker run --rm -d <image_id_précédente>
   ```
3. (Kubernetes) Revenir à la version précédente d’un déploiement :
   ```sh
   kubectl rollout undo deployment/<nom-du-deployment>
   ```

---

## Bonnes pratiques

- Ne **pas** committer le `.env`, `data/` ou les dossiers d'environnement.
- Sécuriser l'API avant déploiement (auth, whitelist SQL, rate limit).
- Documenter chaque modification via des Pull Requests.
- Toujours ajouter des tests pour chaque bug corrigé ou nouvelle fonctionnalité.
- Utiliser des tags Git pour marquer les versions stables.

---

## Dépannage rapide

- **Connexion BDD** : `psql $DATABASE_URL`
- **Données manquantes** : vérifier `ls data/` et `ls cleaned_data/`.
- **Port occupé** : changer le port PostgreSQL ou utiliser `127.0.0.1`.
- **Logs** : consulter les logs générés par les scripts Python.

---

*Documentation rédigée par Oussama Mahraz – 2025*