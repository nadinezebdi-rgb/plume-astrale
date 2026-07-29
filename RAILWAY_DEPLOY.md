# Plume Astrale - Déploiement Railway

## Structure du projet
- `/frontend` - React app (Vite)
- `/backend` - FastAPI + MongoDB

## Variables d'environnement requises

### Backend
```
MONGO_URL=mongodb+srv://...  # Votre MongoDB Atlas URL
DB_NAME=plume_astrale
STRIPE_API_KEY=sk_live_...
ASTROLOGY_API_IO_KEY=ask_...  # cle api.astrology-api.io (remplace les anciennes ASTROLOGY_API_USER_ID/KEY, obsoletes)
CORS_ORIGINS=https://plume-astrale.fr,https://votre-app.up.railway.app
```

### Frontend
```
REACT_APP_BACKEND_URL=https://votre-backend.up.railway.app
```
