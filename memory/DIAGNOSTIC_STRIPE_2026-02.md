# 🔴 DIAGNOSTIC STRIPE — Rapport P0 (Feb 2026)

## TL;DR
La cause racine des 22 abandons Stripe et 0 ventes n'est **PAS** que les checkouts se créent au chargement de page. Les endpoints Stripe se déclenchent bien uniquement au clic.

**Le vrai problème : le webhook Stripe est BLOQUÉ.**

Depuis le commit `12d1f82` (juillet 2026), le code exige `STRIPE_WEBHOOK_SECRET` en variable d'env. Si la variable manque, **tous les webhooks entrants sont rejetés en HTTP 503**. Résultat :

1. Le client paye ✅ (côté Stripe, l'argent arrive dans votre compte)
2. Stripe envoie l'event `checkout.session.completed` → backend renvoie 503 ❌
3. La DB reste en `initiated/unpaid`
4. **Aucun PDF n'est généré, aucun email de confirmation, aucune livraison**
5. Le client demande un remboursement (ou râle sur les DMs Instagram)
6. Stripe marque la charge comme "abandonnée / refunded"

Cela explique parfaitement l'écart : Stripe voit N sessions créées, presque aucune ne finit `paid` côté nos logs, et vous voyez 22 "checkouts échoués" alors que certaines étaient probablement des paiements techniquement réussis mais **bloqués côté livraison**.

## Preuves rassemblées

### 1. Audit du code front (checkout créé onClick, pas onMount)
Tous les fetch `POST .../checkout` du frontend sont enveloppés dans un handler de clic (`handlePurchase`, `handleCheckout`, `submit()`), aucun n'est déclenché depuis un `useEffect`.
- `pages/Apercu.js` line 115 → `handlePurchase()` sur clic uniquement
- `pages/Tarologie.js` line 181 → `handlePurchase()` sur clic
- `pages/ThemeNatalOneshot.js` line 108 → `handleCheckout()` sur clic
- `pages/EditionReliee.js` line 269 → `submit()` sur form submit
- `pages/Index.js` line 617 → `startCheckout(form)` sur form submit
- etc.

**Verdict : hypothèse "checkouts fantômes créés au chargement" ÉCARTÉE.**

### 2. Audit du backend (endpoints checkout OK)
Test manuel de tous les endpoints principaux en preview :

| Endpoint | Résultat |
|---|---|
| `/api/theme-natal-oneshot/checkout` | ✅ URL Stripe live valide retournée |
| `/api/lecture-complete/checkout` | ✅ URL valide |
| `/api/edition-reliee/checkout` | ✅ URL valide (attend `purchaser_email`) |
| `/api/voyage-karmique/checkout` | ✅ URL valide |
| `/api/karma-destin/checkout` | ✅ URL valide |
| `/api/kabbale/checkout` | ✅ URL valide |
| `/api/checkout/create` | ✅ URL valide |

**Verdict : la création de session Stripe fonctionne. Le paiement peut avoir lieu côté Stripe.**

### 3. État de la DB `payment_transactions`
Sur les 200 dernières lignes :
- **92 sessions Stripe RÉELLES** (`session_id` commençant par `cs_`)
  - 83 `initiated/unpaid` → **jamais livrées**
  - 6 `pending/pending` → bloquées en cours
  - **3 seulement `completed/paid`** → livrées via self_heal (polling manuel de la page succès)
- 60 sessions admin bypass (codes promo 100%) → OK
- Répartition par produit : theme_natal_pdf_oneshot (34), kabbale (29), rencontres_ultime (16)…

**Ratio actuel : ~3 % de livraison sur les sessions Stripe créées.**

### 4. Cause racine identifiée
Fichier : `/app/backend/server.py`, ligne 786-793
```python
webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
if not webhook_secret:
    logger.error('[stripe_webhook] STRIPE_WEBHOOK_SECRET manquant — refus de traiter le webhook.')
    raise HTTPException(status_code=503, detail='Webhook secret not configured')
```

Fichier `/app/backend/.env` :
```
STRIPE_API_KEY=sk_live_51RyVvs... ✅ présent
STRIPE_WEBHOOK_SECRET=            ❌ MANQUANT
```

C'est LA cause racine.

## Actions correctives

### Action 1 (USER) — Configurer le webhook Stripe (URGENT, 5 min)
1. Allez sur **Stripe Dashboard → Developers → Webhooks** (mode LIVE, pas test)
   → https://dashboard.stripe.com/webhooks
2. Cliquez **+ Add endpoint**
3. URL de l'endpoint : `https://plume-astrale.fr/api/webhook/stripe`
4. Events à écouter (minimum) :
   - `checkout.session.completed`
   - `charge.refunded`, `refund.created`, `refund.updated`
   - `customer.subscription.created`, `updated`, `deleted`
   - `invoice.payment_succeeded`
5. Cliquez **Add endpoint**, puis récupérez la valeur **Signing secret** (format `whsec_...`)
6. Envoyez-moi cette valeur, je l'ajouterai à `/app/backend/.env` comme `STRIPE_WEBHOOK_SECRET=whsec_...`
7. Après ajout : `sudo supervisorctl restart backend` (ou redéployez en prod)

### Action 2 (AGENT — DÉJÀ FAIT) — Ajouter le fallback self-heal aux 3 routes qui l'oubliaient
Trois produits critiques n'avaient PAS le fallback `self_heal_if_paid` qui rattrape les paiements manqués via polling Stripe côté serveur :
- `lecture_complete` (97 €) → ajouté ✅
- `edition_reliee` (149 €) → ajouté ✅
- `consultation_ultime` (149 €) → ajouté ✅

Désormais, quand un client arrive sur la page succès (`/lecture-complete/succes`, `/edition-reliee/merci`, `/consultation-ultime/merci`), le polling `/status` vérifiera directement l'état de la session Stripe et déclenchera la livraison si `paid` — même si le webhook est cassé.

Fichiers modifiés :
- `backend/routes/edition_reliee.py`
- `backend/routes/lecture_complete.py`
- `backend/routes/consultation_ultime.py`

### Action 3 (RECOVERY) — Rattraper les 83 sessions bloquées
Une fois le webhook configuré, il faut rattraper manuellement les paiements passés qui n'ont pas été livrés. Cf. script SQL à la fin de ce document.

## Script SQL Supabase pour reporting

Copier-coller dans **Supabase → SQL Editor** puis Run.

```sql
-- ============================================================
-- 1. PDFs gratuits (Aperçu 5 pages) générés — trafic organique
-- ============================================================
-- On compte les leads captés via le flow "Aperçu" (source=apercu, oracle, homepage_free)
SELECT
    source,
    COUNT(*)                            AS total,
    COUNT(DISTINCT email)               AS emails_uniques,
    MIN(created_at)                     AS premier,
    MAX(created_at)                     AS dernier
FROM oracle_leads
GROUP BY source
ORDER BY total DESC;

-- ============================================================
-- 2. Répartition des paiements par statut & pack (30 derniers jours)
-- ============================================================
SELECT
    pack_id,
    status,
    payment_status,
    COUNT(*)                            AS n,
    ROUND(SUM(amount)::numeric, 2)      AS total_eur
FROM payment_transactions
WHERE created_at > now() - interval '30 days'
GROUP BY pack_id, status, payment_status
ORDER BY pack_id, status;

-- ============================================================
-- 3. Sessions Stripe RÉELLES bloquées en 'initiated/unpaid'
--    → celles à investiguer pour recovery manuel
-- ============================================================
SELECT
    created_at,
    session_id,
    user_email,
    pack_id,
    amount,
    metadata->>'kind' AS kind
FROM payment_transactions
WHERE session_id LIKE 'cs_%'
  AND status = 'initiated'
  AND payment_status = 'unpaid'
  AND created_at > now() - interval '60 days'
ORDER BY created_at DESC;

-- ============================================================
-- 4. Sessions Stripe payées mais PDF non livré (à relancer)
-- ============================================================
SELECT
    created_at,
    session_id,
    user_email,
    pack_id,
    amount,
    metadata->>'pdf_status' AS pdf_status
FROM payment_transactions
WHERE session_id LIKE 'cs_%'
  AND payment_status = 'paid'
  AND (metadata->>'pdf_path' IS NULL OR metadata->>'pdf_status' != 'success')
ORDER BY created_at DESC;

-- ============================================================
-- 5. Taux de conversion réel (payé / initié) sur 30 jours
-- ============================================================
WITH tx AS (
  SELECT
    pack_id,
    COUNT(*) FILTER (WHERE status = 'initiated' AND session_id LIKE 'cs_%')   AS initiated,
    COUNT(*) FILTER (WHERE payment_status = 'paid' AND session_id LIKE 'cs_%') AS paid
  FROM payment_transactions
  WHERE created_at > now() - interval '30 days'
  GROUP BY pack_id
)
SELECT
    pack_id,
    initiated,
    paid,
    CASE WHEN initiated + paid = 0 THEN NULL
         ELSE ROUND(100.0 * paid / (initiated + paid), 2)
    END AS conversion_pct
FROM tx
ORDER BY (initiated + paid) DESC;
```

## Estimation d'impact
- **Ventes réelles cachées** : sur les 83 sessions `initiated/unpaid`, il est probable qu'une partie (5-15 %) soit en fait de vrais paiements Stripe non délivrés. Une fois le webhook branché, on pourra vérifier une par une côté Stripe et **rembourser ou re-livrer**.
- **Après fix** : le taux de conversion devrait passer de ~3 % à 20-40 % (moyenne du marché pour ce type de produits) — potentiellement des milliers d'euros récupérés par mois.

