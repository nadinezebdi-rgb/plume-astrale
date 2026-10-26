# 📋 Checklist de Déploiement - Plume Astrale

## 🚀 Avant Chaque Déploiement

### Étape 1: Préparer les Secrets
- [ ] **OPENAI_API_KEY** obtenue depuis https://platform.openai.com/api-keys
- [ ] **ASTROLOGY_API_IO_KEY** obtenue depuis https://www.astrology-api.io
- [ ] **STRIPE_API_KEY** obtenue depuis https://dashboard.stripe.com
- [ ] **JWT_SECRET** généré (min 32 caractères aléatoires)
- [ ] **EMERGENT_LLM_KEY** (optionnel, depuis profil Emergent)

### Étape 2: Configuration Locale (Test)
```bash
# Copier le modèle
cp .env.example .env

# Remplir avec vos valeurs
nano .env  # ou ouvrir dans votre éditeur

# Vérifier les variables
bash scripts/verify-env.sh

# Lancer localement
docker-compose up
```

- [ ] Application démarre sans erreurs
- [ ] `/api/health` répond (HTTP 200)
- [ ] Chat LLM fonctionne
- [ ] Paiements Stripe testés

---

## 🌍 Déploiement sur Emergent (Production)

### Étape 1: Accéder au Dashboard
1. [ ] Connectez-vous à https://app.emergent.sh
2. [ ] Allez dans **Home** → **"Deployed Apps"**
3. [ ] Trouvez **"consultation-astro"**

### Étape 2: Ajouter les Variables d'Environnement
1. [ ] Cliquez sur votre app
2. [ ] Allez à **"Environment Variables"** ou **"Settings"**
3. [ ] Cliquez sur **"Configure"** ou **"Edit"**

### Étape 3: Configurer Chaque Variable

```
Nom de variable: OPENAI_API_KEY
Valeur: sk-...
Environnement: Production
✅ Cliquez sur "Add" ou "Save"
```

Répétez pour:
- [ ] `OPENAI_API_KEY`
- [ ] `ASTROLOGY_API_IO_KEY`
- [ ] `STRIPE_API_KEY`
- [ ] `JWT_SECRET`
- [ ] `EMERGENT_LLM_KEY` (optionnel)

### Étape 4: Obtenir la Clé Universelle Emergent (si besoin)
1. [ ] Cliquez sur l'**icône de profil** (haut droit)
2. [ ] Sélectionnez **"Universal Key"**
3. [ ] **Copiez** la clé
4. [ ] Collez-la dans `EMERGENT_LLM_KEY`

### Étape 5: Redéployer
1. [ ] Cliquez sur **"Redeploy"** ou **"Redéployer"**
2. [ ] **Attendez 10-15 minutes** pour que le déploiement se termine
3. [ ] Consultez les logs pour vérifier qu'il n'y a pas d'erreurs

### Étape 6: Vérifier le Déploiement
```bash
# Tester l'API
curl https://your-domain.com/api/health

# Vérifier les logs
# Via Emergent Dashboard → Select App → Logs
```

- [ ] API répond (status 200)
- [ ] Aucune erreur dans les logs
- [ ] Chat LLM fonctionne
- [ ] Paiements Stripe actifs

---

## 🚂 Déploiement sur Railway (Backend)

### Étape 1: Accéder aux Variables
1. [ ] Connectez-vous à https://railway.app
2. [ ] Sélectionnez le projet
3. [ ] Cliquez sur le service **backend**
4. [ ] Allez à l'onglet **"Variables"**

### Étape 2: Ajouter les Clés
Pour chaque variable, cliquez sur **"Add Variable"**:

| Clé | Valeur |
|-----|--------|
| [ ] `OPENAI_API_KEY` | `sk-...` |
| [ ] `ASTROLOGY_API_IO_KEY` | `ask_...` |
| [ ] `STRIPE_API_KEY` | `sk_live_...` |
| [ ] `JWT_SECRET` | `random...` |

### Étape 3: Redéployer
- [ ] Allez à l'onglet **"Deployments"**
- [ ] Cliquez sur **"Redeploy"**
- [ ] Attendez que le déploiement se termine
- [ ] Vérifiez les logs

---

## 🎨 Déploiement sur Vercel (Frontend)

### Étape 1: Accéder aux Variables
1. [ ] Connectez-vous à https://vercel.com
2. [ ] Sélectionnez le projet **frontend**
3. [ ] Allez à **Settings** → **Environment Variables**

### Étape 2: Ajouter les Variables Frontend
Cliquez sur **"Add New"**:

| Clé | Valeur |
|-----|--------|
| [ ] `REACT_APP_BACKEND_URL` | `https://api.your-domain.com` |
| [ ] `REACT_APP_API_URL` | `https://api.your-domain.com/api` |
| [ ] `REACT_APP_STRIPE_PUBLIC_KEY` | `pk_...` |

### Étape 3: Redéployer
- [ ] Les changements se déploient automatiquement
- [ ] Ou cliquez sur **"Redeploy"** manuellement
- [ ] Vérifiez que le frontend se charge

---

## 🐳 Déploiement sur VPS Local (Docker)

### Étape 1: Préparer le Serveur
```bash
# SSH sur le serveur
ssh root@187.124.9.214

# Créer le dossier
mkdir -p /root/plume-astrale
cd /root/plume-astrale
```

### Étape 2: Copier les Fichiers
```bash
# Depuis votre local
scp -r . root@187.124.9.214:/root/plume-astrale/
```

### Étape 3: Créer le Fichier .env
```bash
# Sur le serveur
ssh root@187.124.9.214
cd /root/plume-astrale
cp .env.example .env
nano .env  # Remplir avec les valeurs réelles
```

### Étape 4: Lancer le Script de Déploiement
```bash
bash deploy/deploy.sh
```

- [ ] Docker installé ✅
- [ ] Docker Compose installé ✅
- [ ] Application lancée ✅
- [ ] SSL configuré ✅

### Étape 5: Vérifier
```bash
# Vérifier les conteneurs
docker ps

# Vérifier les logs
docker compose logs -f backend

# Tester l'API
curl http://localhost/api/health
```

---

## 🔒 Checklist de Sécurité

- [ ] `.env` **JAMAIS** committé sur GitHub
- [ ] `.env` est dans `.gitignore`
- [ ] Les secrets ne sont **PAS** hardcodés dans le code
- [ ] `JWT_SECRET` est suffisamment aléatoire (32+ caractères)
- [ ] Les clés API sont **secrets** (utilisez `*****` pour les logs)
- [ ] Seuls les admins ont accès au fichier `.env`

---

## 🚨 Dépannage Rapide

### L'app ne démarre pas
```bash
# Vérifier les logs
docker compose logs backend

# Vérifier les variables
bash scripts/verify-env.sh

# Vérifier le fichier .env
cat .env | grep OPENAI
```

### Erreur "API Key invalid"
- [ ] Vérifiez que la clé est copiée correctement (sans espaces)
- [ ] Vérifiez que la clé est **active** sur le dashboard du service
- [ ] Vérifiez que la clé est déployée (redéployez si besoin)

### Frontend ne trouve pas l'API
- [ ] Vérifiez `REACT_APP_BACKEND_URL`
- [ ] Testez directement: `curl $REACT_APP_BACKEND_URL/api/health`
- [ ] Vérifiez les CORS dans le backend

### Paiements Stripe ne fonctionnent pas
- [ ] Vérifiez `STRIPE_API_KEY` est un `sk_live_` ou `sk_test_`
- [ ] Vérifiez `REACT_APP_STRIPE_PUBLIC_KEY` est un `pk_`
- [ ] Testez en mode test avant production

---

## 📚 Ressources Rapides

| Platform | Lien |
|----------|------|
| Emergent Dashboard | https://app.emergent.sh |
| OpenAI API Keys | https://platform.openai.com/api-keys |
| Astrology API IO | https://www.astrology-api.io |
| Stripe Dashboard | https://dashboard.stripe.com |
| Railway App | https://railway.app |
| Vercel | https://vercel.com |
| Documentation | [ENV_SETUP.md](./ENV_SETUP.md) |

---

## ✅ Finalisation

Après tous les déploiements:

- [ ] Tester l'application en production
- [ ] Vérifier tous les paiements
- [ ] Vérifier le chat LLM
- [ ] Vérifier les endpoints d'astrologie
- [ ] Vérifier les logs pour les erreurs
- [ ] Communiquer la version déployée à l'équipe
- [ ] Documenter tout changement effectué

---

**Créé le:** 2026-07-07  
**Dernière mise à jour:** 2026-07-07  
**Responsable:** DevOps Team
