import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
from imblearn.over_sampling import SMOTE
import joblib

# 1. Connexion à la base et extraction des données
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

query = """
SELECT * FROM covid19_daily
WHERE total_cases IS NOT NULL AND total_deaths IS NOT NULL AND total_recovered IS NOT NULL
"""
df = pd.read_sql(query, engine)

# 2. Préparation des features et de la cible (exemple : prédire si un pays a eu plus de 10000 cas)
df['target'] = (df['total_cases'] > 10000).astype(int)
features = ['total_deaths', 'total_recovered']
X = df[features]
y = df['target']

# 3. Équilibrage des classes (optionnel)
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

# 4. Split 60% train / 40% test
X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.4, random_state=42, stratify=y_res)

# 5. Cross-validation sur le train
clf = RandomForestClassifier(random_state=42)
cross_val = cross_val_score(clf, X_train, y_train, cv=5, scoring='f1')
print(f"F1-score cross-validation (train): {cross_val.mean():.3f}")

# 6. Entraînement du modèle
clf.fit(X_train, y_train)

# 7. Évaluation sur le test
y_pred = clf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("F1-score:", f1_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# 8. Sauvegarde du modèle
joblib.dump(clf, "model_covid_rf.joblib")
print("Modèle sauvegardé sous model_covid_rf.joblib")

# 9. (Optionnel) Export des résultats de test dans un CSV
results = pd.DataFrame({
    "y_true": y_test,
    "y_pred": y_pred
})
results.to_csv("rf_test_results.csv", index=False)
print("Résultats de test exportés dans rf_test_results.csv")