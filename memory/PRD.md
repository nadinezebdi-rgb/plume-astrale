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

## Implemente — Feb 2026 (Premium 14,99€ + 7j Trial + Social Proof)

### Premium Subscription Mensuel
- `services/premium_subscription.py` : Stripe Subscription mode=subscription, 14,99€/mois EUR, locale=fr
- `trial_period_days: 7` -> essai gratuit 7 jours, annulable a tout moment
- Auto-creation Stripe Customer + persistance `stripe_customer_id` dans `profiles`
- Endpoints : `POST /api/premium/checkout`, `GET /api/premium/status`, `POST /api/premium/portal`
- Webhook handlers : `checkout.session.completed` + `customer.subscription.*` -> sync `profiles.premium_status` et table `subscriptions`
- Frontend : pages `Premium.js`, `PremiumLanding.js`, `PremiumExperience.js`

### Social Proof component
- `GET /api/stats/social-proof` -> `{consultations_7d, visible, label}`
- Seuil minimum 100 (auto-hide en dessous)
- `frontend/src/components/SocialProof.js` integre sur landing

### Tests E2E valides (Feb 2026 — iteration_24)
- 9/9 endpoints backend OK : premium/checkout (trial 7j active, amount_total=0), premium/status, premium/portal, stats/social-proof (threshold 100), auth/me (is_premium/is_admin), energy/today (AstrologyAPI+LLM), credits/checkout (non-regression), wallet/balance
- Stripe live key sk_live_... 100% fonctionnelle, aucune AuthenticationError
- Tests pytest : `/app/backend/tests/test_iteration24_premium_trial.py`

### Backlog mis a jour
**P1** : Module Compatibilite Relationnelle avance (amour/amitie/famille via AstrologyAPI) + PDF Premium luxe (themes natals & compatibilite)
**P2** : Cartes virales Instagram/TikTok partage energie + Notifications Push web cycles emotionnels
**P3** : Journal & historique emotionnel graphique + features sociales legeres

### Refactoring suggere (non bloquant)
- server.py 690 lignes -> extraire premium/credits routes dans routes/
- _PRICE_ID_CACHE module-level non thread-safe (OK single-worker uvicorn)
- social-proof : ajouter health flag pour distinguer "<100" vs "Supabase down"

## Implemente — Feb 2026 (Fix Navbar + Mobile responsiveness)
- **Navbar** : fix chevauchement logo "Plume Astrale" / "Accueil"
  - Breakpoint desktop releve de 1024px a 1240px (sous lequel hamburger)
  - Gap reduit a 14px + marginLeft 24px entre logo et items
  - Font items 13->12px, letterSpacing 0.08->0.07em
  - Boutons Connexion/Creer un compte compactes (padding 6/10-12, font 11px)
- **Hero Index.js** : kicker "Sanctuaire Numerique" ne chevauche plus le titre sur mobile (pt-32 sm:pt-24, top-20 sm:top-24)
- **Mobile audit (390px) — 7 pages testees sans overflow horizontal** : /, /premium, /energie, /horoscope, /acheter-credits, /formulaire, /consultation, /tarot-oui-non — toutes scrollW = clientW = 390

## Implemente — Feb 2026 (Audit UX : fin du re-onboarding)
**Problème** : 14 pages legacy (Horoscope, Tarot, Compatibilite, etc.) lisaient uniquement `localStorage.plume_astrale_data` -> redirection forcée vers `/formulaire` à chaque nouveau navigateur ; données fantômes (ex: "Saida") faussaient les résultats malgré un user connecté avec son propre profil natal.

**Fix** :
- `AuthContext` :
  - `hydrateNatalLocalStorage(user)` synchronise `localStorage.plume_astrale_data` avec le profil Supabase à chaque `loadMe()`. Si user a `birth_date`, écrase avec ses données. Sinon, vide le localStorage (élimine les données rogue).
  - `clearNatalLocalStorage()` appelé au logout
  - `updateProfile(fields)` : PUT `/api/auth/profile` + re-loadMe pour resync auto
- `Formulaire.js` : redirige vers `/mon-compte` si `isAuthenticated && user.birth_date` (replace), plus aucun re-onboarding pour user connecté
- `MonCompte.js` :
  - Bouton "Modifier" (testid `edit-natal-btn`) sur la carte "Informations personnelles"
  - Race condition fix : redirect `/connexion` uniquement si `!authLoading && !token`
  - `chargerProfil` migré de `/api/account/profile` (404) vers `/api/auth/me` + `/api/ritual/today` + `/api/premium/status`
- `NatalDataModal.js` : nouveau composant avec tous les data-testid (prenom, gender, birth-date/time/place/country, save, close)
- Backend `/api/auth/me` : normalise `birth_time` `HH:MM:SS` -> `HH:MM`

**Tests E2E (iteration 25)** :
- Login admin avec localStorage "Saida" rogue -> automatiquement écrasé par Paris/1990
- Hard reload `/mon-compte` -> reste sur la page
- Visiter `/formulaire` connecté -> redirige vers `/mon-compte`
- Modal modification ouvre + pré-remplit + persiste via PUT /api/auth/profile
- Backend 6/6 endpoints OK

## Implemente — Feb 2026 (Bannière trial 7j + Lune rotative)
- **TrialBanner** (`/app/frontend/src/components/TrialBanner.js`) :
  - **Globale** dans `App.js` après `<Navbar />` (toutes les pages avec navbar)
  - Cachée automatiquement sur : `/premium*`, `/paiement*`, `/credits/succes`, `/commande/succes`, `/inscription`, `/connexion` (HIDE_ON_PATHS)
  - `position: fixed; top: 64px` (sous navbar, ne pousse pas le contenu)
  - "🎁 7 JOURS d'essai gratuit Premium — annulable a tout moment"
  - CTA "EN PROFITER" -> `/premium`, croix de fermeture (localStorage, 24h)
  - Si user connecté, calcule remaining days basé sur `user.created_at`
  - Auto-hide si Premium actif
  - Responsive : version courte mobile (<640px), longue desktop
- **Lune rotative** (`/app/frontend/src/index.css` + `Index.js`) :
  - Nouvelle animation `animate-spin-moon` 50s linear infinite
  - Cratères dans un wrapper rotatif → l'éclairage solaire reste fixe (réaliste)
  - 6 cratères au lieu de 4 pour plus de détail visuel
  - Anneau zodiacal continue à tourner indépendamment (80s)
