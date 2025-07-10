
# Documentation technique du Dashboard

- **URL** : http://localhost:8501

## Fonctionnalités principales
- Visualisation des indicateurs COVID-19 (tableaux, graphiques dynamiques)
- Affichage des prédictions IA (modèle RandomForest)
- Carte interactive par pays (Plotly, zoom, tooltips)
- Filtres par date, pays, type d'indicateur
- Téléchargement des résultats (CSV)
- Explications IA (code couleur, explications simples)
- Responsive : fonctionne sur ordinateur, tablette, mobile
- Accessibilité : navigation clavier, contraste élevé, polices lisibles
- Contact : [Votre email ou lien GitHub]

## Accessibilité
- Compatible desktop, mobile et tablette
- Navigation claire, boutons accessibles, focus visible
- Contraste élevé, polices lisibles, taille de texte adaptable
- Testé avec navigation clavier (tabulation)

## Logs et supervision
- Les erreurs sont affichées dans la console Streamlit
- Les accès et actions utilisateurs peuvent être logués (voir logging Python)
- (Optionnel) Intégration Sentry pour logs front-end

## Exemples d'utilisation
- Lancer le dashboard :
```bash
streamlit run scripts/dashboard.py
```
- Accéder à l'URL : http://localhost:8501

## Sécurité
- Les accès au dashboard sont publics par défaut (ajouter authentification si besoin)
- Les données sensibles ne sont pas exposées côté client

## Contact
- Pour toute question, contacter l'équipe projet (voir README)
