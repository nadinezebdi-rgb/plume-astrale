# 🔧 Guide de Configuration des Variables d'Environnement

## Vue d'Ensemble

Votre application **consultation-astro** utilise trois clés API principales :
- **OPENAI_API_KEY** : Clé OpenAI (GPT-4o-mini pour Plume Chat)
- **ASTROLOGY_API_IO_KEY** : Clé API d'astrologie (api.astrology-api.io)
- **EMERGENT_LLM_KEY** : Clé universelle Emergent (optionnelle, legacy)

---

## 1️⃣ Configuration Locale (Développement)

### Étape 1 : Créer votre fichier `.env`
```bash
cp .env.example .env
```

### Étape 2 : Remplir les variables requises
Ouvrez `.env` et complétez :
```env
OPENAI_API_KEY=sk-...
ASTROLOGY_API_IO_KEY=ask_...
EMERGENT_LLM_KEY=...
JWT_SECRET=your_jwt_secret
STRIPE_API_KEY=sk_live_...
```

### Étape 3 : Vérifier avec Docker Compose
```bash
docker-compose up
```

---

## 2️⃣ Déploiement sur Emergent (app.emergent.sh)

### Accéder à l'Interface
1. Connectez-vous à https://app.emergent.sh
2. Allez dans **Home** → onglet **"Deployed Apps"**
3. Trouvez votre application **"consultation-astro"**

### Configurer les Variables
1. Cliquez sur votre application
2. Cherchez **"Environment Variables"** ou **"Settings"**
3. Cliquez sur **"Configure"** ou **"Edit"**

### Ajouter les Clés API
Ajoutez ces variables d'environnement :

| Variable | Valeur | Source |
|----------|--------|--------|
| `OPENAI_API_KEY` | `sk-...` | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `ASTROLOGY_API_IO_KEY` | `ask_...` | [Astrology API IO](https://www.astrology-api.io) |
| `EMERGENT_LLM_KEY` | **(optionnel)** | Profil Emergent → Universal Key |
| `STRIPE_API_KEY` | `sk_live_...` | [Stripe Dashboard](https://dashboard.stripe.com) |
| `JWT_SECRET` | `random_secret` | Générez une clé aléatoire sécurisée |

### Récupérer l'EMERGENT_LLM_KEY
1. Cliquez sur l'**icône de profil** (haut droit)
2. Sélectionnez **"Universal Key"** ou **"Clé Universelle"**
3. **Copiez** la clé affichée
4. **Collez-la** dans les variables du déploiement

### Redéployer l'Application
1. Cliquez sur **"Redeploy"** ou **"Redéployer"**
2. **Attendez 10-15 minutes** que le redéploiement se termine
3. Vérifiez que l'application démarre sans erreurs

---

## 3️⃣ Déploiement sur Railway (railway.app)

### Accéder aux Variables
1. Connectez-vous à https://railway.app
2. Sélectionnez votre projet
3. Cliquez sur le service backend
4. Allez à l'onglet **"Variables"**

### Ajouter les Clés
Cliquez sur **"Add Variable"** et remplissez :
```
OPENAI_API_KEY = sk-...
ASTROLOGY_API_IO_KEY = ask_...
EMERGENT_LLM_KEY = ...
STRIPE_API_KEY = sk_live_...
JWT_SECRET = your_secret
```

### Redéployer
Cliquez sur **"Redeploy"** dans le panneau de déploiement.

---

## 4️⃣ Déploiement sur Vercel (Frontend)

### Accéder aux Variables
1. Connectez-vous à https://vercel.com
2. Sélectionnez le projet **frontend**
3. Allez à **Settings** → **Environment Variables**

### Ajouter les Variables Frontend
Cliquez sur **"Add New"** :
```
REACT_APP_BACKEND_URL = https://your-api-domain.com
REACT_APP_API_URL = https://your-api-domain.com/api
REACT_APP_STRIPE_PUBLIC_KEY = pk_...
```

### Redéployer
Les changements se déploient automatiquement ou cliquez sur **"Redeploy"**.

---

## 5️⃣ Sauvegarder sur GitHub (Optionnel)

⚠️ **ATTENTION** : Ne jamais commiter le fichier `.env` !

### Procédure
1. Retournez dans le chat du projet Emergent
2. Cliquez sur **"Save to GitHub"**
3. Sélectionnez la branche (ex: `main`)
4. Cliquez sur **"PUSH TO GITHUB"**

**Prérequis** : Compte GitHub connecté à Emergent + abonnement payant

---

## 📋 Checklist de Configuration

### Avant Déploiement en Production
- [ ] ✅ `.env` rempli localement avec tous les secrets
- [ ] ✅ OPENAI_API_KEY valide testé
- [ ] ✅ ASTROLOGY_API_IO_KEY valide testé  
- [ ] ✅ EMERGENT_LLM_KEY configuré sur Emergent (si utilisation legacy)
- [ ] ✅ STRIPE_API_KEY présent pour les paiements
- [ ] ✅ JWT_SECRET défini (32+ caractères aléatoires)
- [ ] ✅ `.env` ajouté au `.gitignore`

### Après Redéploiement
- [ ] ✅ Application démarre sans erreurs
- [ ] ✅ API /health répond (HTTP 200)
- [ ] ✅ Chat LLM fonctionne
- [ ] ✅ Endpoints d'astrologie répondent
- [ ] ✅ Paiements Stripe actifs

---

## 🔍 Dépannage

### Erreur : "OPENAI_API_KEY manquante"
```
Error: OPENAI_API_KEY env var manquante
```
**Solution** : Vérifiez que OPENAI_API_KEY est configurée dans Emergent/Railway/votre serveur.

### Erreur : "ASTROLOGY_API_IO_KEY invalid"
```
Response 401: Invalid credentials
```
**Solution** : La clé est invalide ou expirée. Vérifiez sur https://www.astrology-api.io

### Erreur : "Cannot connect to backend API"
```
ECONNREFUSED: Connection refused
```
**Solution** : Vérifiez que REACT_APP_BACKEND_URL pointe vers le bon domaine.

### Les variables ne se mettent pas à jour après redéploiement
**Solution** : 
1. Attendez 2-3 minutes après le redéploiement
2. Videz le cache du navigateur (Ctrl+Shift+Del)
3. Redéployez à nouveau

---

## 📚 Ressources

| Service | Lien |
|---------|------|
| OpenAI API Keys | https://platform.openai.com/api-keys |
| Astrology API IO | https://www.astrology-api.io |
| Stripe Dashboard | https://dashboard.stripe.com |
| Emergent Dashboard | https://app.emergent.sh |
| Railway Dashboard | https://railway.app |
| Vercel Dashboard | https://vercel.com |

---

## ❓ Questions Fréquentes

**Q: Puis-je stocker le `.env` sur GitHub ?**  
A: **Non !** Ajoutez-le toujours au `.gitignore` pour éviter de leaker les secrets.

**Q: Comment régénérer une clé si je l'ai compromise ?**  
A: Allez sur le dashboard du service (OpenAI, Stripe, etc.), supprimez l'ancienne clé, créez-en une nouvelle.

**Q: Les variables changent en production, comment ça marche ?**  
A: Les déploiements (Emergent, Railway, Vercel) relient automatiquement les variables. Pas besoin de redémarrer le code.

**Q: Combien de temps avant les changements sont actifs ?**  
A: Généralement 10-15 minutes après le redéploiement, selon la plateforme.
