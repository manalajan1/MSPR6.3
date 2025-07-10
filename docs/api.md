# Documentation technique de l'API

## Endpoints principaux

### `POST /predict`
- **Description** : Prédire le statut COVID à partir des données envoyées.
- **Body attendu** :
```json
{
  "country": "France",
  "date": "2020-03-01",
  "total_cases": 100,
  "total_deaths": 2,
  "total_recovered": 10
}
```
- **Réponse** :
```json
{
  "prediction": 1
}
```

### `GET /health`
- Vérifie que l'API est en ligne (healthcheck, monitoring)

### `GET /docs`
- Documentation Swagger interactive (OpenAPI)

### `GET /covid`
- Liste tous les enregistrements COVID (GET)

### `POST /covid`
- Ajoute un enregistrement COVID

### `GET /mpox`
- Liste tous les enregistrements Mpox

### `POST /mpox`
- Ajoute un enregistrement Mpox

### `GET /covid/{id}`
- Détail d'un enregistrement COVID

### `DELETE /covid/{id}`
- Supprime un enregistrement COVID

### `GET /mpox/{id}`
- Détail d'un enregistrement Mpox

### `DELETE /mpox/{id}`
- Supprime un enregistrement Mpox

## Sécurité
- Authentification par token (JWT recommandée, à implémenter si besoin)
- Limitation des droits selon le rôle (admin, user)
- Protection contre l'injection SQL (requêtes paramétrées)
- CORS activé uniquement pour les domaines autorisés
- (Optionnel) Limitation de débit (rate limiting)

## Logs
- Tous les accès, erreurs et requêtes sont logués via le module Python `logging` (niveau INFO/ERROR)
- Les logs sont stockés dans la console et peuvent être redirigés vers un fichier ou un outil de supervision (Sentry, ELK...)

## Exemples d'utilisation

### Requête de prédiction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"country": "France", "date": "2020-03-01", "total_cases": 100, "total_deaths": 2, "total_recovered": 10}'
```

### Authentification (exemple à implémenter)
```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

## Supervision
- Endpoint `/health` pour monitoring automatisé
- Logs d'accès et d'erreur exploitables par Prometheus/Grafana ou Sentry

## Contact
- Pour toute question, contacter l'équipe projet (voir README)

