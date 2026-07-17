# CHANGELOG - Plume Astrale

## 2026-02-09

### Session 6 — SafeEmptyState : fallback anti-page-blanche
- **Nouveau composant** `/app/frontend/src/components/design/SafeEmptyState.js` : filet de sécurité UI qui s'affiche si l'API répond 200 mais qu'aucun contenu attendu n'est présent (schéma cassé, drift API, contenu vide). Affiche un message poétique "Le ciel est momentanément silencieux" + CTA "Parler à Solena" (bouton or) + lien mail support + bouton "Réessayer" si `onRetry` fourni. Design Nuit Douce cohérent.
- **Intégré sur 4 pages produit** :
  - `RevolutionSolaire.js` — détection via `interpretations.length || lifeAreas.length || srAspects.length || overview`
  - `Archetype.js` — détection via `profile_name || core_message || dominant.length || shadow || balance_type`
  - `Compatibilite.js` — détection via `score !== undefined || name_1 || report || dominant_element`
  - `KarmaDestin.js` — détection via `data.karma_principal || data.mission_de_vie || data.noeuds_lunaires`
- **Résultat** : plus JAMAIS de page blanche visible pour l'utilisatrice, même si le fournisseur d'API change son schéma. La conversion émotionnelle est sauvegardée via la redirection vers Solena.
- Corrections lint annexes : 2 apostrophes non échappées dans `Archetype.js` (pré-existantes).
- **Note** : `Horoscope.js` a déjà un fallback interne `fallbackHoroscopes`, pas besoin d'ajouter SafeEmptyState.

### Session 5 — Audit produits + Fix Révolution Solaire
- **Testing agent iteration_46** : Backend 100% OK en preview (15/15 endpoints, `/api/astrology/v3/solar-return` en 2.4s, très en-dessous du timeout Cloudflare 100s). Cloudflare 520 en prod NON-reproductible en preview — probablement env var ou rate-limit prod.
- **🚨 Bug critique frontend détecté** : `RevolutionSolaire.js` lisait `report.overview/summary/themes/major_themes` qui n'existent PAS dans la réponse API v3. Le vrai schéma est `report.interpretations` (list de {title,text}), `report.life_areas` (LIST de {area_key, theme, prediction}), `report.sr_to_natal_aspects`. Résultat: API répondait 200 mais la page restait vide (l'utilisatrice pensait que le produit était cassé).
- **Fix appliqué** : refactor complet des sections rendues dans `RevolutionSolaire.js` (interpretations en cascade + life_areas grid 2 colonnes + sr_to_natal_aspects). `TransitsToday` fixé aussi (lecture de `report.events` array au lieu de `report.summary/text`).
- **Vérification E2E** : login admin + click "Générer" → API répond en 2.4s → **rapport complet affiché** avec 5 interprétations planétaires + 8 domaines de vie.
- ⚠️ **Note produit** : l'API v3 renvoie le contenu en **anglais** malgré `language: fr`. Amélioration future = post-processing OpenAI (traduction FR).
- ⚠️ Warning hydration `<span> in <option>` sur `/rencontres-astrales` — non-bloquant, pré-existant.

### Session 4 — Audit Supabase + Codes Promo/Réduction

**Audit schéma DB**
- ✅ Toutes les colonnes attendues par le code sont couvertes par les migrations existantes (profiles, wallets, credit_transactions, payment_transactions, promo_codes, promo_code_redemptions, subscriptions, energy_cache, oracle_leads, cercle_*, synastrie_purchases, plume_chat_messages, journal_entries, streaks, is_admin).
- 🚨 **Table manquante détectée** : `archetype_readings` (utilisée par `/api/archetype/*`). Migration créée : `/app/supabase/archetype_readings_migration.sql`.

**Système de codes de réduction (déjà partiellement en place)**
- ✅ `POST /api/discount/validate` — validation publique (retourne 100% pour tout code valide)
- ✅ `POST /api/access/free` — grant free access (crédits + premium via `redeem_promo`)
- ✅ Support natif sur : `/paiement`, `/livre`, `/apercu`, `/premium`, `/compatibilite`, `/compatibilite2`
- 🆕 **Ajout support sur `/kabbale` et `/rencontres-astrales`** :
  - Backend : nouveau helper `services/promo_bypass.py::try_consume_promo()` — valide + incrémente `used_count`.
  - `kabbale.py::checkout` et `rencontres.py::checkout` acceptent désormais un champ `promo_code`. Si valide, saute Stripe entièrement, crée une tx `completed`, et déclenche directement `handle_*_webhook()` (PDF + email).
  - Frontend : input `Code promo (optionnel)` ajouté sur `KabbaleSales.js` et `RencontresAstrales.js`.

**Codes créés dans la migration `/app/supabase/discount_codes_migration.sql`**
- `ADMIN26` — 999999 crédits + 3650 jours Premium, `max_uses=1` (pour toi uniquement)
- `BIENVENUE10` / `LUNE20` / `SOLENA30` — codes crédits pour clientes
- `DECOUVERTE7` / `CADEAU30` / `FIDELITE90` — codes Premium 7j / 30j / 90j
- `KABBALE100` / `RENCONTRES100` / `ARCHETYPE100` — bonus produits high-ticket

### Session 3 — Refonte Homepage P1 complète ("app-native" vision)
- **Portrait Solena unique** : remplacement de toutes les vidéos par le portrait mystique CDN (`n7vv5dtw_IMG01_portrait_femme_mystique_corrigee_2.png`). Homepage, `/solena`, `/rencontres-astrales`. Aucune balise `<video>` restante sur ces pages.
- **`solena.js`** : suppression des URLs vidéos actives, `portrait` pointe vers le CDN Emergent.
- **JabInteractif** (`/app/frontend/src/components/design/JabInteractif.js`) : 3 cartes cliquables `[1] [2] [3]` (La Lune / L'Étoile / Le Soleil), reveal glassmorphism avec message + keyword, CTA doré "Continuer avec Solena" post-révélation. Portrait Solena en glass à gauche.
- **FloatingReviews** (`/app/frontend/src/components/design/FloatingReviews.js`) : 6 bulles de conversation SMS-style (Camille/Léa/Sarah/Manon/Julie/Emma), avatars gradient (initiale + hue signe), rotation subtile ±1.4°, alignement gauche/droite alternées, staggered fade-in-up 80ms cascade.
- **Motion.js** (`/app/frontend/src/components/design/Motion.js`) : composants `SectionTransition` (radial gradient or 0→8%→3% brumeux entre sections), `FadeInUp` (framer-motion whileInView), `StaggerGroup` (cascade 60ms).
- **Index.js** : structure Home avec SectionTransition intercalés entre chaque section, FadeInUp sur BrandStory/ServicesShowcase/JabInteractif. Suppression du code mort (`ClientReviews`, `ReviewCard`, `StarRow`, `REVIEWS`, imports Play/Quote/Star/Heart).
- **Testing agent iteration_45** : 100% (18/18) frontend, aucun bug détecté, aucun retest requis.

### Session 2 — Harmonisation Visuelle Absolue (P0)
- **Fix cassure Lune ↔ Page** : Hero3D background passé de `radial(#1a1147→#0C0918→#050308)` (violet/noir agressif) à `radial(#1A2035→#141A2C→#111625)` — parfaite continuité avec le reste de l'app.
- **Emissif Lune** : `0x2a1e4a` (violet indigo) → `0x1A2035` (Nuit Douce). Intensité réduite 0.08 → 0.06.
- **Shader aura** : palette violet/indigo remplacée par gold + midnight blue. L'aura se fond désormais dans le fond de la page.
- **TestimonialsMarquee** (`/app/frontend/src/components/design/TestimonialsMarquee.js`) : bandeau de preuve sociale animé sous le Hero, 5 bulles glass (Léa/Camille/Marion/Sophie/Alice), verbatims 5⭐, effet Cormorant italic + Cinzel uppercase, pauseOnHover.
- **Index.js** : `<TestimonialsMarquee />` intercalé entre `<Hero3D />` et `<ServicesShowcase />`. Body background `#111625` explicite pour éviter tout flash.

### Session 1 — Fix Three.js Deprecation
- Remplacement de `THREE.Clock` par `performance.now()` dans `Moon3D.js`. Warning console éliminé.

## 2026-07-17 — Fix panne chat astral production (503/CORS) + fuite console.log
- CAUSE RACINE : clé `ASTROLOGY_API_IO_KEY` expirée/révoquée (401 sur tous les endpoints astrology-api.io). Nouvelle clé fournie par l'utilisateur, testée et configurée dans backend/.env. ⚠️ À METTRE À JOUR AUSSI SUR RAILWAY.
- CORS : déjà correct dans le code (commit 3ad043a du 27 mai). Le "préflight 405" observé par l'utilisateur = test OPTIONS sans en-têtes Origin/Access-Control-Request-Method (faux négatif). Si prod KO → Railway sur un commit trop ancien, redéployer.
- Durcissement route /api/astrology/v3/chat (routes/astrology_v3.py) : try/except global → toute erreur renvoie un 502 propre AVEC en-têtes CORS + remboursement 10 crédits ; cache in-memory 24h du contexte natal (_natal_ctx_cache) ; timeout chat 30s → 60s (astrology_io_service.py `_call(timeout=)`).
- Privacy : suppression des console.log("LOGIN ATTEMPT", email) et console.log("LOGIN SUCCESS") dans frontend/src/pages/Login.js.
- Tests : chat e2e OK (1er msg 5.8s natal frais, 2e msg 3.8s natal caché, crédits débités, réponses FR).

## 2026-07-17 — 4 features : Pack Karmique 89€, Compat Ultime synastrie, Alerte 401, Refonte couleurs + étoiles
- **Pack Karmique + Kabbale 89€** (one-shot) : routes/pack_karmique.py (checkout+status, bypass promo), services/pack_karmique_service.py (webhook : karmic + tree-of-life parallèle + 3 synthèses GPT-4o-mini + email Resend), services/pack_karmique_pdf.py (PDF 44 pages, réutilise kabbale_pdf). Frontend : PackKarmique.js (/pack-karmique) + PackKarmiqueSucces.js (polling). Dispatch webhook kind='pack_karmique_kabbale' dans server.py. Pack ajouté à config.PACKS.
- **Compat Ultime 29,99€ enrichie** : données partenaire OBLIGATOIRES au checkout (partner_first_name/partner_birth_date, 400 sinon). build_synastry_chapter() dans rencontres_ultime_service.py : /analysis/synastry-report + 13 appels GPT parallèles pour franciser les 12 domaines de vie + dynamics → nouveau chapitre PDF (_p_synastry_intro + _p_synastry_areas, PDF passe de 15 à 20 pages). Champs partenaire dans RencontresAstrales.js (data-testid partner-*).
- **Alerte clé API** : _alert_invalid_key() dans astrology_io_service.py — email Resend à ADMIN_ALERT_EMAIL (=contact@plume-astrale.fr dans .env) dès qu'un 401 est reçu, throttle 6h. Testé (livré à nadine.zebdi@gmail.com, seule adresse autorisée par la clé Resend test du preview ; en prod le domaine est vérifié).
- **Refonte couleurs + étoiles (Patch #5)** : sed global frontend — #B8961F→#D4AF37, #0C0918→#111625, #F4E8D2/#F0E6D3→#F5EEE0, #C5A059→#D4AF37, #1a1147→#1A2035, rgba(184,150,31)→rgba(212,175,55), classes purple-*→lavande #B8A9E8/#E3D7FF (TirageTarot, TirageDuJour). Nouveau composant global Starfield.js (90 étoiles dorées scintillantes, .plume-starfield z-index 1) monté dans App.js.
- Tests : iteration_47.json — 100% PASS (9/9 backend + tous flux frontend). Code promo de test en preview : TESTPLUME (ADMIN26 absent de la DB preview).
- À FAIRE côté user pour la prod : redéployer Railway + Vercel, ajouter ADMIN_ALERT_EMAIL=contact@plume-astrale.fr sur Railway, vérifier que le code ADMIN26 existe dans la table promo_codes de la DB prod si besoin.

## 2026-07-17 (suite) — Nouveaux packs de crédits "Cosmiques"
- Remplacement des 3 anciens packs (Initiation 15/4,99 · Clarté 60/14,99 · Flammes Jumelles 130/29,99) par 4 packs sans bonus ni émojis : Comète 30cr/7,99€ · Nébuleuse 80cr/17,99€ (Le plus choisi) · Constellation 180cr/34,99€ (Meilleure valeur) · Voie Lactée 350cr/59,99€.
- Fichiers : backend/config.py (PACKS, ids: comete/nebuleuse/constellation/voie_lactee), BuyCredits.js (grille passée en xl:grid-cols-4, mention "crédits offerts" retirée), CreditsPaywallModal.js (grid 2 col), ServicesEquivalence.js + Navbar.js ("DÈS 14,99€" → "DÈS 17,99€").
- Testé : GET /api/packs OK, POST /api/credits/checkout pack_id=nebuleuse → URL Stripe OK, rendu visuel 4 cartes vérifié.
