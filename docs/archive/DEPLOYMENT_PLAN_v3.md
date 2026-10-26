# 📊 RÉSUMÉ COMPLET - Déploiement Plume Astrale v3.0

## 🎯 OBJECTIF: Production-Ready avec Archetype + Discount Codes

**Date:** 10 Juillet 2026  
**Status:** ✅ **PRÊT POUR DÉPLOIEMENT**

---

## 📋 PROBLÈMES IDENTIFIÉS & SOLUTIONS

### **Problème #1: archetype_readings Table MANQUANTE ⚠️**

**Symptôme:** 
- Route `/api/archetype/history` → 500 error ou table doesn't exist
- Utilisateurs ne peuvent pas voir l'historique de leurs lectures d'archétype

**Cause:**
- `archetype.py` route existe mais la table Supabase `archetype_readings` n'a jamais été créée
- Référencée dans `backend/routes/archetype.py` ligne 183+

**Solution:**
1. Exécuter `supabase/complete_migration_v3.sql` dans Supabase
2. Cela va créer:
   - Table `archetype_readings` avec colonnes: id, user_id, result (jsonb), created_at
   - Index pour le tri par user + date
   - RLS policies (utilisateurs voient seulement leurs lectures)

**Impact si non-fixed:** 🔴 **PRODUIT CASSÉ** - "Ton Archétype" ne fonctionne pas

---

### **Problème #2: promo_codes.premium_days Colonne MANQUANTE ⚠️**

**Symptôme:**
- Codes premium (DECOUVERTE7=7j, CADEAU30=30j, FIDELITE90=90j) ne fonctionnent pas
- Utilisateurs redeeming ces codes reçoivent 0 crédits au lieu de jours Premium

**Cause:**
- `schema.sql` définit promo_codes sans colonne `premium_days`
- `discount_codes_migration.sql` tente d'insérer des valeurs dans `premium_days`
- Mismatch: colonne existe pas → INSERT fail

**Solution:**
1. `supabase/complete_migration_v3.sql` inclut: `ALTER TABLE public.promo_codes ADD COLUMN IF NOT EXISTS premium_days integer DEFAULT 0;`
2. Puis insère tous les codes promo avec premium_days corrects

**Impact si non-fixed:** 🟠 **REVENUS PERDUS** - Codes Premium offerts ne marchent pas

---

### **Problème #3: DNS plume-astrale.fr → Vercel (Outdated) ⚠️**

**Symptôme:**
- `plume-astrale.fr` charge l'ancienne version déployée sur Vercel
- Pas de DNS pointage vers Emergent (serveur principal)
- Mismatch frontend URL vs backend API

**Cause:**
- DNS nameservers ou CNAME encore configurés pour Vercel
- Emergent deployment existe mais pas accessible via domaine custom

**Solution:**
1. Aller au registrar (OVH, GoDaddy, Namecheap, etc.)
2. Changer DNS vers Emergent nameservers OU configurer CNAME
3. Attendre propagation (5-30 min)
4. Vérifier: `nslookup plume-astrale.fr` → doit afficher Emergent servers

**Impact si non-fixed:** 🟠 **UX MAUVAISE** - Utilisateurs chargent old version

---

### **Problème #4: CORS Configuration À Vérifier ⚠️**

**Symptôme:**
- Frontend sur `plume-astrale.fr` mais backend rejects les requests
- Console error: "CORS header 'Access-Control-Allow-Origin' missing"

**Cause:**
- `CORS_ORIGINS` env var dans Railway peut ne pas inclure domaine Emergent
- Ou mismatch entre frontend URL et backend CORS whitelist

**Solution:**
1. Railway Dashboard → Backend Service → Variables
2. Vérifier: `CORS_ORIGINS` inclut `https://plume-astrale.fr` OU `https://app.emergent.sh`
3. Si pas présent, ajouter

**Impact si non-fixed:** 🔴 **APIS INACCESSIBLES** - Tout les appels API fail

---

## ✅ 4 ÉTAPES DÉPLOIEMENT

### **ÉTAPE 1: Exécuter SQL Migrations ✅**

```sql
-- File: supabase/complete_migration_v3.sql
-- 1. Ajoute promo_codes.premium_days
-- 2. Crée archetype_readings table + index + RLS
-- 3. Insère tous les promo codes (ADMIN26, LUNE20, etc.)

-- À exécuter:
1. Aller: https://supabase.com/dashboard/project/ebwicqvbkwogxneipaxh/sql/new
2. Copy-paste: supabase/complete_migration_v3.sql
3. Click: RUN
4. Attendre: "Migration complete ✅"
```

**Temps:** ~2 min

---

### **ÉTAPE 2: Vérifier Mismatches Frontend/API ✅**

| Composant | Check |
|-----------|-------|
| Backend Routes | ✅ 11 routes OK (archetype, oracle, kabbale, etc.) |
| Frontend Pages | ✅ 20+ pages OK (composants chargent) |
| Archetype Flow | ⚠️ FIXED après migration (history + generate endpoints) |
| CORS Headers | ⚠️ À vérifier Railway env vars |
| Promo Codes | ⚠️ FIXED après migration (premium_days) |

**Après migration SQL:** Tous les mismatches seront fixed ✅

---

### **ÉTAPE 3: Configurer Custom Domain Emergent ✅**

```
Fichier: DOMAIN_CONFIG_EMERGENT.md

Options:
  1. Nameservers Emergent (RECOMMANDÉE)
  2. CNAME record (si no nameservers)
  3. A record IP (si IP statique dispo)

Checklist:
  - [ ] DNS changé
  - [ ] SSL certificate auto-activé
  - [ ] plume-astrale.fr charge sans Vercel
  - [ ] Pas de "mixed content" warnings
```

**Temps:** ~20 min (incluant propagation DNS)

---

### **ÉTAPE 4: Redéploiement Production ✅**

```bash
Fichier: DEPLOYMENT_CHECKLIST_v3.md

Phases:
  1. Pre-deployment verification (5 min)
     - SQL migrations: vérifier archetype_readings + promo_codes
     - Env vars: Railway + Emergent
  
  2. Déploiement (10 min)
     - Git push → Railway auto-build
     - Netlify auto-redeploy (si repo lié)
     - Emergent redeploy manual
  
  3. Smoke tests (5 min)
     - Health check: curl /health → 200
     - Archetype: curl /api/archetype/history → 401 (expected)
     - Promo codes: curl /api/promo-codes/list → codes array
     - Frontend load: plume-astrale.fr → no errors
  
  4. Monitoring (ongoing)
     - Watch logs Railway + Emergent
     - Check for 500 errors, CORS issues, auth failures
```

**Temps:** ~30 min total

---

## 📊 RISQUES & MITIGATION

| Risque | Probabilité | Mitigation |
|--------|-------------|-----------|
| SQL migration fails (syntax error) | 🔴 LOW | Migration idempotent (IF NOT EXISTS, ON CONFLICT) |
| DNS propagation delayed | 🟠 MEDIUM | Attendre 30 min, vérifier whatsmydns.net |
| CORS still broken | 🟠 MEDIUM | Check Railway env vars + Emergent config |
| archetype endpoints 404 | 🔴 LOW | After migration, routes will work |

**Rollback Plan:** `git revert HEAD` → Railway redeploys → back to stable in 5 min

---

## 🚀 POST-DEPLOYMENT

### Vérifications à faire:

```bash
✅ SQL migrations exécutées (archetype_readings table existe)
✅ Promo codes avec premium_days insérés
✅ DNS plume-astrale.fr → Emergent (nslookup test)
✅ SSL certificate activé (https:// works)
✅ Health check: GET /health → 200
✅ Archetype flow: history + generate working
✅ Promo codes: ADMIN26, LUNE20, ARCHETYPE100 redeemable
✅ Frontend loads from https://plume-astrale.fr
✅ No CORS errors in console
✅ No 500 errors in Railway logs
```

### Monitoring:

```bash
Daily checks for 7 days:
  - Railway logs: grep ERROR
  - Emergent logs: grep ERROR, auth failures
  - User reports: Archetype working? Promo codes working?
  - API metrics: response times, error rates
```

---

## 📁 FILES CREATED

| File | Purpose |
|------|---------|
| `supabase/complete_migration_v3.sql` | Combined SQL migration (archetype + promo codes) |
| `DOMAIN_CONFIG_EMERGENT.md` | DNS configuration guide (3 options) |
| `DEPLOYMENT_CHECKLIST_v3.md` | Full deployment + testing checklist |
| `DEPLOYMENT_PLAN_v3.md` | This file - comprehensive overview |

---

## ⏱️ TIMELINE

| Step | Time | Notes |
|------|------|-------|
| 1. Execute SQL migration | 2 min | Supabase SQL editor |
| 2. Verify env vars | 5 min | Railway + Emergent dashboard |
| 3. Git push | 1 min | Terminal: git push origin main |
| 4. Railway auto-build | 5-10 min | Watch deployments page |
| 5. Netlify auto-redeploy | 3-5 min | If repo linked |
| 6. DNS change | 1 min | Edit registrar, wait propagation |
| 7. Smoke tests | 5 min | curl + browser checks |
| **TOTAL** | **~30 min** | (+ 20 min DNS propagation) |

---

## ✨ APRÈS DÉPLOIEMENT

Tout devrait marcher:
- ✅ Utilisateurs peuvent générer leur archétype
- ✅ Historique des lectures sauvegardé + accessible
- ✅ Codes promo premium donnent jours Premium
- ✅ Domain `plume-astrale.fr` pointe vers production
- ✅ SSL certificate activé
- ✅ CORS headers permettent frontend requests
- ✅ Backend 100% OK (déjà validé)
- ✅ Frontend 100% OK (déjà validé)

---

## 📞 PROBLÈME?

Si quelque chose crash après déploiement:

1. **Vérifier les logs:**
   - Railway: https://railway.app → Logs (chercher ERROR)
   - Emergent: https://app.emergent.sh → Logs (chercher ERROR)

2. **Vérifier les env vars:**
   - Rails CORS_ORIGINS
   - Emergent ASTROLOGY_API_IO_KEY
   - Supabase keys valides

3. **Rollback:**
   ```bash
   git revert HEAD
   git push origin main
   # Railway redéploie version précédente
   ```

4. **Re-examine:**
   - SQL migration vraiment exécutée?
   - DNS vraiment changé?
   - Certificats vraiment actifs?

**Support:** Consulter logs + re-run migration si needed
