# 🔧 Audit + fix du handler Stripe — les 3 pièges classiques

Suite au conseil pertinent d'un audit externe : « Le vrai risque n'est pas le secret, c'est le handler. Les 3 pièges classiques sont raw body, réponse 200 en < 30 s, idempotence event.id. » — voici l'audit complet et les correctifs.

## Ma stack
- **Backend** : FastAPI (Python 3.11) + Supabase (Postgres) + Stripe SDK Python
- **PDF** : ReportLab (généré backend) → upload Supabase Storage → email Resend
- **Route webhook** : `POST /api/webhook/stripe`

## Audit des 3 pièges

### ✅ Piège #1 — Raw body : **OK avant le fix**
```python
body = await request.body()  # bytes raw
event = stripe.Webhook.construct_event(body, sig, webhook_secret)  # OK
```
FastAPI ne parse pas le body automatiquement pour cet endpoint (pas de body Pydantic dans la signature). Le SDK Stripe reçoit donc les bytes tels quels et la HMAC-SHA256 valide correctement.

### ❌ Piège #2 — Répondre 200 sous 30 s : **CASSÉ, maintenant fixé**
Avant : le handler faisait `await handle_theme_natal_oneshot_webhook(session_id)` etc. Ces handlers font :
- Astrology API v3 (≤ 30 s)
- Enrichissement GPT (≤ 90 s)
- Génération PDF ReportLab (≤ 60 s)
- Upload Supabase Storage (≤ 30 s, PDFs ~ 27 Mo)
- Envoi Resend (≤ 10 s)
→ **60 à 300 s au total**, largement au-dessus des 30 s Stripe.
→ Stripe considère l'endpoint down → **retry 4 fois** (jusqu'à 3 j) → doublons de PDFs/emails.

**Correctif appliqué** :
```python
@api_router.post('/webhook/stripe')
async def stripe_webhook(request: Request):
    # 1. Verify signature (fast, ~10 ms)
    # 2. Insert idempotence row (fast, ~50 ms)
    # 3. Fire-and-forget:
    asyncio.create_task(_process_stripe_event(event, event_type, data_obj, event_id))
    return {'received': True, 'queued': True, 'event_id': event_id}
```
Réponse en **< 500 ms** measured. Le processing lourd tourne en tâche background.

### ⚠️ Piège #3 — Idempotence event.id : **partiel avant, complet maintenant**
Avant : certains handlers utilisaient des flags métier (`bundle_dispatched`, `pdf_status: 'success'`, `credits_granted`) — bonne pratique, mais pas de guard global. Un handler qui crashait entre la génération PDF et le flag update pouvait ré-envoyer le PDF au retry.

**Correctif appliqué** :
- Nouvelle table Postgres `stripe_webhook_events` (PK = `event_id`)
- INSERT en amont de tout traitement
- PK conflict (`23505`) → retour `{'received': True, 'idempotent': True}` immédiat
- Colonne `status` (`processing` | `done` | `failed`) + `error_message` pour observer les échecs
- Le wrapper `_process_stripe_event` marque `done` ou `failed` en fin de tâche

## Migration Supabase à jouer (30 s)
Copier-coller dans **Supabase → SQL Editor → Run** :
`/app/backend/migrations/2026_02_28_stripe_webhook_events.sql`

Le code fonctionne en **mode dégradé** (logs warning, sans idempotence) tant que la table n'existe pas, donc tu peux déployer sans jouer la migration en premier — mais sans elle, un retry Stripe pourrait doubler la livraison.

## Retour d'un échec handler
Si un handler crashe en background, la ligne dans `stripe_webhook_events` passe en `status='failed'` avec `error_message`. Tu peux les voir dans le dashboard admin :
```sql
SELECT event_id, event_type, session_id, kind, error_message, received_at
FROM stripe_webhook_events
WHERE status = 'failed'
ORDER BY received_at DESC;
```
Et rejouer via l'endpoint admin `/api/admin/stripe-recovery` (déjà livré) qui interroge Stripe et redéclenche la livraison si `paid`.

## Test de régression
`/app/backend/tests/test_stripe_webhook_refactor.py` — **8/8 tests pass**, exécution 6 s. Verrouille les 3 pièges contre toute régression future.

## Étapes finales à ta charge

1. **Jouer la migration SQL** dans Supabase SQL Editor (30 s)
2. **Créer l'endpoint webhook dans Stripe Dashboard** en mode LIVE avec l'URL `https://plume-astrale.fr/api/webhook/stripe` et les events :
   - `checkout.session.completed`
   - `payment_intent.payment_failed` (pour logger les échecs, optionnel)
   - `charge.refunded`, `refund.created`, `refund.updated`
   - `customer.subscription.*`
   - `invoice.payment_succeeded`
3. **Reveal le Signing secret**, puis coller directement dans `.env` de prod (variable `STRIPE_WEBHOOK_SECRET`), sans passer par le chat
4. **Redéployer** (bouton Deploy dans l'interface Emergent)

Après ça, teste avec Stripe CLI :
```bash
stripe listen --forward-to https://plume-astrale.fr/api/webhook/stripe
stripe trigger checkout.session.completed
```
Tu dois voir dans les logs backend `[stripe_webhook] event evt_... queued` en < 1 s, puis quelques minutes plus tard `[stripe_webhook processor] event evt_... done`.
