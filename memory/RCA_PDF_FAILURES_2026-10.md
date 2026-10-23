# RCA — 3 PDFs Thème Natal échoués (semaine du 20-21 octobre 2026)

## Résumé exécutif
3 échecs de génération PDF sur un seul utilisateur (`nadine.zebdi@gmail.com`), tous via l'endpoint admin `theme_natal_pdf_oneshot`. **Les 3 erreurs sont des gardes anti-slop qui ont fonctionné comme prévu** — elles ont refusé de livrer un PDF incomplet.

| # | Session | Date (UTC) | Erreur | Cause racine |
|---|---------|------------|--------|--------------|
| 1 | `admin-natal-05cd53f6` | 2026-10-21 06:59 | `astrology-api.io a retourné 0 planètes (core manquantes: ['sun','moon','mercury','venus','mars'])` | **Clé API `ASTROLOGY_API_IO_KEY` invalide/expirée au moment de l'appel** |
| 2 | `admin-natal-23647d02` | 2026-10-20 20:04 | Idem #1 | Idem #1 |
| 3 | `admin-natal-fb5885d2` | 2026-10-20 19:39 | `Livre enrichi incomplet : sections=[], planètes=['Soleil','Lune','Vénus'].` | **Enrichissement GPT (natal_ai_enrichment) a renvoyé un payload incomplet** — très probablement un timeout OpenAI transitoire |

## Preuves
- `ASTROLOGY_API_IO_KEY` dernière mise à jour : **2026-10-22T09:26:51Z** (≈ 2h30 après la 3ème erreur).
- Reproduction avec le `birth_data` stocké de Nadine via `aio.natal_chart()` **aujourd'hui = succès** (12 planètes retournées en 1.96s).
- Les logs backend du 2026-05-29 montrent déjà `[astrology_io] /pdf/natal-report -> 401 : UNAUTHORIZED "Invalid credentials"` — pattern récurrent côté astrology-api.io quand la clé expire.

## birth_data stocké (3 sessions, identique)
```json
{"day": 17, "city": "SAINT AVOLD", "hour": 1, "year": 1968,
 "month": 7, "minute": 40, "country_code": "France"}
```
Note : `country_code: "France"` au lieu de `"FR"` était un bug précédemment identifié (handoff Feb 2026), mais `normalize_birth_data()` le corrige désormais → `"FR"`. Testé OK.

## Actions correctives
1. **Rejouer les 3 transactions** via `POST /api/admin/regenerate/{session_id}` avec `force=true` — l'API Stripe est désormais disponible et la clé astrology-api.io est valide.
2. **Monitoring proposé** : alerter dès que `payment_transactions.metadata.pdf_error` contient `"a retourné 0 planètes"` plus d'une fois dans l'heure → signal clair d'expiration de clé API externe.
3. **Fix préventif** : wrapper `aio.natal_chart()` avec un health-check au boot pour détecter immédiatement une clé invalide (plutôt qu'au premier appel user).

## Commande de rejeu suggérée (admin)
```bash
for SID in admin-natal-05cd53f6 admin-natal-23647d02 admin-natal-fb5885d2; do
  curl -X POST "$API_URL/api/admin/regenerate/$SID?force=true" \
       -H "Authorization: Bearer $ADMIN_TOKEN"
done
```
