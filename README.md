# 🌙 Plume Astrale

Application web d'astrologie et de tarot — thème astral, tirage tarot, horoscope, numérologie, compatibilité amoureuse.

## Stack technique

- **Frontend** : React 19, Tailwind CSS, React Router v7, Craco
- **Backend** : FastAPI (Python), MongoDB, Stripe
- **Déploiement** : Netlify (frontend) + Railway/Docker (backend)

## Installation locale

### Prérequis
- Node.js 20+, Yarn
- Python 3.11+
- MongoDB

### Frontend
```bash
cd frontend
yarn install
REACT_APP_BACKEND_URL=http://localhost:8001 yarn start
```

### Backend
```bash
cd backend
pip install -r requirements.txt
# Copier .env.example en .env et remplir les variables
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Avec Docker Compose
```bash
cp .env.example .env
# Remplir .env avec vos vraies clés
docker compose up --build
```

## Variables d'environnement

Voir `.env.example` pour la liste complète des variables nécessaires.

> ⚠️ Ne jamais committer de clés API dans le dépôt.
