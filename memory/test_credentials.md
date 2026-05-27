# Test Credentials — Plume Astrale

## 👑 Compte ADMIN (super utilisateur)

```
EMAIL    : admin@plume-astrale.fr
PASSWORD : PlumeAdmin2026
```

- **9999 crédits** pour tester tous les produits sans limite
- **is_admin = true** → accès au dashboard `/admin`
- Données natales : Paris, 15/05/1990, 12h00

Dashboard admin disponible via :
- Le menu "Mon Compte" → "Tableau de bord"
- Ou directement : https://consultation-astro.preview.emergentagent.com/admin

## Compte utilisateur standard (test)

```
EMAIL    : plume_test_863a0303@gmail.com
PASSWORD : TestPlume2026!
```

## Codes promo actifs

- `PLUMEASTRALE` — 100 credits
- `TESTPLUME` — 200 credits (test)
- `BIENVENUE` — 50 credits

## Stripe test (dev)

- Carte succès : `4242 4242 4242 4242` + exp future + CVC quelconque
- Carte 3DS : `4000 0025 0000 3155`
- Carte refusée : `4000 0000 0000 0002`

## Notes techniques

- Supabase utilise des **clés asymétriques ES256** (verif via JWKS).
- Email confirmation **DÉSACTIVÉE** côté Supabase (l'utilisateur l'a fait dans le dashboard).
- Le trigger `handle_new_user` crée auto le profile + wallet (20cr) à chaque signup.
- Endpoints admin protégés par dependency `require_admin` (check `profiles.is_admin = true`).
