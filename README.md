# Hyperliquid Trading Bot

Bot de trading et de monitoring pour **Hyperliquid** avec API REST et système de notifications Telegram en temps réel.

## Fonctionnalités

### API REST (FastAPI)
- **Récupération d'état** : Consulter l'état d'un compte utilisateur (positions, margin, valeur du portefeuille)
- **Trading** : Ouvrir et fermer des positions market
- **Health check** : Vérifier la santé de l'API et la configuration de l'exchange

### Worker de Notifications Telegram
- **Alertes en temps réel** : Reçoit des notifications Telegram pour chaque trade exécuté
- **Surveillance multi-adresses** : Écoute plusieurs adresses simultanément
- **Détails des trades** : Coin, prix, taille, side (buy/sell), PnL réalisé

---

## Prérequis

- Python 3.11+
- Compte Hyperliquid (mainnet)
- Bot Telegram (optionnel, uniquement pour les notifications)

---

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/nathanruer/hyperliquid-fastapi-gateway.git
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## Configuration

### 1. Créer le fichier `.env`

Créez un fichier `.env` à la racine du projet :

```bash
cp .env.example .env
```

### 2. Remplir les variables d'environnement

```bash
# Sécurité (OBLIGATOIRE)
API_KEY=votre_cle_api_32_caracteres_minimum  # Générer avec: openssl rand -hex 32
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
TRADING_ENABLED=true  # false pour mode read-only

# Configuration Hyperliquid (OBLIGATOIRE si TRADING_ENABLED=true)
ACCOUNT_ADDRESS=0xVotreAdresseEthereum
SECRET_KEY=votre_cle_privee_sans_0x  # Optionnel si TRADING_ENABLED=false

# Adresses à écouter pour les notifications (format JSON)
USERS_LISTENED=["0xAdresse1", "0xAdresse2"]

# Configuration Telegram (optionnel, pour les notifications)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321

# Configuration API
API_HOST=0.0.0.0
API_PORT=8000
```

#### Notes sur la sécurité

- **API_KEY** : **OBLIGATOIRE** (min 32 caractères). Utilisé pour authentifier les requêtes de trading.
  - Générer : `openssl rand -hex 32`
  - Inclure dans les requêtes via header `X-API-Key`
- **ALLOWED_ORIGINS** : Liste des domaines autorisés pour CORS (jamais `*` en production)
- **TRADING_ENABLED** : 
  - `true` = trading activé (SECRET_KEY requis)
  - `false` = mode read-only (SECRET_KEY optionnel)

#### Notes générales

- **SECRET_KEY** : Requis uniquement si `TRADING_ENABLED=true`
- **USERS_LISTENED** : Format JSON array. Exemple : `["0xabc...", "0xdef..."]`
- **TELEGRAM_BOT_TOKEN** & **TELEGRAM_CHAT_ID** : Optionnels. Si absents, pas de notifications Telegram.

---

## Lancement

### Option 1 : Lancer l'API

```bash
python scripts/run_api.py
```

L'API sera disponible sur `http://localhost:8000`

- **Documentation Swagger** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

### Option 2 : Lancer le Worker de Notifications

```bash
python scripts/run_trades_listener.py
```

Le worker se connectera au WebSocket Hyperliquid et enverra des notifications Telegram pour chaque trade détecté.

### Option 3 : Lancer les deux (dans des terminaux séparés)

**Terminal 1** :
```bash
python scripts/run_api.py
```

**Terminal 2** :
```bash
python scripts/run_trades_listener.py
```

---

## 📡 Endpoints API

### Health Check

**GET** `/health`

```bash
curl http://localhost:8000/health
```

**Réponse** :
```json
{
  "status": "ok",
  "service": "hyperliquid-api",
  "exchange_configured": true,
  "account_address": "0xYourAddress"
}
```

### État utilisateur

**GET** `/v1/user/{address}`

```bash
curl http://localhost:8000/v1/user/0xYourAddress
```

**Réponse** :
```json
{
  "address": "0xYourAddress",
  "accountValue": "1000.50",
  "totalRawUsd": "1000.50",
  "numPositions": 2,
  "marginSummary": {...},
  "assetPositions": [...]
}
```

### Ouvrir une position market

**POST** `/v1/order/market` **Authentification requise**

```bash
curl -X POST http://localhost:8000/v1/order/market \
  -H "Content-Type: application/json" \
  -H "X-API-Key: votre_api_key_ici" \
  -d '{
    "coin": "BTC",
    "is_buy": true,
    "size": 0.01,
    "slippage": 0.01
  }'
```

**Body** :
```json
{
  "coin": "BTC",
  "is_buy": true,
  "size": 0.01,
  "slippage": 0.01
}
```

**Réponse** :
```json
{
  "status": "ok",
  "filled_orders": [
    {
      "oid": 123456,
      "totalSz": "0.01",
      "avgPx": "50000"
    }
  ],
  "errors": []
}
```

### Fermer une position

**POST** `/v1/order/market/close` **Authentification requise**

```bash
curl -X POST http://localhost:8000/v1/order/market/close \
  -H "Content-Type: application/json" \
  -H "X-API-Key: votre_api_key_ici" \
  -d '{"coin": "BTC"}'
```

---

## Sécurité

### Authentification API Key

Les endpoints de **trading** (`/v1/order/*`) nécessitent une authentification via header `X-API-Key`.

**Endpoints protégés :**
- `POST /v1/order/market` - Ouvrir une position
- `POST /v1/order/market/close` - Fermer une position

**Endpoints publics :**
- `GET /health` - Health check
- `GET /v1/user/{address}` - État utilisateur (avec rate limiting)

### Rate Limiting

- **Trading** : 30 requêtes/minute maximum
- **Consultation** : 60 requêtes/minute maximum

Au-delà de ces limites, l'API retournera une erreur `429 Too Many Requests`.

### CORS

Seules les origines configurées dans `ALLOWED_ORIGINS` peuvent accéder à l'API depuis un navigateur.

### Mode Read-Only

Pour utiliser l'API en mode consultation uniquement (sans trading) :

```bash
TRADING_ENABLED=false
# SECRET_KEY peut être omis
```

---

## Architecture

```
hyperliquid-bot/
├── app/
│   ├── api/                   # Application FastAPI
│   │   ├── app.py             # Factory FastAPI
│   │   ├── dependencies.py    # Dependency injection
│   │   └── routers/           # Routes API
│   │       ├── root.py        # /, /health
│   │       └── v1/
│   │           └── endpoints/
│   │               ├── trading.py     # POST /v1/order/market
│   │               └── user_state.py  # GET /v1/user/{address}
│   │
│   ├── workers/                # Background workers
│   │   └── trades_listener.py  # WebSocket listener + Telegram notifications
│   │
│   ├── services/                   # Services métier
│   │   ├── hyperliquid_service.py  # Interaction avec Hyperliquid SDK
│   │   └── telegram_service.py     # Envoi de notifications Telegram
│   │
│   ├── models/                 # Schemas Pydantic
│   │   └── schemas.py
│   │
│   └── core/                  # Configuration & middleware
│       ├── config.py          # Settings (.env)
│       ├── logger.py          # Logger configuré
│       ├── middleware.py      # API key verification middleware
│       └── exceptions.py      # Exception handling middleware
│
├── tests/                     # Tests unitaires
│   ├── conftest.py
│   ├── test_api_endpoints.py
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_hyperliquid_service.py
│   └── test_telegram_service.py
│
├── scripts/                   # Points d'entrée
│   ├── run_api.py             # Lancer l'API
│   └── run_trades_listener.py # Lancer le worker
│
├── .env                        # Variables d'environnement
├── requirements.txt            # Dépendances Python
└── README.md                   # Cette documentation
```

### Séparation API / Worker

- **API** (`app/api/`) : Application FastAPI indépendante, peut tourner seule
- **Worker** (`app/workers/`) : Process séparé pour les notifications, peut tourner seul
- **Services** (`app/services/`) : Code partagé entre API et Worker

Cette architecture permet de :
- Déployer API et Worker sur des serveurs différents
- Scaler horizontalement chaque composant indépendamment
- Tester et développer chaque partie séparément

---

## Développement

### Structure de code

- **Type hints** partout pour la lisibilité
- **Pydantic** pour validation des données
- **Logging** structuré
- **Séparation des responsabilités** (API / Workers / Services)

### Ajouter un nouvel endpoint

1. Créer une fonction dans `app/api/routers/v1/endpoints/`
2. Importer le router dans `app/api/app.py`
3. Utiliser les dependencies pour injecter les services

### Ajouter un nouveau worker

1. Créer un fichier dans `app/workers/`
2. Créer un script d'entrée dans `scripts/`
3. Implémenter la logique métier

---

## Bonnes Pratiques de Sécurité

- **Ne jamais commit le fichier `.env`** (contient vos clés privées)
- Le `.env` est déjà dans `.gitignore`
- **Générez une API_KEY forte** : `openssl rand -hex 32`
- **Restreignez CORS** : Ne jamais utiliser `*` en production
- **Utilisez HTTPS** en production (derrière un reverse proxy)
- **Activez le mode read-only** si vous n'avez pas besoin de trader
- **Surveillez les logs** pour détecter les tentatives d'accès non autorisées
- N'exposez jamais votre `SECRET_KEY` ou `API_KEY` publiquement

---

## Ressources

- [Documentation Hyperliquid SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Telegram Bot API](https://core.telegram.org/bots/api)

---

## Troubleshooting

### L'API ne démarre pas

```
ConfigurationError: API_KEY doit contenir au minimum 32 caractères
```

**Solution** : Générez une clé API forte :
```bash
openssl rand -hex 32
```

### Erreur 401 Unauthorized

```
{"detail": "API Key manquante. Incluez le header 'X-API-Key' dans votre requête."}
```

**Solution** : Incluez le header `X-API-Key` dans vos requêtes de trading :
```bash
curl -H "X-API-Key: votre_cle_api" ...
```

### Erreur 429 Too Many Requests

```
{"error": "Rate limit exceeded"}
```

**Solution** : Vous avez dépassé le rate limit. Attendez 1 minute ou réduisez la fréquence des requêtes.

### Le worker ne reçoit pas de notifications

1. Vérifiez que `USERS_LISTENED` est au bon format JSON
2. Vérifiez que `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` sont corrects
3. Vérifiez les logs du worker pour voir les erreurs

### "Exchange non configuré" en mode trading

**Solution** : Si `TRADING_ENABLED=true`, configurez `ACCOUNT_ADDRESS` et `SECRET_KEY` dans `.env`.

Pour le mode read-only, définissez `TRADING_ENABLED=false` - `SECRET_KEY` devient optionnel.

### CORS Error dans le navigateur

**Solution** : Ajoutez votre domaine dans `ALLOWED_ORIGINS` :
```bash
ALLOWED_ORIGINS=http://localhost:3000,https://votre-domaine.com
```

---

## License

MIT License

---