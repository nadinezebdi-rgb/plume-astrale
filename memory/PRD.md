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

## Implemente — Feb 2026 (Endpoints manquants + Node engines)
- **Bug** : Numerologie, Karma & Destin et Theme natal cassés sur prod (endpoints 404)
- **Solutions implémentées** :
  - `services/numerology_service.py` : calculs purs (chemin de vie, expression, intime, realisation, annee perso, defis, cycles, nombre du jour)
  - `POST /api/numerology/complete` + `POST /api/numerology/deep-profile`
  - `POST /api/astrology/karma-destiny` : noeuds lunaires (calcul approximatif sans API externe)
  - `POST /api/astrology/natal-chart` : wrapper AstrologyAPI (`get_western_horoscope`)
  - `POST /api/discount/validate` + `POST /api/access/free` : codes de reduction sur tous les checkouts
- **Fix Node** :
  - `package.json` : `engines.node = ">=20.0.0 <23.0.0"`
  - `.nvmrc` : `20.18.0` pour forcer la même version sur Vercel/Netlify
- **Tests** : 100% des endpoints retournent `success: true` en local

## Implemente — Feb 2026 (Nudge "Compléter ton heure de naissance")
- `NatalCompletionPrompt.js` : nouveau composant compact qui s'affiche **uniquement** si user authentifié + a `birth_date` + manque `birth_time`
- CTA "Compléter" ouvre directement `NatalDataModal` (réutilisation du modal MonCompte)
- Intégré sur la home (`Index.js` sous le titre Énergie actuelle) + page Horoscope
- Auto-hide si user complet ou non-connecté
- Testid : `natal-completion-prompt`, `natal-completion-cta`

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

## Implemente — Feb 2026 (Integration astrology-api.io v3 sur theme & synastrie)
- **Service `services/astrology_io_service.py` refactore** :
  - Schema corrige : `birth_data` flat (year/month/day/hour/minute + latitude/longitude OU city/country_code) au lieu de la structure nested erronee
  - Helpers `make_birth_data()`, `make_subject()`, `parse_profile()` reutilisables
  - Nouveaux endpoints : `get_positions`, `get_house_cusps`, `get_aspects`, `get_lunar_metrics`, `natal_chart`, `synastry_chart`, `composite_chart`, `relationship_compatibility_score`, `relationship_compatibility`, `natal_report`, `synastry_report`
  - Fix cache 24h : colonne `energy_cache.day` (etait `.date` -> erreur silencieuse)
- **Nouveau routeur `routes/astrology_v3.py`** monte sous `/api/astrology/v3/*` :
  - `POST /natal` -> theme natal Swiss Ephemeris (positions + cuspides + aspects)
  - `POST /positions` -> positions planetaires precises
  - `POST /lunar` -> phase / signe lunaire / mansion
  - `POST /synastry` -> compatibilite entre 2 personnes pour 4 types de relations (love/friendship/family/work)
    - Renvoie : score 0-100, level francais (Flamme Jumelle, Ames Soeurs, etc), description contextuelle, aspects cles
    - Si person1 absent -> utilise profil de l'utilisateur connecte
- **Frontend `Compatibilite.js` totalement refait** :
  - 4 onglets (Amour / Amitie / Famille / Travail) avec icones Heart/Users/Home/Briefcase
  - Formulaire compact pour le partenaire (nom, date JJ/MM/AAAA, heure HH:MM, ville)
  - Auth gate si non connecte
  - Resultat avec score, level, description, aspects astrologiques cles
  - Tous data-testid : `compatibilite-page`, `relation-tab-{id}`, `partner-{field}`, `btn-analyze`, `result-card`, `result-score`, `result-level`, `aspect-{i}`
- **`Tarot.js` refait avec design editorial premium** :
  - 3 cartes (Passe / Present / Avenir) en grid
  - 22 arcanes du Tarot de Marseille avec signification + element + conseil
  - Carte verso elegante avec sparkles, hover scale, glow gold a la reveal
  - Gate "Premium requis" si non-Premium, avec CTA `/premium` ou `/inscription`
  - Tous data-testid : `tarot-page`, `tarot-card-{i}`, `tarot-actions`, `btn-reshuffle`, `tarot-premium-gate`
- **`server.py`** :
  - Inclus `astrology_v3_router`
  - `POST /api/astrology/natal-chart` : fallback v3 si AstrologyAPI legacy echoue
  - Endpoint `POST /api/astrology/horoscope-prediction` migrate vers signature corrigee de `horoscope_personal`

**Tests E2E valides (iteration 26)** : 25/25 backend tests PASS (test_iteration26_astrology_v3.py). Auth requise, validation Pydantic OK, cache 24h Supabase fixe. En preview la cle locale est invalide (502 graceful) ; sur Railway production la cle est valide -> 200 OK automatique.

### Backlog mis a jour (post iteration 26)
**P1** :
- Rapports PDF luxe pour theme natal et synastrie (premium)
- Affichage des cuspides et aspects natals sur la page MonCompte / Resultats
**P2** : Cartes virales Instagram/TikTok partage energie + Notifications Push web cycles emotionnels
**P3** : Journal & historique emotionnel graphique

## Hotfix Feb 2026 (Karma "Service inconnu" + Carte partageable synastrie)
- **Bug fix `karma_destin` & co.** : `config.SERVICE_COSTS` ne contenait pas `karma_destin`, `lecture_astrologique`, `lecture_tarot`, `cartographie_premium`, `synastrie`. L'endpoint `/api/credits/use` levait 400 "Service inconnu" -> page Karma cassee. Ajout des 5 entrees manquantes. Verifie : POST credits/use avec `karma_destin` deduit 10cr.
- **Carte partageable synastrie** (`POST /api/astrology/v3/synastry/share-card`) :
  - Public (pas d'auth) - renvoie un PNG 1080x1080 ratio Instagram square
  - Inputs : `name_1`, `name_2`, `score`, `level`, `relationship_type`
  - Design editorial : brand "PLUME ASTRALE", label compatibilite (AMOUR/AMITIE/FAMILLE/TRAVAIL), 2 prenoms + coeur or, score 160px, level, barre de progression, footer plume-astrale.fr
  - Helper `generate_synastry_card()` ajoute dans `services/share_card_generator.py`
- **Frontend `Compatibilite.js`** : 3 nouveaux boutons sur le resultat
  - `btn-download-card` : telecharge le PNG via fetch blob
  - `btn-share-native` : `navigator.share` avec File (image + texte), fallback clipboard
  - `btn-share-whatsapp` : ouvre wa.me avec texte pre-rempli (score + lien)
- Image testee : 49KB PNG 1080x1080 generee correctement avec PIL.

## Hotfix Feb 2026 (Karma "page vide" + PDF Natal + audit API v3)
- **Bug fix Karma & Destin "aucun contenu"** : le backend renvoyait uniquement `noeud_nord`/`noeud_sud`/`lecon_karmique` mais le frontend lisait `karma_principal`, `mission_de_vie`, `nombre_karmique`, `message_akashique`, `noeuds_lunaires` -> tous les blocs UI restaient invisibles apres deduction des credits.
- **Refonte `/api/astrology/karma-destiny`** :
  - Tentative 1 : `astrology-api.io v3 /data/positions` pour Node North + Soleil + Lune precis (Swiss Ephemeris)
  - Tentative 2 : AstrologyAPI legacy (en preview - cle valide)
  - Tentative 3 : approximation par ephemeride simplifiee (fallback ultime)
  - 12 profils karmiques riches (theme, description, lecon, don cache) pour chaque signe du Noeud Nord
  - 12 messages akashiques poetiques
  - Calcul du `nombre_karmique` (reduction des chiffres de la date avec preservation maitres 11/22/33)
  - Tous les champs du frontend remplis + retro-compatibilite des anciens champs
- **Bug fix URL** dans `KarmaDestin.js` : `fetch('/api/astrology/natal-chart')` (sans `${API_URL}` -> 404 sur Vercel) -> remplace par `${API_URL}/api/astrology/v3/positions` avec parsing direct des `points`/`positions` pour extraire Soleil/Lune/Ascendant/9 planetes
- **PDF Natal Premium** : nouveau endpoint `POST /api/astrology/v3/natal/pdf`
  - Wrapper sur `/api/v3/pdf/natal-report` de astrology-api.io (chart wheel SVG + interpretations psychologiques en francais)
  - Tradition "psychological" (depth jungien), theme `dark` cohérent avec la charte
  - Cover page + table of contents + 28 sections analytiques disponibles
  - `services/astrology_io_service.natal_report_pdf()` gere PDF binaire OU base64-in-JSON
- **Test prod karma**: `astrologyapi` source confirmee, returns Taureau/Scorpion axis avec full data structure pour date 1985-06-12.

## Implemente Feb 2026 (4 features P1 ROI eleve - API v3)
- **Solar Return Report (Revolution Solaire)** : nouvelle page `/revolution-solaire`
  - Backend `POST /api/astrology/v3/solar-return` wrappe `/charts/solar-return` + `/analysis/solar-return-report`
  - Calcul auto du return_year (prochain anniversaire)
  - UI affiche themes majeurs + life areas + summary, paywall 20 credits via `lecture_astrologique`
- **Transits du Jour** : composant `TransitsToday` embarque dans Horoscope
  - Backend `POST /api/astrology/v3/transits/today` wrappe `/charts/transit` + `/analysis/natal-transit-report`
  - Affiche 5 aspects principaux (planete transitante x planete natale + orbe) + interpretation
  - Refresh auto sur chaque visite page
- **Love Languages cosmiques** : nouvelle page `/love-languages`
  - Backend `POST /api/astrology/v3/love-languages` wrappe `/insights/relationship/love-languages`
  - Affiche langage principal + secondaires + conseils
  - CTA pour rebondir sur la compatibilite
- **Chat Astrologique v3 (Plume Chat upgrade)** : 
  - Backend `POST /api/astrology/v3/chat` wrappe `/chat/completions` avec `astrology.subjects` injectant le theme natal nativement
  - Frontend `ChatIA.js` essaie v3 EN PREMIER si user connecte avec birth_date, fallback transparent vers `/api/plume-chat` (legacy GPT)
  - Historique des 10 derniers messages envoyes a l'IA
  - Session id persiste cote backend (gere par astrology-api.io)
- **Service `astrology_io_service.py`** : 6 nouvelles methodes (`solar_return`, `solar_return_report`, `transits_today`, `transit_report_today`, `love_languages`, `astro_chat`)
- **Navbar** : ajout entries "Révolution Solaire" (dans Theme Astral) et "Langages d'Amour" (dans Tirages)
- 10 routes v3 au total : positions, lunar, natal, natal/pdf, synastry, synastry/share-card, solar-return, transits/today, love-languages, chat

**Tests prod (cle locale invalide donc 502 graceful pour les 4)** :
- POST `/v3/transits/today` -> 502 detail "Service astrologique indisponible." (auth OK)
- POST `/v3/love-languages` -> 502 (auth OK)
- POST `/v3/solar-return` -> 502 (auth OK)
- POST `/v3/chat` -> 502 "Service de chat astrologique indisponible." (auth OK)
- Smoke screenshots Revolution Solaire + Love Languages + Horoscope : pages rendent correctement.

## Implemente Feb 2026 (Tarifs unifies + Section "Mes Rapports" + Chat 3cr/q)
- **SERVICE_COSTS mis a jour** (`config.py`) :
  - chat_astral 2 -> 3 cr/question
  - karma_destin 10 -> 20 cr
  - synastrie 10 -> 20 cr
  - theme_natal_pdf : 20 cr (nouveau)
  - revolution_solaire : 20 cr (nouveau)
  - love_languages : 10 cr (nouveau)
- **Helpers wallet** (`wallet_service.py`) :
  - `is_premium_active(user_id)` : true si premium_status='active' ET premium_until > now
  - `charge_or_premium(user_id, service_id, amount, desc)` : skip si Premium, sinon deduct ; renvoie `{charged, amount, is_premium, new_balance}`
- **Paywalls v3 routes** :
  - Chat : charge AVANT + refund-on-fail (balance inchangee si 502)
  - PDF Natal : charge AVANT + refund-on-fail
  - Synastry : charge AVANT + refund-on-fail
  - Solar Return : charge APRES succes (pas de refund necessaire)
  - Love Languages : charge APRES succes
- **Section "Mes Rapports"** dans `/mon-compte` :
  - Nouvel onglet entre "Apercu" et "Abonnement"
  - 6 cartes : Karma 20cr · Compatibilite 20cr · Revolution Solaire 20cr · Langages d'Amour 10cr · Theme Natal PDF 20cr · Chat Plume 3cr/question
  - Affiche "Offert" pour Premium, prix sinon
  - CTA Premium en bas (7 jours gratuits)
  - data-testid : `rapports-tab`, `rapport-card-{slug}`, `rapports-premium-cta`
- **Chat v3 cote frontend** (`ChatIA.js`) :
  - Gere erreur 402 -> redirige vers /acheter-credits
  - Fallback transparent vers /api/plume-chat si v3 indisponible

**Tests valides (iteration 27)** : 14/14 backend PASS. Verified live balance deltas via admin token : karma_destin -20cr, chat_astral -3cr, chat-v3 refund flow OK (balance inchangee apres 502).

## Phase 1 cahier des charges implementee (Feb 2026)
- **Nouvelle Navbar** :
  - Mega-menu "Décoder ma période" (4 colonnes: Au quotidien · Mon thème · Relations · Explorations) consolidant les 16 outils
  - Accordéon mobile (une section ouverte a la fois)
  - CTA Premium STICKY DORÉ ("✦ L'Expérience Premium") seul élément plein, visible sur toutes les pages
  - Items navbar : Accueil · Décoder ma période ▾ · Le Cercle · Notre cadre · [Premium] · Connexion · Inscription
  - Synastrie 49€ mise en évidence (✦ doré) dans la colonne "Relations"
- **HeroOracle.js** (4 états du tunnel d'acquisition) :
  - idle : prénom + date | CTA "✦ Révéler mon énergie" + micro-réassurance "Gratuit · sans carte"
  - computing : loading 1.5s mis en scène ("la Plume écoute ton ciel...")
  - teaser : wheel + chemin de vie + phase lunaire + tarot oui/non ; interpretation floutée + capture email
  - email_captured : invitation à affiner avec heure/lieu + pont Premium
- **Endpoints publics Oracle** (`routes/oracle.py`) :
  - `POST /api/oracle/teaser` : calcul chemin de vie + phase lunaire algo Conway + tarot oui/non déterministe sha256
  - `POST /api/oracle/capture-email` : upsert dans table `oracle_leads` (graceful si table absente)
  - Migration SQL Supabase : `/app/supabase/oracle_leads_migration.sql`
- **PremiumStickyCTA.js** : barre fixe basse mobile (>=56px tactile, masquée sur pages commerciales/admin/auth/Premium-déjà-actif)
- **Pages nouvelles** :
  - `/notre-cadre` (NotreCadre.js) : charte symbolique anti-prédiction (cadre réglementaire UE), 4 sections (miroir · ce qu'on ne fera jamais · ce qu'on croit · vos données)
  - `/cercle` (CercleSales.js) : page de vente abonnement avec 6 cards de valeur + 5 FAQ + CTA principal
  - `/cercle-quotidien` : redirige vers l'ancien dashboard Cercle (sera refondu Phase 2)
  - `/synastrie` : routé vers Compatibilite2 (Phase 3 retravaillera cette page)
- **Build Vercel CI strict** : ✅ Compiled successfully (apostrophes JSX escapés, composants nested déplacés au module-scope)
- **Tests** : 16/16 backend tests PASS (iteration 28), endpoints publics validés, validation Pydantic OK, capture-email gracieux si table absente
- **Bug fix bonus** : `/api/health` ajouté (route directe sur `app` car `api_router` était freezed), tarot deterministe via sha256 (au lieu de hash() instable)

### Prochaines etapes (Phase 2 — Le Cercle dashboard quotidien)
- Refondre `/cercle-quotidien` selon spec `<DailyRitual />` : salutation, contexte lunaire, streak doux, Conseil de la Plume, check-in 1 tap, jauges 4 énergies, accès Réflexion du soir
- Système streak doux + jour de grâce (DB Supabase, conditionné webhook Stripe)
- Réflexion du soir déverrouillée ~19h avec journal privé
- Cache journalier Supabase pour quota API

## Resend integre (Feb 2026) — Sequence 6 emails Plume Astrale
- **Service `services/resend_service.py`** (basé sur playbook Emergent) :
  - 6 templates editoriaux (E1 a E6) en HTML+plain text
  - Layout cohérent avec la marque (cards dorees, fond sombre, typo serif)
  - Helper `_wrap()`, `_btn()`, `_h2()`, `_p()` réutilisables
  - Fonction `send_e1_teaser_now()` : envoi immediat E1 a la capture email
  - Fonction `process_sequence_step()` : envoi differe selon le planning (J+1, J+3, J+7, J+10, J+14)
  - Tracking dans `oracle_leads.email_sequence_step` + `last_email_sent_at` (idempotent)
- **Endpoints `routes/oracle.py`** :
  - `POST /api/oracle/capture-email` : upsert + recalcul teaser + envoi E1 (best-effort)
  - `POST /api/oracle/run-sequence` : a appeler depuis un cron externe (Railway cron / GitHub Actions) toutes les 6h
  - `GET /api/oracle/unsubscribe?email=X` : desabonnement 1-clic (lien dans chaque email)
- **Frontend `Desabonnement.js`** : page elegante "C&apos;est fait." avec retour accueil
- **Env vars** (`backend/.env`) :
  - `RESEND_API_KEY=re_124cm1X3...` (a configurer aussi sur Railway prod)
  - `SENDER_EMAIL="Plume Astrale <onboarding@resend.dev>"` (TEMPORAIRE en mode test - cf. note)
- **Test envoi reel** : ✅ Email E1 livre a `nadine.zebdi@gmail.com` (id Resend `c666abf5-3814-...`)
- **ACTION USER REQUISE pour passer en production** :
  1. Aller sur https://resend.com/domains et ajouter `plume-astrale.fr`
  2. Configurer les enregistrements DNS donnés par Resend (chez le registrar)
  3. Une fois vérifié, changer `SENDER_EMAIL` sur Railway : `Plume Astrale <hello@plume-astrale.fr>`
  4. Exécuter `/app/supabase/oracle_leads_migration.sql` dans Supabase SQL Editor (sinon le tracking step ne fonctionne pas)
  5. Configurer un cron externe : `POST https://api.plume-astrale.fr/api/oracle/run-sequence` toutes les 6h


## Iteration 29 — Bugs P0 production resolus (Feb 2026)

### Bug 1 : Redirection post-login erronee → CORRIGE
- **Symptome** : apres connexion, l'utilisateur etait redirige sur `/tarot` (page legacy) au lieu de son espace personnel
- **Root cause** : `Login.js:35` faisait `navigate('/tarot')` en dur (residu du tunnel oracle initial)
- **Fix** : `navigate(redirect || '/mon-compte')` avec lecture du param `?redirect=...` depuis l'URL (utile pour les guards de routes protegees)
- **Fichier** : `frontend/src/pages/Login.js` lignes 30-38
- **Tests** : E2E playwright OK avec admin, redirection respecte `?redirect=/cercle`

### Bug 2 : Portail Stripe 404 pour les premium grants manuels → CORRIGE
- **Symptome** : le bouton "Gerer mon abonnement" sur `/premium` retournait 404 pour les utilisateurs ayant un premium offert manuellement par l'admin (sans `stripe_customer_id`)
- **Root cause** : `Premium.js` affichait le bouton manage des que `isPremium === true`, mais le endpoint `/api/premium/portal` retourne legitimement 404 si l'utilisateur n'a pas de `stripe_customer_id` dans son profil
- **Fix** :
  1. Nouveau flag `hasStripeSubscription = !!status?.subscription_id` derive de la reponse de `/api/premium/status`
  2. Le bouton manage n'est rendu QUE si `hasStripeSubscription === true`
  3. Sinon affichage d'un texte editorial : "Acces offert — aucun abonnement Stripe a gerer."
  4. `handleManage` gere maintenant le 404 avec un message clair (defense en profondeur)
- **Fichier** : `frontend/src/pages/Premium.js` lignes 129-150 + 192-208
- **Bonus** : correction d'une route brisee (`/mon-profil` → `/mon-compte`) sur le CTA du plan gratuit
- **Tests** : iteration 29 → 6/6 backend PASS + 5/6 frontend PASS (juliette UI path bloque par mot de passe manquant mais validation code-review OK)

### Action user encore requise
- **CRITIQUE** : executer `/app/supabase/oracle_leads_migration.sql` dans le SQL Editor Supabase. Sans ca, la capture email Oracle continue de logger `PGRST205 - oracle_leads not found` (les leads ne sont PAS persistes, donc la sequence Resend ne fonctionne pas). Le endpoint retourne neanmoins 200 (graceful fallback), masquant le probleme.
- **Production** : faire "Save to Github" pour redeployer les fix Login.js + Premium.js sur consultation-astro.emergent.host / plume-astrale.fr

### Code review surface points (non bloquants)
- `Premium.js:147` : `isPremium` melange `status` et `user` (2 sources) → preferer trust uniquement `status` une fois charge
- `Premium.js:109` : silent .catch() sur le status fetch → ajouter logging/sentry
- `Login.js:35` : redirect param sans allowlist → faible risque (react-router neutralise les URLs absolues) mais a securiser long terme
- `premium_subscription.py:111` : portail Stripe ouvert tant que `stripe_customer_id` existe meme apres expiration → considerer aussi `status in ('active','trialing')`
