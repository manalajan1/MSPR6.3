def train_model():
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
    df['target'] = (df['total_cases'] > 10000).astype(int)

    print(f"Nombre de lignes extraites de la base : {len(df)}")
    print(df[['total_cases', 'total_deaths', 'total_recovered']].describe())
    print("Distribution de la cible (target) :")
    print(df['target'].value_counts())

    features = ['total_deaths', 'total_recovered']
    X = df[features]
    y = df['target']

    # 3. Équilibrage des classes (optionnel)
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X, y)

    # 4. Split 60% train / 40% test
    X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42, stratify=y_res)

    # 5. Cross-validation sur le train
    clf = RandomForestClassifier(random_state=42)
    n_splits = min(5, len(X_train))
    if n_splits > 1:
        cross_val = cross_val_score(clf, X_train, y_train, cv=n_splits, scoring='f1')
        print(f"F1-score cross-validation (train): {cross_val.mean():.3f}")
    else:
        print("Pas assez d'échantillons pour la cross-validation.")
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

    return clf  # ou return True si tu veux juste valider l'exécution
if __name__ == "__main__":
    train_model()