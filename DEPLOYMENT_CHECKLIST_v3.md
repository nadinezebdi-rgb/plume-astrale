# 🚀 REDÉPLOIEMENT PRODUCTION - Checklist Complète

## Phase 1: Vérification Pré-Déploiement

### SQL Migrations (À faire AVANT redeploy)
- [ ] Exécuter `supabase/complete_migration_v3.sql` dans Supabase SQL Editor
- [ ] Vérifier que:
  - [ ] archetype_readings table créée
  - [ ] promo_codes.premium_days colonne ajoutée
  - [ ] Tous les codes promo insérés (ADMIN26, BIENVENUE10, LUNE20, etc.)

### Vérifier Variables d'Environnement Railway

```bash
URL: https://railway.app/dashboard
Navigation: Votre Projet Plume Astrale → Backend Service

Variables à vérifier:
  ✅ SUPABASE_URL = https://ebwicqvbkwogxneipaxh.supabase.co
  ✅ SUPABASE_SERVICE_ROLE_KEY = (non vide, commence par eyJ)
  ✅ SUPABASE_ANON_KEY = (non vide)
  ✅ SUPABASE_JWT_SECRET = <REDACTED - a regenerer>
  ✅ ASTROLOGY_API_USER_ID = <REDACTED>
  ✅ ASTROLOGY_API_KEY = <REDACTED - a regenerer>
  ✅ ASTROLOGY_API_ACCESS_TOKEN = <REDACTED - a regenerer>
  ✅ OPENAI_API_KEY = sk_... (non vide)
  ✅ CORS_ORIGINS = https://plume-astrale.fr,https://app.emergent.sh
  ✅ EMERGENT_LLM_KEY = (ta clé Emergent)
```

### Vérifier Variables d'Environnement Emergent

```bash
URL: https://app.emergent.sh → Applications → consultation-astro

Variables à vérifier:
  ✅ OPENAI_API_KEY = sk_...
  ✅ ASTROLOGY_API_IO_KEY = ask_...
  ✅ JWT_SECRET = (long + secure)
  ✅ CORS_ORIGINS = inclut plume-astrale.fr
```

---

## Phase 2: Déploiement

### 2A: Déploiement Backend (Railway)

```bash
# Terminal: À la racine du repo

# 1. Créer branche de déploiement
git checkout -b deploy/v3.0-migrations-archetype

# 2. Copier la migration SQL vers le commit (optionnel - juste pour tracking)
git add supabase/complete_migration_v3.sql

# 3. Commit et push
git commit -m "chore: Add complete migration v3.0 (archetype + discount codes)"
git push origin deploy/v3.0-migrations-archetype

# 4. Créer PR vers main (optionnel)
# ou directement:
git checkout main
git merge deploy/v3.0-migrations-archetype
git push origin main

# 5. Railway auto-redéploie après git push (5-10 min)
```

**Vérifier le déploiement:**
- Aller sur: https://railway.app/dashboard
- Service Backend → Deployments
- Chercher la dernière déploiement: status "Success" (vert)
- Noter l'URL: `https://plume-backend.up.railway.app` (ou similaire)

### 2B: Déploiement Frontend (Netlify)

**Option 1: Redéploiement automatique (si repo lié)**
```bash
# Après push à main, Netlify redéploie automatiquement
# Aller sur: https://app.netlify.com/sites/plume-astrale/deploys
# Status: "Published" (vert) après 2-5 min
```

**Option 2: Redéploiement manuel**
```bash
# Si Netlify ne redéploie pas auto:
# 1. Aller sur: https://app.netlify.com/sites/plume-astrale/deploys
# 2. Cliquer: "Trigger deploy" → "Deploy site"
# 3. Attendre status "Published"
```

### 2C: Déploiement Emergent

```bash
# Sur https://app.emergent.sh:
# 1. Applications → consultation-astro
# 2. Cliquer: "Redeploy" ou "Trigger Build"
# 3. Attendre: status "Running" (vert)
```

---

## Phase 3: Smoke Tests (Validation Post-Déploiement)

### Test 1: API Health Check
```bash
# Doit retourner 200 + JSON
curl https://plume-backend.up.railway.app/health
curl https://plume-astrale.fr/api/health  # Après domain config

# Réponse attendue:
# { "status": "ok", "version": "3.0" }
```

### Test 2: Archetype Endpoint (Critical)
```bash
# Test sans auth (doit rejeter avec 401):
curl https://plume-astrale.fr/api/archetype/history

# Réponse attendue: 401 Unauthorized
```

### Test 3: Promo Codes (Non-auth)
```bash
# Récupérer les codes actifs:
curl https://plume-astrale.fr/api/promo-codes/list

# Réponse attendue: Array JSON avec ADMIN26, LUNE20, ARCHETYPE100, etc.
```

### Test 4: Frontend Load
```bash
# Ouvrir dans navigateur:
https://plume-astrale.fr/

# Checklist visuelle:
  ✅ Page charge sans erreur
  ✅ Logo + navbar visibles
  ✅ "Découvrir" buttons clickables
  ✅ Pas de console errors (F12 → Console)
  ✅ Pas de "CORS" errors
```

### Test 5: Product Pages (Archetype Spécial)
```bash
# Aller sur: https://plume-astrale.fr/archetype
# Checklist:
  ✅ Page charge
  ✅ Bouton "Générer mon archétype" visible
  ✅ Si connecté: peut cliquer (sinon redirect login)
  ✅ Pas d'erreur 404 ou 500
```

---

## Phase 4: Monitoring Post-Déploiement

### Vérifier les Logs

**Railway Logs:**
```bash
# https://railway.app → Backend Service → Logs
# Chercher: 
  - "Archetype routes initialized" ✅
  - Pas de "ERROR" ou "exception"
  - Health check responses (200 OK)
```

**Emergent Logs:**
```bash
# https://app.emergent.sh → Applications → consultation-astro → Logs
# Chercher:
  - "Application started" ✅
  - "CORS headers enabled" ✅
  - Pas de auth failures massives
```

### Alertes à Surveiller

| Alerte | Cause | Fix |
|--------|-------|-----|
| 500 errors sur `/api/archetype/*` | Archetype table still missing | Re-exécuter migration SQL |
| 400 errors avec "premium_days" | Column still missing | Vérifier ALTER TABLE schema |
| CORS errors au frontend | CORS_ORIGINS mal config | Vérifier Railway env vars |
| 401 errors partout | SUPABASE_JWT_SECRET incorrect | Vérifier Railway + Emergent keys |

---

## Phase 5: Rollback Plan (Si problèmes)

Si tout crash après déploiement:

```bash
# 1. Revert Git:
git revert HEAD  # Ou revert commit spécifique
git push origin main

# 2. Railway auto-redéploie depuis Git (5 min)

# 3. Vérifier status:
curl https://plume-astrale.fr/health
# Doit redevenir OK

# 4. Réexaminer logs pour trouver le problème
```

---

## ✅ CHECKLIST FINALE

- [ ] SQL migrations exécutées + vérifiées (archetype_readings existe)
- [ ] Variables d'env vérifiées Railway
- [ ] Variables d'env vérifiées Emergent
- [ ] Git push à main (déclenche Railway build)
- [ ] Railway déploiement réussi (status "Success")
- [ ] Netlify déploiement réussi (status "Published")
- [ ] Emergent redéploiement réussi (status "Running")
- [ ] Domain config finalisée (DNS pointe vers Emergent)
- [ ] Smoke tests passés (health check, archetype, promo codes)
- [ ] Pas d'erreurs dans les logs
- [ ] Production OK ✅ 🚀

---

## 📞 SUPPORT

Si problèmes:
1. Vérifier Logs Railway + Emergent
2. Vérifier Variables d'env dans les 2 platforms
3. Vérifier DNS propagation: https://www.whatsmydns.net/?domain=plume-astrale.fr
4. Rollback et réessayer après 15 min
