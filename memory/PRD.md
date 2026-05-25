# Plume Astrale — PRD

## Projet
**Plume Astrale** — Plateforme de guidance astrologique en francais avec IA.
Site prod : plume-astrale.fr

## Architecture (Mai 2026 — Refonte Supabase)
- **Frontend** : React.js + Tailwind + Shadcn UI + `@supabase/supabase-js`
- **Backend** : Python FastAPI + Supabase (Postgres + Auth)
- **Auth** : Supabase Auth (email/password) — JWT asymetriques ES256, verifies via JWKS
- **Paiement** : Stripe (via emergentintegrations) — packs generiques + packs Chat dedies
- **LLM** : EMERGENT_LLM_KEY (GPT-4o-mini) pour Plume Chat
- **APIs externes** : AstrologyAPI (Plan Growth, actif jusqu'au 25/06/2026)
- **Deploy** : Backend Railway / Frontend Netlify

## Implemente — Session Mai 2026 (Refonte complete Supabase)

### Backend (FastAPI + Supabase)
- `config.py` : settings centralises, packs definis cote serveur (anti-tampering)
- `middleware/auth.py` : verification JWT Supabase via JWKS (ES256) avec fallback HS256
- `services/supabase_client.py` : client admin (service_role)
- `services/wallet_service.py` : balance/deduct/add credits + promo redemption
- `services/plume_chat.py` : historique persiste dans Supabase par user_id

### Endpoints
- `GET /api/auth/me` — profil + solde
- `PUT /api/auth/profile` — mise a jour donnees natales
- `GET /api/wallet/balance`, `GET /api/wallet/transactions`
- `POST /api/credits/use` — deduction avec 1er tarot oui/non gratuit
- `POST /api/credits/promo` — codes PLUMEASTRALE/TESTPLUME/BIENVENUE
- `POST /api/credits/checkout` — Stripe pour 6 packs (3 generiques + 3 chat)
- `GET /api/payments/status/{sid}` — polling apres redirection Stripe
- `POST /api/webhook/stripe` — fulfillment automatique
- `POST /api/plume-chat`, `GET /api/plume-chat/history/{sid}` — auth optionnelle
- `GET /api/packs` — liste publique des packs + couts services
- Tarot : oui-non, marseille, celtique, jour
- Ritual : today, moods, checkin
- Journal : entry, history

### Frontend
- `src/lib/supabase.js` : client Supabase pour le frontend
- `src/context/AuthContext.js` : refait avec supabase-js, persistance auto session, JWT vers backend
- Pages Login/Register fonctionnent avec la nouvelle API
- ChatIA.js : 3 messages gratuits anonymes, deduction 2cr/msg connecte, donnees natales auto
- BuyCredits.js : 6 packs (3 generiques + 3 Chat : Lueur/Constellation/Voie Lactee)

### Schema Supabase (8 tables + RLS + trigger auto-signup)
- `profiles` : donnees natales (prenom, birth_date, birth_time, birth_place, lat/lon, gender)
- `wallets` : solde + free_tarot_used
- `credit_transactions` : historique
- `payment_transactions` : Stripe sessions
- `promo_codes` + `promo_code_redemptions`
- `plume_chat_messages` : historique multi-tour
- `streaks` : check-in quotidien
- `journal_entries`
- Trigger `handle_new_user` : auto-cree profile + wallet (20cr) + log transaction

### Deployment
- `backend/railway.toml` + `Procfile`
- `frontend/netlify.toml`
- `supabase/schema.sql` (idempotent — applicable a tout moment)
- `DEPLOY.md` guide complet

#### Compte admin + Dashboard (25 Mai 2026)
- Colonne `is_admin` ajoutee sur `profiles` (migration `supabase/admin_migration.sql`)
- Compte super-admin : `admin@plume-astrale.fr` / `AdminPlume2026!` (9999 credits, Paris)
- `backend/routes/admin.py` : endpoints proteges par dependency `require_admin`
  - `GET /api/admin/stats` — KPIs (users, signups 7j/30j, revenu, conversion, engagement)
  - `GET /api/admin/users?search=` — liste paginée + recherche email + balance + total depensé
  - `GET /api/admin/payments` — historique Stripe (status, credits_granted)
  - `GET /api/admin/transactions` — toutes les operations de credits
  - `GET /api/admin/promo-codes` — codes + utilisations
  - `POST /api/admin/users/{id}/grant-credits` — credit manuel admin
- `frontend/src/pages/Admin.js` refait : 5 onglets, 11 KPI cards, tableaux complets, recherche
- Navbar : link "Tableau de bord" auto-affiché si `user.is_admin === true`
- `/auth/me` retourne maintenant `is_admin` dans le profil utilisateur

## Tests E2E valides (25 Mai 2026)
- Signup Supabase Auth (admin API) -> profile + wallet auto-crees (trigger)
- Login JWT ES256 -> verif JWKS -> /api/auth/me 200 OK
- Wallet balance 20 -> use chat_astral -> 18 -> promo BIENVENUE +50 -> 68
- Stripe checkout pour chat_constellation -> URL Stripe valide retournee
- Plume chat connecte : reponse francaise GPT-4o-mini
- Frontend UI : login redirige proprement, quota affiche correctement

## Backlog

### P1 (prochaine session)
- Page historique des transactions (`/api/wallet/transactions` deja pret)
- Bonus automatique "1 credit gratuit/jour" via streak
- Polling Stripe success page apres paiement
- Reset password / email confirmation flow

### P2
- Page profil pour mettre a jour les donnees natales depuis l'UI
- Geolocation auto pour lat/lon depuis birth_place
- PDF synthese tirage tarot
- Personnaliser scores Alignement Cosmique avec donnees utilisateur
- Systeme de parrainage (+5cr par ami)
- Numerologie/Tarologie : interpretations dynamiques via AstrologyAPI

### Action manuelle utilisateur (avant prod)
- Desactiver "Confirm email" dans Supabase Auth (ou implementer flow)
- Configurer Stripe webhook prod -> Railway
- Ajouter Netlify URL dans Supabase Auth -> Redirect URLs
