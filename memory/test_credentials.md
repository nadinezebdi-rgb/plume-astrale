# Test Credentials — Plume Astrale

## 👑 Compte ADMIN (super utilisateur)

```
EMAIL    : admin@plume-astrale.fr
PASSWORD : PlumeAdmin2026
```

- **is_admin = true** en base Supabase → accès au dashboard `/admin`
- Password re-set le 2026-08-02 via `supabase.auth.admin.update_user_by_id` (précédent était rejeté)
- Données natales : Paris, 15/05/1990, 12h00
- Une commande lecture_complete de test `e2e-admin-lecture-001` est active (pour valider le badge Cercle 90j sur /mon-compte)

Dashboard admin disponible via :
- `/admin` → tabs : Utilisateurs / Paiements / Codes promo / PDFs envoyés / Fix Thème Natal / **Lecture Complète** (nouvel onglet)

## Compte utilisateur standard (test)

```
EMAIL    : test@plume-astrale.fr
PASSWORD : TestPlume2026!
```

- Créé le 2026-08-02 (l'ancien `plume_test_863a0303@gmail.com` n'existait plus)
- is_admin = false — utilisable pour tester les 403 non-admin sur `/api/lecture-complete/admin/*`

## Codes promo actifs

- `TOUT2026` — bypass admin 100% (nécessite is_admin=true)
- `PLUMEASTRALE` — 100 credits
- `TESTPLUME` — 200 credits (test)
- `BIENVENUE` — 50 credits
