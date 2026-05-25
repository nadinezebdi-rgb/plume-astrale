# Test Credentials — Plume Astrale

## Compte test (Supabase Auth)

```
EMAIL: plume_test_863a0303@gmail.com
PASSWORD: TestPlume2026!
```

Solde initial : 20 credits (signup bonus auto via trigger Supabase).

## Codes promo actifs

- `PLUMEASTRALE` — 100 credits
- `TESTPLUME` — 200 credits (test)
- `BIENVENUE` — 50 credits

## Stripe test

Cartes test Stripe (mode sandbox `sk_test_emergent`) :
- Carte succes : `4242 4242 4242 4242`, exp future, CVC quelconque
- Carte 3D Secure : `4000 0025 0000 3155`

## Notes

- Le projet Supabase utilise des cles asymetriques (ES256) — verifie via JWKS endpoint.
- Email confirmation : actuellement actif. Pour creer des users en bypass utiliser l'admin API.
