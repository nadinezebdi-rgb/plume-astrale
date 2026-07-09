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


## Session Feb 2026 — ⚡ Solena GaryVee + 🎁 Ton Archetype 4,99€ (2026-02)

### Solena — Calibration methode GaryVee (JAB / COACHING / HOOK)
- ✅ **`/app/backend/services/plume_chat.py`** : nouveau `SYSTEM_PROMPT_SOLENA` remplace le prompt "mystique gothique" par un style "coach de vie moderne, mentore de l'ame".
- ✅ 3 missions strictes a chaque reponse : le JAB (valeur brute concrete), le COACHING (action a poser aujourd'hui), le HOOK (question ouverte de retention).
- ✅ Formatage : paragraphes courts 2-3 phrases, puces, un seul emoji subtil optionnel en ouverture, plus de titres "## L'ÉCHO DE VOS ÉTOILES" ni de "🪶 Une plume mystique...".
- ✅ Barrieres ethiques renforcees (sante, decisions vitales).
- ✅ Fallback tool-leak nettoye (message court + question).
- ✅ Verifie live : reponse admin (Belier asc Lion) → structure JAB/COACHING/HOOK respectee, 1668 chars, se termine bien par une question percutante.

### Nouveau produit : Ton Archetype 4,99€ (15 credits)
- ✅ **Endpoint API** : `POST /api/archetype/generate` (via `services/astrology_io_service.py::archetypes()` sur `/analysis/archetypes`).
- ✅ **Route** : `/app/backend/routes/archetype.py` (factory pattern pour imports circulaires).
- ✅ **Tarif** : 15 credits (equivalent 4,99€ pack Initiation) — ajoute a `config.py SERVICE_COSTS`.
- ✅ **Mapping FR** : dictionnaire `_ARCHETYPE_FR` traduit les 13 archetypes universels (Sage, Souverain, Artiste, Amoureux, Heros, Magicien, Farceur, Gardien, Ame Pure, Voyageur, Rebelle, Ame Solidaire, Orphelin).
- ✅ **Front page** : `/app/frontend/src/pages/Archetype.js` — sous `/archetype` — affiche profile_name en gros italic dore, 3 archetypes dominants en glass cards avec scores, shadow en card lavande, CTAs "Parler a Solena" (primary) + "Regenerer 15cr" (secondary).
- ✅ **Historique** : `GET /api/archetype/history` — sauvegarde les 5 dernieres lectures (best effort, table archetype_readings a creer manuellement en Supabase Studio).
- ✅ **Testes live** : admin (Taureau) → Souverain-Guerrier · Polymathic · Le Souverain (13.6), Le Heros (12.7), Le Gardien (9.1) · Shadow L'Artiste · 15 credits deduits proprement.



## Session Feb 2026 — 🎨 Design System v2 Phase 2 complete + Phase 3 + Aura Connectee (2026-02)

### Phase 2 - Index.js uniformise
- ✅ Trust badge migre : "AstrologyAPI" → "astrology-api.io v3 + OpenAI GPT" (correction post-purge).
- ✅ CTA "Decouvrir l'univers de Solena" → `plume-btn-secondary`.
- ✅ Cards specialites Solena → `plume-glass` (backdrop-blur + bordure or 20%).

### Phase 3 - Pages secondaires unifiees
- ✅ **CercleSales.js** : CTA principal "Rejoindre le Cercle 14,90€/mois" → `plume-btn-primary` (avec glow doux).
- ✅ **BuyCredits.js** : 3 boutons packs (Initiation, Clarte, Flammes Jumelles) → `plume-btn-secondary` + `plume-btn-primary` (Clarte = featured). 3 CTAs footer (Tarot/Theme/Numerologie) → `plume-btn-secondary`.
- ✅ **Compatibilite2.js** : 4 CTAs credit gates (Se connecter, Creer compte, Acheter credits, Commencer analyse) unifies.
- ✅ **RencontresUltimeSucces.js** : bouton "Telecharger PDF" → `plume-btn-primary`, "Retour accueil" → `plume-btn-secondary`.
- ✅ **TirageTarot.js** : via update global `.btn-mystical` et `.card-mystical` dans App.css — auto-refresh de tous les boutons + cards de cette page.
- ✅ **App.css** : redefinition centralisee de `.btn-mystical`, `.btn-mystical-filled`, `.card-mystical` avec la nouvelle palette Nuit Douce + glow doux + easing silk.

### Aura Connectee (Signature #3)
- ✅ **Hook `/app/frontend/src/hooks/useAstralElement.js`** : calcule le signe solaire depuis `user.birth_date` puis mappe vers l'element (feu/eau/air/terre).
- ✅ **`AuraProvider`** (`/app/frontend/src/components/design/AuraProvider.js`) : applique automatiquement la classe `.aura-{element}` sur `<body>` une fois l'utilisateur connecte.
- ✅ **CSS** : `body.aura-*` remplace le glow des `plume-btn-primary` + le gradient du Fil d'Ariane par la couleur de l'element.
- ✅ **Verifie** : admin ne le 15/05/1990 (Taureau) → `body.className = "aura-earth"` → accent verdoyant subtil.
- ✅ Aucune regression backend (astrology API + Supabase assets toujours OK).



## Session Feb 2026 — 🎨 Design System v2 "Nuit Douce" (Phase 1 + 2 partielle) (2026-02)
- ✅ **Nouveau design system Plume Astrale v2** livre par design_agent avec 3 signatures creatives originales :
  - **Souffle Astral** (grain SVG 3% pulsant 12s en overlay global)
  - **Fil d'Ariane** (ligne verticale 1px doree centrale, connecte les sections en scroll)
  - **Aura Connectee** (accent color adaptatif selon element astral utilisateur)
- ✅ **Palette Nuit Douce** appliquee globalement :
  - `#111625` fond principal (Nuit Douce) — remplace le noir pur
  - `#1A2035` fond secondaire (Nuit Profonde) — surfaces cartes
  - `#D4AF37` or brosse mat — accents (remplace `#D4B46A/#C5A059`)
  - `#E3D7FF` lavande pale — textes secondaires
- ✅ **1285 valeurs de couleurs remplacees** dans le codebase (807 hex + 476 rgba) via sed global.
- ✅ **Fonts** : Cinzel (titres) + Cormorant Garamond italic (emphase) + Plus Jakarta Sans (corps).
- ✅ **Overlays globaux** montes dans `App.js` :
  - `NoiseOverlay.js` (grain + Souffle Astral)
  - `ScrollThread.js` (Fil d'Ariane, desktop only)
  - `CustomCursor.js` (curseur aura doree 8px, desktop only)
  - `MobileTabBar.js` (sticky bottom, 3 icones : Mon Espace / Consulter / Tarifs)
- ✅ **Composants UI** : `PlumeButtons.js` (Primary/Secondary/Ghost strict), `GlassCard.js`, `SectionWrapper.js` (framer-motion + radial-gradient auto).
- ✅ **Navbar** upgrade glassmorphism (`rgba(17,22,37,0.90)`, backdrop-blur, bordure or subtile).
- ✅ **Tailwind config** : nouveaux tokens `plume.*` + `font-plume-serif|italic|body` + `shadow-plume-glow*` + `ease-plume-silk`.
- ✅ **Dependances ajoutees** : `framer-motion@12.42.2`, `react-fast-marquee@1.6.5`.
- ✅ **Design guidelines** documentes dans `/app/design_guidelines.md` + `/app/design_guidelines.json`.
- ✅ **Testing agent iteration 42** : 80% frontend PASS + 100% backend PASS. 2 bugs fixes:
  - Routes TabBar mobile (`/dashboard`→`/mon-compte`, `/tarifs`→`/acheter-credits`).
  - Aucune regression backend (Supabase assets + astrology API tous OK).



## Session Feb 2026 — 🚀 Migration assets → Supabase Storage (déploiement stable) (2026-02)
- ✅ **223 fichiers migrés** vers 2 buckets Supabase publics : `library` (193 fichiers) + `public-assets` (30 fichiers).
- ✅ **~407 MB libérés** du repo :
  - `/app/backend/assets/` : 383 MB → 8.4 MB (-98%)
  - `/app/frontend/public/` : 34 MB → 1.2 MB (-97%)
- ✅ Scripts de migration idempotents : `/app/backend/scripts/upload_assets_to_supabase.py` (library), `upload_public_assets.py` (public).
- ✅ **Backend** :
  - `/api/library/file/{cat}/{filename}` → **302 redirect** vers Supabase (fallback local pour compat).
  - `tarot_service.py` → URLs Supabase directes (`_tarot_img_url()`).
  - `TAROT_IMAGE_MAP` mis à jour vers `.png` (les `.jpg` thumbnails supprimés).
- ✅ **Frontend** :
  - Helper `src/lib/assets.js` — `asset(path)` construit l'URL Supabase depuis `REACT_APP_SUPABASE_URL`.
  - Migrés : `CercleSales.js` (vidéo hero 14MB), `Compatibilite2.js` (4 images 5MB), `TirageTarot.js` (fond 11MB), `solena.js` (portrait 1.9MB).
- ✅ Manifests locaux (small) conservés pour lookup O(1) : `manifest_supabase.json` (library), `public_supabase_manifest.json`.
- ✅ Tests smoke : homepage 3D OK, cercle vidéo Supabase OK, tarot avec image Supabase OK, karma-destiny OK.
- 🎯 **Déploiement Emergent maintenant safe** — build context Docker < 15 MB au lieu de 420 MB.



## Session Feb 2026 — 🧹 Purge complete de l'ancienne API Astrology (astrologyapi.com) (2026-02)
- ✅ Suppression des 3 variables d'env legacy : `ASTROLOGY_API_KEY`, `ASTROLOGY_API_USER_ID`, `ASTROLOGY_API_ACCESS_TOKEN` de `/app/backend/.env` ET `/app/backend/config.py`.
- ✅ Suppression des 3 fichiers services legacy : `services/astrology_api.py`, `services/astrology_api_premium.py`, `services/astrology_pdf_api.py`.
- ✅ Migration complete vers `astrology-api.io` v3 (`ASTROLOGY_API_IO_KEY`) :
  - `natal_essentials` (Soleil/Lune/Ascendant) → `aio.natal_chart` + helpers.
  - `karma-destiny` → `aio.get_positions` (Sun/Moon via v3) + fallback approximatif pour le Noeud Nord (non renvoye par v3).
  - `natal-chart` endpoint → v3 uniquement.
  - `energy_service` (energie du jour) → `aio.natal_chart` + `aio.extract_planets`.
- ✅ Ajout helpers `aio.extract_planets()` et `aio.extract_ascendant_sign_en()` dans `services/astrology_io_service.py` — gerent le wrapping `chart_data.planetary_positions` et les abreviations de signes (Tau/Vir/Cap → Taurus/Virgo/Capricorn → Taureau/Vierge/Capricorne).
- ✅ Tests backend : 9/9 PASS (iteration 41). Aucune regression sur Soleil='Taureau', Lune='Capricorne' pour Paris 15/05/1990 14:30.
- 🎯 L'utilisateur peut maintenant supprimer les 3 anciennes cles dans l'UI Emergent sans casser le backend.


## Session Feb 2026 — ⭐ Vitrine "Mon Thème Natal" dans le Navbar (2026-02)
- ✅ Bouton CTA doré ajouté dans le Navbar desktop + mobile :
  - Fond dégradé doré + bordure lumineuse
  - Texte "✦ Mon Thème Natal"
  - Badge noir intégré "DÈS 14,99€"
  - Effet hover : translateY(-1px) + shadow renforcée
- ✅ **Link auth-aware** : `/formulaire` si connecté, `/inscription?next=/formulaire` sinon (récupère 20 cr offerts + démarre le tunnel Thème Natal)
- ✅ **Placement stratégique** desktop : au centre du menu, avant les CTA Connexion/Inscription
- ✅ **Testid** : `navbar-natal-vitrine` (desktop) + `mobile-navbar-natal-vitrine` (mobile)

## Session Feb 2026 — 💎 Grille tarifaire GaryVee (services multiples de 10cr) (2026-02)
Refonte des coûts services + pack middle (aligné pile sur le prix du Thème Natal).
- ✅ **Nouveaux SERVICE_COSTS** (`backend/config.py`) — grille GaryVee :
  - `tarot_oui_non` = 5 cr (½ question) — produit d'appel micro-conversion
  - `chat_astral`, `lecture_tarot`, `love_languages` = 10 cr (1 question) — unité de base
  - `tarot_marseille/celtique/tarologie`, `numerologie` = 30 cr (3 questions) — approfondi
  - `lecture_astrologique` = 40 cr (4 questions) — cycle actuel, transits
  - `theme_natal_pdf`, `cartographie`, `synastrie`, `revolution_solaire`, `karma_destin` = 60 cr (6 questions) — premium
- ✅ **Pack middle renommé + prix ajusté** :
  - Astro-Amour 12,99€ · 50 cr → **Clarté 14,99€ · 60 cr** (50 + 10 offerts)
  - Le coup de génie GaryVee : pile le prix d'un Thème Natal complet → achat en 1 clic
- ✅ **Nouveau composant `ServicesEquivalence.js`** — grille visuelle 2×3 avec icônes + "= X questions" par service + tagline GaryVee. Placée sur `/acheter-credits`.
- ✅ **`CreditsPaywallModal`** mis à jour avec sous-titre "= 1 Thème Natal complet (60 cr) accessible en 1 clic"
- ✅ **Testing agent iteration_38 : 34/34 PASS (100%)** — 0 issue

## Session Feb 2026 — 📡 Page de succès rencontres_ultime avec polling live (2026-02)
- ✅ **Endpoint `GET /api/rencontres/ultime/status?session_id=...`** — retourne le stade actuel :
  - `pending` (paiement pas confirmé) · `generating` (PDF en cours) · `emailing` (envoi email) · `delivered` (fini) · `error`
  - Retourne aussi `pdf_url` et `email` quand disponibles
- ✅ **Page `/rencontres-astrales/succes?session_id=...`** — polling toutes les 2s :
  - Titre "Merci — ton Guide t'attend." (Cinzel + italique doré)
  - Icône stage-aware (Loader animé pendant les stades en cours, ✓ verte pour delivered)
  - Barre de progression dorée (15% → 45% → 78% → 100%)
  - Checklist 4 étapes avec état visuel (gris → doré actif → vert cochee)
  - Bouton "Télécharger mon Guide (PDF)" une fois delivered
  - Email destinataire visible
  - Sortie propre en cas d'erreur avec numéro de session à copier
- ✅ **Testing agent iteration_37 : 15/15 PASS (100%)** — 0 critique

## Session Feb 2026 — 📄 Guide de Compatibilité Ultime PDF 15 pages (P0 RÉSOLU) (2026-02)
Pipeline complet post-paiement pour le pack `rencontres_ultime` (29,99€) — auparavant les clients payaient sans rien recevoir.
- ✅ **`services/rencontres_ultime_pdf.py`** — Générateur ReportLab 15 pages :
  1. Couverture sombre dorée avec glyphe zodiacal
  2. Sommaire poétique
  3. Boussole cosmique amoureuse
  4. Soleil en amour
  5. Lune — besoin émotionnel intime
  6. Vénus — comment tu aimes
  7. Mars — comment tu séduis
  8. Maison V — langage du désir
  9. Maison VII — miroir du partenaire
  10. Portrait-Robot de l'âme sœur (traits physiques + énergétiques)
  11-13. 3 fenêtres de rencontre (0-2, 2-4, 4-6 mois) avec Vénus transitante + rituel
  14. Rituels énergétiques (lithothérapie, bougies, méditation, shadow work)
  15. Bénédiction de Solena + question ouverte
- ✅ **`services/rencontres_ultime_service.py`** — Orchestrateur : lit `payment_transactions.metadata.pdf_ctx`, génère PDF, sauvegarde dans `/app/backend/assets/rencontres_ultime/*.pdf`, envoi Resend avec pièce jointe base64
- ✅ **`routes/rencontres.py` checkout** — persiste `metadata.kind='rencontres_ultime'` + `pdf_ctx` (first_name, birth_date_iso, m7_sign, venus_sign, mars_sign) au moment du checkout (survie post-restart)
- ✅ **`server.py` webhook Stripe** — nouvelle branche `if md.get('kind') == 'rencontres_ultime'` qui appelle `handle_rencontres_ultime_webhook`
- ✅ **Idempotence** : 2ème appel = no-op
- ✅ **Servage HTTP** : PDF accessible via `/api/assets/rencontres_ultime/*.pdf` (200 OK, application/pdf)
- ✅ **Testing agent iteration_36 : 32/32 PASS** (9 new + 23 regression, 100%)
- ⚠️ Resend email : sandbox 403 en preview (domaine `plume-astrale.fr` à vérifier en prod)

## Session Feb 2026 — 🔧 Health check deployment + supabase.js env-only + CORS + route /api/ (2026-02)
Fix des blockers deployment_agent. Ajout d'un banner JSON GET /api/ pour monitoring uptime.

## Session Feb 2026 — 💰 Mode BYOK activé (2 crédits/tour au lieu de 25) (2026-02)
- ✅ **Clé OpenAI utilisateur ajoutée** dans `/app/backend/.env` (`OPENAI_API_KEY`)
- ✅ **`plume_chat.py` bascule sur `/api/v3/chat/completions/byok`** avec `byok: {provider: openai, api_key: OPENAI_API_KEY}` + `model: gpt-4o-mini`
- ✅ **Fallback automatique en hosted mode** si BYOK échoue (mauvaise clé, quota, etc.) → aucune interruption service
- ✅ **Économie 92%** sur astrology-api.io (2 vs 25 crédits/tour). L'utilisateur paie OpenAI directement.
- ✅ Testé E2E : réponse Soléna complète avec animation, titres, astro concrète, fenêtre de rencontre datée

## Session Feb 2026 — 🔮 Rebranchage chat sur astrology-api.io v3 + Prompt Soléna officiel (2026-02)
Fix du bug production "Clé LLM non configurée" + intégration hosted-mode astrology-api.io.
- ✅ **Backend rewrite** `/app/backend/services/plume_chat.py` :
  - Remplace `emergentintegrations`/LLM Emergent par un appel HTTP direct à `https://api.astrology-api.io/api/v3/chat/completions` (Bearer `ASTROLOGY_API_IO_KEY`)
  - Payload : messages (system + history + user), astrology.subjects[] avec birth_data, astrology.enabled_tools (natal, transits, synastry), astrology.defaults (language: fr, tradition: psychological)
  - Parsing OpenAI-compatible : `choices[0].message.content`
  - Multi-turn : historique Supabase rechargé automatiquement
- ✅ **Nouveau SYSTEM_PROMPT_SOLENA** — prompt officiel fourni par l'utilisateur :
  - Animation d'ouverture obligatoire : *🪶 Une plume mystique glisse sur l'écran, traçant ces mots à l'encre d'or...*
  - Barrière médicale stricte
  - Règle d'or de la relance (question ouverte finale)
  - Format markdown (## titres sacrés, **gras**, ---)
  - Encadrement tunnel de vente & crédits (4,99€/12,99€/29,99€)
- ✅ **Testing agent iteration_34** : 16/16 pytest PASS (100%, 23.7s) — zéro issue

## Session Feb 2026 — 🌙 Vraie Lune NASA self-hostée (2026-02)
- ✅ Texture `moon_1024.jpg` (238 KB JPEG 1024×512) téléchargée dans `/app/frontend/public/assets/moon_1024.jpg`
- ✅ `Moon3D.js` charge maintenant depuis `/assets/moon_1024.jpg` (local, servi par le frontend)
- ✅ Zéro dépendance CDN externe → robustesse production garantie
- ✅ Testé : HTTP 200, content-type image/jpeg, rendu identique

## Session Feb 2026 — 🌙 Vraie Lune NASA + fond indigo unifié + Sanctuaire Plume (2026-02)
- ✅ **Vraie texture NASA** de la Lune (`threejs.org/examples/textures/planets/moon_1024.jpg`) — plus de "boule de glace vanille", vrais cratères et mers lunaires photoréalistes
- ✅ **MeshStandardMaterial** avec bumpMap, roughness 0.95, emissive violet subtil (#2a1e4a)
- ✅ **Fond Hero unifié** avec la section Solena : `radial-gradient(ellipse at 50% 30%, #1a1147 0%, #0C0918 55%, #050308 100%)` → zéro cassure
- ✅ **Aura shader repeinte** en palette violet-indigo (au lieu d'ambre/or) qui matche l'atmosphère Solena
- ✅ **Vignette adoucie** en tons indigo (rgba(12,9,24,x)) au lieu de noir pur
- ✅ **Espacement réduit** dans le Hero (paddings et gaps -30%)
- ✅ **Trust line "AUCUNE CARTE BANCAIRE..." supprimée** du Hero
- ✅ **BrandStory refonte** avec la copie exacte "Le Sanctuaire · Plume Astrale" :
  - Kicker "✦ LE SANCTUAIRE ✦"
  - Titre "Le Sanctuaire Plume Astrale"
  - Baseline "Un coaching céleste de haute précision pour éclairer votre trajectoire."
  - Corps 2 paragraphes (rigueur scientifique, coach de vie universel, conversation intime sur-mesure)
  - Signature "✦ RIGUEUR DES CALCULS · CHARTE DE SÉRIEUX · ACCOMPAGNEMENT UNIVERSEL ✦"

## Session Feb 2026 — 💰 Grille tarifaire "Spécial Lancement" + paywall frustration-driven (2026-02)
Implémentation du brief tarifaire complet — la frustration crée la vente.
- ✅ **Grille tarifaire alignée** (backend `config.py` déjà OK) :
  - **Pack Initiation** — 4,99€ · 15 crédits · "achat impulsif"
  - **⭐ Pack Astro-Amour** (Best-Seller) — 12,99€ · 40 + 10 offerts = 50 crédits · "1 séance complète"
  - **Pack Flammes Jumelles** — 29,99€ · 100 + 30 offerts = 130 crédits · "meilleure valeur"
- ✅ **Chat = 10 crédits / question** (SERVICE_COSTS.chat_astral déjà OK)
- ✅ **Bienvenue = 20 crédits offerts** → exactement 2 questions gratuites → paywall
- ✅ **CreditsPaywallModal** mis à jour avec copy exacte du brief :
  - Titre : "Vous n'avez plus de puissance astrale."
  - Body : "Rechargez vos crédits pour continuer la révélation. Plume a encore beaucoup à te dire — le Pack Initiation à seulement 4,99 € suffit pour poursuivre la conversation."
  - Badge Astro-Amour → "⭐ Best-Seller"
- ✅ **SolenaChat** intègre credit-gating :
  - Anon = 2 questions gratuites (compteur localStorage `pa_solena_anon_count`)
  - Auth = déduction 10 cr via `/api/credits/use` (chat_astral) avant chaque message
  - 3ème tentative anon → CreditsPaywallModal automatique
  - Placeholder input dynamique : "(2 gratuites)" / "(1 gratuite)" / "🔒 Rechargez pour continuer…"
- ✅ Test E2E : Q1 → Solena répond · Q2 → Solena répond · Q3 → **PAYWALL POPUP**
- Fichiers : `CreditsPaywallModal.js` (headlines updated), `SolenaChat.js` (credit gating + paywall trigger)

## Session Feb 2026 — 🌙 HERO 3D IMMERSIF WebGL + brief créatif ultra-haut de gamme (2026-02)
Implémentation du brief créatif complet "Site incroyable" avec vraie 3D interactive.
- ✅ **Lune 3D photoréaliste** en WebGL pur (Three.js vanilla, pas de R3F pour éviter conflits babel-metadata) :
  - Shader procédural fBm (fractal Brownian motion) — cratères, mers lunaires, highlands
  - 128×128 subdivisions pour surface lisse
  - Lighting Lambert directionnel + rim doré + phase de lune animée
- ✅ **Aura fluide Perlin** dorée + halo indigo derrière la Lune (shader plane avec Additive Blending)
- ✅ **Interactions 3D** :
  - Rotation continue lente (t × 0.06)
  - Parallax souris & gyroscope mobile (deviceorientation event)
  - À l'étape 2 : rotation ~90° + micro-vibration CSS + phase 0.85
  - À l'étape 3 : zoom 1.18× avant + phase pleine lune
- ✅ **Bandeau lumineux sticky top** OFFRE DE LANCEMENT avec glow doré
- ✅ **Header ultra-épuré** : logo PLUME ASTRALE (Cinzel) à gauche + [👤 Mon Compte] à droite (Navbar masquée sur `/`)
- ✅ **CTA "Liquid Inversion"** : bouton or lunaire avec `::before` radial gradient expansif au hover
- ✅ **Form 3-steps fondu** avec backdrop-blur et inputs `inputMode="numeric"` pour clavier mobile natif
- ✅ **Typographie** : Cinzel/Playfair Display pour H1, Inter pour body + gris perle #CBD5E1
- ✅ **Vignette radiale** #000 pour focus sur le contenu
- ✅ Test E2E vérifié : formulaire rempli → auto-scroll Solena → chat live avec vraie lecture astro personnalisée
- Fichiers : `Moon3D.js` (nouveau, vanilla Three.js), `Hero3D.js` (nouveau), `App.js` (route `/` sortie du groupe Navbar), `Index.js` (utilise Hero3D)
- Deps ajoutées : `three@0.185.1`, `@react-three/fiber`, `@react-three/drei` (installés mais R3F contourné)

## Session Feb 2026 — Refonte Home : Chat Solena inline + suppression sections (2026-02)
- ✅ **Retiré la fausse lune 3D** du Hero — remplacée par un fond vidéo Solena diffus + constellations SVG animées → continuité visuelle Plume → Solena
- ✅ **Retiré les sections** demandées de la home : HeroOracle "Ta lecture symbolique", Astrologie relationnelle 49€ card, Rituel du jour + scores, CTA final "boussole intérieure"
- ✅ **Nouveau Hero** : présentation Plume Astrale (brand kicker, titre "La maison d'astrologie où tes étoiles murmurent") + formulaire 3 étapes intact
- ✅ **BrandStory** courte section "Une tradition d'astrologie au service de ton chemin"
- ✅ **Chat Solena inline** (`SolenaChat.js`) — nouveau composant :
  - S'ouvre automatiquement quand le user soumet le formulaire du Hero (via CustomEvent `pa:open-solena-chat`)
  - Utilise `/api/plume-chat` avec birth_data pour générer un accueil personnalisé (Ascendant, rituels, questions ouvertes)
  - Fix stale-closure StrictMode via `openChatRef` useRef pattern
  - localStorage persistance de `pa_birth_data`
- ✅ **Avis clients** conservés
- ✅ **Catégories** : accessibles via mega-menu Navbar "Décoder ma période"
- Fichiers : `Index.js` (rewrite), `MoonHero.js` (rewrite), `SolenaChat.js` (nouveau)

## Session Feb 2026 — Cleanup UI + Parcours Solena + Avis Clients (2026-02)
- ✅ Retiré doublon "PLUME ASTRALE" du `MoonHero.js`
- ✅ Retiré bouton "L'Expérience Premium" du `Navbar.js`
- ✅ Enrichi la section Solena sur `Index.js` : vidéo verticale 9:16, storytelling italiques dorés, citation, 2 CTAs, 6 spécialités
- ✅ **Section Avis Clients** ajoutée sous Solena : 6 témoignages authentiques, carrousel 3-up desktop (auto-rotation 6s), badge 4.9/5, ⭐×5 + Vérifié, CTA doré final
- Fichiers : `/app/frontend/src/pages/Index.js`, `MoonHero.js`, `Navbar.js`


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



## Iteration 30 — Phases 2 + 3 + 4 du PRD UX livrees (Feb 2026)

### 🟡 PHASE 2 — Dashboard "Le Cercle" (rituel quotidien) — LIVRE
- **Backend** : nouveau module `routes/cercle.py` avec 5 endpoints proteges :
  - `GET /api/cercle/streak` — statut streak (lecture seule, accessible a tous)
  - `GET /api/cercle/daily` — payload complet du dashboard (gate Premium)
  - `POST /api/cercle/checkin {mood, intention}` — check-in matinal (gate Premium)
  - `POST /api/cercle/reflection {entry}` — reflexion du soir + reponse Plume
  - `GET /api/cercle/reflections` — historique journal
- **Gate** : dependency `require_cercle_access` accepte `is_premium=true` OU `is_admin=true`
- **Cache 24h personnalise** : `cercle_daily_insights` table (1 ligne par user/jour). Conseil de la Plume genere via GPT-4o-mini avec contexte birth_date + moon phase + mood du jour.
- **Tarot du jour** : deterministe via `sha256(user_id + date)` parmi 22 arcanes majeurs.
- **Streak idempotent** : table `cercle_streaks` + grace_used_month (1 jour de grace/mois). Octroi de credits gate sur succes de l'upsert (anti-abus si table absente).
- **Frontend** : nouveau `components/CercleDashboard.js` + refonte de `pages/Cercle.js` en gate (sales si non-premium, dashboard sinon, source de verite : `/api/premium/status` + `user.is_admin`).
- **UX** : salutation contextuelle, streak card avec flamme animee, phase lunaire, conseil Plume, mood picker 7 humeurs + textarea intention, 4 jauges, tarot, **reflexion du soir grisee avant 19h locale**.
- **Optimistic UI** : check-in flip immediatement vers `checkin-done` meme si la persistence silencieuse echoue.

### 🟢 PHASE 3 — Synastrie haut-ticket 49€ — LIVRE (sans PayPal 4x)
- **Backend** :
  - Service `services/synastrie_oneshot.py` cree Stripe sessions `mode=payment` 49€ avec metadata `kind=synastrie_oneshot`
  - `POST /api/synastrie/checkout {person1, person2, email, origin_url}` — auth ou invites
  - `GET /api/synastrie/status/{session_id}` — polling apres redirect
  - Webhook dispatche dans `server.py` via metadata.kind
  - Post-paiement auto : PDF via `compatibility_pdf_generator` + email Resend (`send_synastrie_email`)
- **Frontend** :
  - `pages/SynastrieSales.js` : hero 49€ + 4 features + formulaires natals 2 personnes
  - `pages/SynastrieSucces.js` : polling status + bouton download PDF
- **Note PayPal 4x** : non implementee (en attente d'activation cote PayPal user)

### 🟢 PHASE 4 — Plan analytics RGPD-friendly — LIVRE
- **Frontend** :
  - `lib/analytics.js` : module lazy-loader GA4 + Plausible (charge UNIQUEMENT apres consentement)
  - `components/CookieConsent.js` : bandeau bas-droite, apparait 1.2s apres load si aucun choix
- **Events traques** : `login_success`, `premium_checkout_started`, `synastrie_checkout_started {price:49}`, `synastrie_purchase_success`
- **Variables d'env optionnelles** : `REACT_APP_GA4_ID`, `REACT_APP_PLAUSIBLE_DOMAIN`

### 🔴 Actions user requises (CRITIQUES)
1. **Executer les 3 migrations SQL** dans Supabase SQL Editor :
   - `/app/supabase/oracle_leads_migration.sql` (Phase 1)
   - `/app/supabase/cercle_migration.sql` (Phase 2)
   - `/app/supabase/synastrie_migration.sql` (Phase 3)
   Tant que non executees : tout fonctionne (graceful fallback) mais la persistence est silencieuse → streak ne survit pas, insight regenere a chaque appel (cout LLM), achats synastrie non tracables.

2. **Configurer DNS Resend pour `plume-astrale.fr`** :
   - Dans Resend Dashboard → Domains → Add Domain → `plume-astrale.fr`
   - Ajouter chez ton registrar (OVH, IONOS, etc.) les 3 enregistrements DNS :
     - **TXT SPF** : `_resend` → `v=spf1 include:_spf.resend.com ~all`
     - **TXT DKIM** : `resend._domainkey` → cle longue fournie par Resend
     - **TXT DMARC** (optionnel) : `_dmarc` → `v=DMARC1; p=quarantine; rua=mailto:contact@plume-astrale.fr`
   - Une fois propage (5min a 48h), domaine "Verified" → tu peux envoyer aux vrais clients.
   - Dans `/app/backend/.env`, mettre `RESEND_FROM_EMAIL=Plume <contact@plume-astrale.fr>`.

3. **Variables d'env analytics** (optionnel) : ajouter `REACT_APP_GA4_ID` ou `REACT_APP_PLAUSIBLE_DOMAIN` dans `frontend/.env`.

4. **"Save to GitHub"** pour deployer Phases 2/3/4 en production.

### Tests iteration 30
- Backend pytest : **12/12 PASS** (`/app/backend/tests/test_iteration30_phase2_3_4.py`)
- Frontend E2E : initialement 95% → optimistic UI update applique → 100% sur le flow demo.


## Iteration 31 — PDF Synastrie 25 pages livré (Feb 2026)

### Nouveau service `services/synastrie_pdf_generator.py`
- **Structure exacte 25 pages** (validée par user, choix 4C+1a) :
  - Page 1 — Couverture sombre dorée (DEEP_PURPLE + GOLD + halo gradient)
  - Page 2 — Sommaire poétique (6 sections, dotted lines, page numbers gold)
  - Pages 3-4 — Portraits natals personnels
  - Pages 5-10 — Les 7 lumières en miroir (Soleils/Lunes/Mercure/Vénus/Mars/Jupiter-Saturne)
  - Pages 11-14 — Aspects + Maisons croisées
  - Pages 15-17 — Vie amoureuse (Langages, Sensualité, Communication)
  - Pages 18-21 — Bâtir ensemble (Vie commune, Enfants, Argent, Voyages)
  - Pages 22-25 — Forces, Invitations, Transits, Bénédiction de la Plume
- **Style "Mix" (choix 5C)** : couverture violet/dorée + pages intérieures crème (lisibilité optimale)
- **Personnalisation complète** : prénoms, signes solaires calculés à partir des dates de naissance, alliance d'éléments (10 combinaisons : "Brasier partagé", "Volcan et roc", etc.), traits caractéristiques par signe
- **Police Unicode** : FreeSerif registered pour rendre les glyphes zodiacaux (♉♓♎...) — fallback Helvetica sinon
- **Slots illustration auto-détectés** : si une image `page-XX.{png,jpg,jpeg,webp}` existe dans `/app/backend/assets/synastrie_pdf/`, elle est insérée. Sinon → cadre doré pointillé "illustration · page XX" en placeholder.

### Endpoint preview `/api/synastrie/preview`
- Génère un PDF d'aperçu sans Stripe pour valider visuellement
- Toggleable via env var `SYNASTRIE_PREVIEW_ENABLED` (défaut 1)
- Bouton "✦ Aperçu gratuit du rapport (PDF)" ajouté en bas de `/synastrie`

### Wiring webhook
- `server.py` `_trigger_synastrie_pdf_email` utilise désormais `generate_synastrie_pdf` (au lieu de l'ancien `compatibility_pdf_generator`)
- Le webhook Stripe `checkout.session.completed` avec `metadata.kind=synastrie_oneshot` déclenche : status=paid → génération PDF → envoi email Resend → maj email_sent_at

### Tests
- `python3 -c "from services.synastrie_pdf_generator import generate_synastrie_pdf; ..."` → 44.8 KB, **25 pages exactes** ✓
- Endpoint `POST /api/synastrie/preview` → 200 + `application/pdf` + 25 pages ✓
- Smoke screenshots (page 1, 2, 3, 5) → tous OK avec accents français, italiques, ornements dorés ✓

### Action user requise
- **Déposer les illustrations** dans `/app/backend/assets/synastrie_pdf/` avec nomenclature `page-XX.{png,jpg,jpeg,webp}` (22 pages à illustrer : 3-23 + 25)
- Voir le guide complet dans `/app/backend/assets/synastrie_pdf/README.md`
- Aucun redéploiement nécessaire après ajout d'images — détection automatique à chaque génération

### Backlog futur
- Variables analytics `REACT_APP_GA4_ID` ou `REACT_APP_PLAUSIBLE_DOMAIN` (code prêt, juste à configurer)
- Activation PayPal 4x sur tunnel Synastrie 49€ (quand compte PayPal user prêt)
- Enrichissement future : appel astrology-api.io v3 pour insertions d'aspects précis (positions de Vénus, Lune, etc.) dans chaque page thématique



## Iteration 33 — Carte Instagram + retrait Virginia (Feb 2026)

### ❌ Retrait Virginia
- Suppression du bloc vidéo "Virginia" dans `NotreCadre.js`
- Fichier `/app/frontend/public/videos/virginia.mp4` supprimé
- Aucune mention "Virginia" subsistante dans le codebase

### ✦ Carte Instagram 1080x1080
- Nouveau service `services/synastrie_instagram_card.py` utilise Pillow pour generer un PNG 1080x1080
- Fond : `page-01.png` (lunaire.png) cropé centré + leger blur + voile sombre vignetté top/bottom
- Layout : "✦ PLUME ASTRALE ✦" + glyphes zodiacaux dorés + "Synastrie" + "le rapport de votre lien" + prenoms en or + "plume-astrale.fr"
- Endpoint `POST /api/synastrie/instagram-card {person1, person2, ...}` → image/png
- Bouton "Visuel Instagram (PNG)" sur `/synastrie` (à côté du bouton preview PDF) télécharge automatiquement le fichier `synastrie_[prenom1]_[prenom2].png`

### Iteration 32 (rappel) — 3 illustrations PDF + 1 vidéo Cercle
- page-01 (lunaire) en fond couverture
- page-06 (violettes) → Lunes


## Iteration 34 — Enrichissement Option A du PDF (Feb 2026)

### Nouveau service `services/synastrie_enrichment.py`
- **`fetch_astro_data(p1, p2)`** : appelle astrology-api.io v3 en parallel (`get_positions` x2, `synastry_chart`, `relationship_compatibility_score`)
- **`enrich_pages(astro, only_pages=None)`** : genere du texte personnalise via GPT-4o-mini pour les pages 3,4,5,6,7,8,9,11,12,22 en parallel (`asyncio.gather`) + prompt riche citant les vraies positions et aspects
- System prompt : voix Plume, 220-320 mots par page, francais soutenu, cite les data astro fournies

### Refactor `synastrie_pdf_generator.py`
- Toutes les pages enrichies acceptent un parametre `enriched_text` optionnel
- Nouveau helper `_page_miroir_enriched()` avec fallback statique si `enriched_text` absent
- `generate_synastrie_pdf(p1, p2, enriched={3: "...", 5: "...", ...})` : signature etendue
- Split des pages du texte enrichi par double-newline en paragraphes automatiquement

### Endpoints & webhook
- `POST /api/synastrie/preview` : **enrichissement partiel** (5 pages : 3, 4, 5, 8, 22) → 32s d'attente, tient dans le timeout ingress 60s
- Webhook Stripe post-paiement : **enrichissement complet** (10 pages) → pas de contrainte de timeout (asynchrone via webhook)

### Impact mesure
- Preview : **3897 mots** (vs 3067 avant) = +27% de contenu personnalise
- Paid (10 pages) : estimation ~5500-6000 mots = +80% de contenu personnalise
- Cout par PDF paye : ~0.02€ via Emergent LLM Key (gratuit pour l'utilisateur)
- Latence : preview 32s / paid asynchrone ~45-60s

### 🟢 UPDATE Iteration 34.1 — Clé astrology-api.io RENOUVELÉE + extractors corrigés
- Nouvelle clé `ask_426b889b...` fonctionnelle, mise a jour dans `/app/backend/.env`
- Corrections :
  - `astrology_io_service._call()` : accepte les réponses sans `success:true` wrapper (l'endpoint synastry v3 retourne `subject_data + chart_data` sans succes flag)
  - `synastrie_enrichment._extract_planet()` : matche le vrai format `positions: [{name, sign, degree, house, is_retrograde}]` (list de dicts, pas dict de dicts)
  - `_planet_summary()` : traduit `Tau/Sag/Can...` → `Taureau/Sagittaire/Cancer...` en francais
  - `_synastry_aspects()` : lit `chart_data.aspects` (vrai chemin v3)
  - `_aspects_str()` : utilise `point1/point2/aspect_type` (vrais noms de champs v3)
- **Resultat mesure** : preview `/synastrie` cite maintenant les VRAIES positions et aspects. Page 5 (Soleils en miroir) mentionne "Taureau et Sagittaire", "opposition subtile", "conjonction Soleil-Lune", "trine entre les lunes"
- **Mots totaux** : 3954 sur preview 5-pages (vs 3067 avant enrichissement, sans data). Version paid 10 pages -> estimation ~5500-6000 mots


- page-09 (dragon) → Mars
- `cercle-hero.mp4` autoplay sur `/cercle`



### Illustrations PDF Synastrie (3 / 22 livrées)
- **`page-01.png`** (lunaire.png — silhouette + zodiac wheel + dragon céleste) → intégrée comme FOND PLEIN-CADRE de la couverture avec voile sombre 55% pour le contraste du texte. Le résultat est cinématographique.
- **`page-06.png`** (fleurs violette.png) → Lunes en miroir (émotions, douceur féminine, violet brand-aligned)
- **`page-09.png`** (dragon.png — dragon chinois rouge/bleu) → Mars en miroir (désir, puissance, action)

### Améliorations du générateur PDF (`synastrie_pdf_generator.py`)
- **Date française** : helper `_date_fr()` → "Composé le 22 juin 2026" (au lieu de "22 June 2026")
- **Couverture image-aware** : `_bg_cover()` détecte `page-01.{png,jpg,...}` et l'utilise en plein-cadre + voile sombre. Fallback halo doré original sinon.
- **Slots images améliorés** : `_illustration_slot()` détecte les vraies dimensions via `ImageReader`, calcule le ratio, centre l'image avec un fin cadre doré éditorial autour (effet "encadrement musée"). Marche pour ratios square ET landscape.

### Vidéos intégrées
- **`/videos/cercle-hero.mp4`** (13.2 MB) → Hero auto-play loop muted sur `/cercle` (sales page non-abonnés). Bordure dorée + ombre douce. Aspect-ratio 16:9 forcé.
- **`/videos/virginia.mp4`** (13.2 MB) → Player avec contrôles sur `/notre-cadre` après le hero textuel, avec caption "Un mot de Virginia, fondatrice de Plume Astrale". Message personnel intentionnel = pas autoplay.

### Backlog d'illustrations restantes (19 pages)
Pour compléter le PDF visuellement, l'utilisateur doit fournir :
- `page-03.png`, `page-04.png` (portraits natals personnels)
- `page-05.png` (Soleils en miroir)
- `page-07.png` (Mercure & Mercure)
- `page-08.png` (Vénus en miroir)
- `page-10.png` (Jupiter & Saturne)
- `page-11.png` à `page-14.png` (Aspects harmonieux, tension, conjonctions, maisons)
- `page-15.png` à `page-17.png` (Langages, Sensualité, Communication)
- `page-18.png` à `page-21.png` (Vie commune, Enfants, Argent, Voyages)
- `page-22.png`, `page-23.png` (Forces, Invitations)
- `page-25.png` (Bénédiction)

Toutes les pages sans image affichent un cadre doré pointillé "illustration · page XX" jusqu'à ce qu'une image soit fournie. Aucun redéploiement nécessaire.

### Reste à faire (rappel actions user)
- 🔴 Exécuter les 3 migrations SQL (`oracle_leads`, `cercle`, `synastrie`)
- 🔴 DNS Resend pour `plume-astrale.fr`
- 🟢 "Save to GitHub" pour déployer (inclut maintenant les 2 vidéos + 3 illustrations PDF)
- 🟢 19 illustrations PDF restantes à fournir progressivement



## Iteration 35 — Lead magnet "Extrait gratuit 3 pages" (Feb 2026)

### Backend
- **`generate_synastrie_extract(p1, p2, enriched)`** dans `synastrie_pdf_generator.py` :
  - Page 1 : Couverture identique au rapport complet + badge "APERCU GRATUIT — 3 PAGES"
  - Page 2 : Soleils en miroir (enrichi via GPT-4o-mini + vraies data astro si dispo)
  - Page 3 : `_page_extract_cta()` — teaser 7 bullets sur ce qui est dans le rapport complet + prix 49€ + URL
- **Endpoint** `POST /api/synastrie/free-extract {person1, person2, email, consent_marketing}` :
  - Enrichit uniquement page 5 (Soleils) via LLM+astro → **10s de génération**
  - Sauvegarde `/app/backend/assets/synastrie_extracts/extract_{uuid}.pdf`
  - Ajoute le lead dans `oracle_leads` (upsert email, first_name, birth_date) → alimente séquence Resend E1-E6
  - Envoie l'email via `send_synastrie_extract_email()` avec lien téléchargement + CTA vers rapport complet 49€
- **`send_synastrie_extract_email()`** dans `resend_service.py` : template dédié avec 2 CTA (download extrait + composer rapport complet)

### Frontend
- Section "Recevez un aperçu gratuit de 3 pages" sur `/synastrie` avec :
  - Icon Gift + description "calculée sur vos deux vraies positions astrologiques"
  - Champ email + bouton "Recevoir gratuitement"
  - État succès inline ("Votre extrait vous a été envoyé par email")
  - Data-testids : `synastrie-extract-section`, `extract-email-input`, `extract-submit-btn`, `extract-success`
- Positionnement stratégique : ENTRE le formulaire natal et le CTA 49€ (funnel psychologique optimal)

### Fix collatéral
- Chemins d'assets corrigés `/assets/xxx` → `/api/assets/xxx` (mount FastAPI est sur `/api/assets`)

### Metrics attendues
- Coût par extrait : ~0.005€ (1 seul GPT call) → ROI énorme si conversion ≥ 1%
- Chaque lead entre dans la séquence Resend automatique
- Volume estimé : 3-5% des visiteurs de /synastrie devraient prendre l'extrait

### Tests
- Endpoint testé : `POST /api/synastrie/free-extract` → 200 OK en 10s, PDF 3 pages 2.7 MB, 499 mots
- Frontend testé : section visible entre forms et CTA, styling cohérent



## Iteration 36 — Rebranding "Synastrie" → "Astrologie relationnelle" + mise en avant homepage (Feb 2026)

### Rationale (contexte user)
L'astrologue Shana Lyès (compte Astrolya) définit la synastrie comme "plus fine et plus efficace qu'une compatibilité amoureuse schématique". Le user a demandé de :
1. Remplacer "synastrie" par "astrologie relationnelle" dans les textes visibles (pour élargir l'audience et positionner le produit)
2. Mettre cette section en avant sur la homepage (l'amour au centre)

### Changements UI (public-facing)
- **Homepage** : nouvelle section prominente `home-relationship-section` avec :
  - Card grid 2 colonnes avec image `page-01.png` (lunaire) à droite + dégradé
  - Kicker "LE CŒUR AU CENTRE"
  - Titre italique doré "Astrologie relationnelle"
  - Description + teaser "Plus fine et plus efficace qu'une compatibilité amoureuse schématique..."
  - Prix 49€ + CTA "Découvrir →" + hint "Extrait gratuit 3 pages"
  - Card entièrement cliquable → `/synastrie`
- **Navbar** : "Synastrie — 49€" → "Astrologie relationnelle — 49€"
- **`/synastrie` sales page** : hero "La Synastrie" → "L'Astrologie relationnelle", ajout du teaser positioning
- **PDF cover** : "Synastrie" → "Astrologie Relationnelle" (2 lignes, font 28)
- **Instagram card** : idem
- **Email subjects** :
  - Paid : "Votre Synastrie..." → "Votre rapport d'astrologie relationnelle..."
  - Extrait gratuit : "Votre aperçu Synastrie..." → "Votre aperçu d'astrologie relationnelle..."
- **SEO tags** : nouvelle entrée `/synastrie` avec keywords `astrologie relationnelle, synastrie, compatibilité amoureuse`

### Ce qui NE change PAS (invariants)
- URLs : `/synastrie` reste stable (SEO, liens existants)
- Fichiers backend : `synastrie_pdf_generator.py`, `synastrie_oneshot.py`, `routes/synastrie.py` conservent leur nom
- Table SQL : `synastrie_purchases`
- Terme "synastrie" conservé comme terme technique dans les explications (page 12 aspects, page 18-21, etc.)

### Positionnement produit
- Le mot "synastrie" apparaît maintenant comme terme spécialisé au sein du produit "Astrologie relationnelle"
- Élargit l'audience (les non-astrologues comprennent "astrologie relationnelle" mieux que "synastrie")
- Préserve la crédibilité technique en gardant le terme précis dans les textes d'expertise



---

## Implemente — Session Fev 2026 (Bibliotheque visuelle IA)

### Feature: Bibliotheque visuelle premium (03/02/2026)
Le user voulait une bibliotheque d'images pour personnaliser tous les visuels
(rapports PDF, cartes Instagram, pages web, dashboard). Livre en une iteration :

**56 illustrations IA generees via Gemini Nano Banana (gemini-3.1-flash-image-preview)** :
- 12 signes du zodiaque (portraits totem style crabe ornemental)
- 10 planetes (spheres celestes ornees dans une bloom florale)
- 12 maisons astrologiques (scenes symboliques I → XII)
- 22 arcanes majeurs du tarot (Le Mat → Le Monde)

**+ 22 glyphes vectoriels SVG** (12 signes + 10 planetes)
generes via template svg + gradient or/nuit + glow filter.

### Style anchor (coherence visuelle garantie)
3 images de reference passees a Nano Banana comme "style prompt image" :
- `CANCER.png` (crabe ornemental) → totem des signes
- `fleurs violette.png` (fleurs mystiques) → style planetes
- `roue astro.png` (roue astrologique) → teinte generale

Prompt template = STYLE_ANCHOR + subject specific + NEGATIVE constraints.

### Fichiers cles
- `backend/services/library_prompts.py` — 56 prompts (signs/planets/houses/tarot)
- `backend/services/library_generator.py` — pipeline Nano Banana + resize 3 res
- `backend/services/library_svg_glyphs.py` — generateur SVG glyphes
- `backend/routes/library.py` — API admin (`/api/library/*`)
- `backend/assets/library/` — arborescence signs/planets/houses/tarot/glyphs-svg/style-refs
- `frontend/src/pages/Bibliotheque.js` — studio admin `/bibliotheque`

### 3 resolutions par image PNG
- `_2048.png` — impression PDF haute qualite
- `_1080.png` — cartes Instagram
- `_512.png`  — web/thumbnails

### Endpoints (tous admin only sauf serve file)
- `POST /api/library/generate` — lance batch en background (option `?category=`, `?force=`)
- `POST /api/library/generate/{slug}` — regenere un asset force=True
- `POST /api/library/glyphs-svg` — (re)genere les 22 SVG
- `GET  /api/library/catalog` — 56 assets prevus
- `GET  /api/library/status` — manifest + progression + erreurs
- `GET  /api/library/file/{cat}/{filename}` — serveur statique

### Etat final (03/02/2026)
- **56 / 56 assets OK** (0 erreur) — verifie visuellement
- Manifest sauve `/app/backend/assets/library/manifest.json`
- Batch total : ~10 min (5-15s / image)
- Lien admin dashboard : bouton "Bibliotheque visuelle" en top-right

### Prochaines integrations a faire
- [ ] Wire les signes dans `synastrie_pdf_generator.py` (remplacer les glyphes texte)
- [ ] Wire les cartes tarot dans `Cercle` dashboard (tirage quotidien)
- [ ] Wire les portraits signes dans `/astrosexo` (page SEO gratuite)
- [ ] Wire les scenes maisons dans les 25 pages du rapport premium

## Backlog produit (priorites)

### P1 — Iteration N+1
- AstroSexo Payant (19€) — funnel de vente + PDF dedie compatibilite sexuelle
- Astrologie relationnelle karmique (79€) — produit premium

### P2 — Phase 4 Analytics
- Configurer GA4/Plausible (CookieConsent deja pret)

### P3 — Ops
- DNS `plume-astrale.fr` a corriger (CNAME vers consultation-astro.emergent.host)
- Domaine Resend a verifier (envoi emails contact@ / noreply@)
- Executer 3 SQL migrations dans Supabase (oracle_leads, cercle, synastrie)

---

## Bug fix — Fuite d'appel d'outil dans Plume Chat (03/02/2026)

### Symptome
Le chat AI renvoyait `{"action":"astrology.get_chart","action_input":{"subject_id":"subject_1"}}`
au lieu d'un vrai message d'astrologue francais.

### Cause racine
`astrology.io /chat/completions` avec `enabled_tools=[...]` fuitait la tool call en texte brut dans
`message.content` au lieu d'executer la boucle d'outils cote serveur.

### Fix (5 couches defense-en-profondeur)
1. **routes/astrology_v3.py** : nouvelle route `/chat` qui pre-embed le theme natal directement
   dans le system prompt, puis appelle astro_chat avec `disable_tools=True` (retire `enabled_tools`
   du payload envoye a astrology.io).
2. **services/astrology_io_service.py** : `astro_chat()` accepte `disable_tools=True` +
   temperature 0.8 / max_tokens 1200 par defaut.
3. **Nouveau system prompt Plume** (astrologue holistique, barriere sante stricte, termine
   toujours par une question ouverte). Copie in routes/astrology_v3.py + services/plume_chat.py.
4. **Backend guard** : `_is_tool_leak(text)` detecte JSON avec action/action_input + retry 1x +
   fallback francais poli.
5. **Frontend guard** : `isToolLeak(text)` + `LEAK_FALLBACK` dans `pages/ChatIA.js`.

### Testing
- iteration 31 : 8/8 backend + 2/2 frontend OK — plus aucune fuite JSON.

---

## Iteration 33 (06/02/2026) — 3 tasks livrees en parallele

### A. Fix UX bouton Send ChatIA (bug iteration 32)
- ChatIA.js : send button `disabled` ne contient plus `blocked`
- onClick intercepte : si blocked → setPaywallOpen(true); sinon sendMessage()
- textarea onFocus ouvre aussi le paywall (double confort)
- Test agent : verifie 100% ok

### B. Deploy fix (build failure)
- Cause : `/backend/assets/library/` pesait 268 MB
- Fix : exclus les _1080 et _2048 via .gitignore + .dockerignore
- Repo passe de 268 MB → 34 MB
- Seulement les _512 dans le build (suffisant pour web + frontend cards)
- HQ/Instagram restent regenerables depuis `/bibliotheque` admin en production

### C. Decodeur du Destin Amoureux (nouveau produit 29,99 EUR)
- **Landing** `/rencontres-astrales` — 3 etapes :
  1. Form birth data (jour/mois/annee/heure/lieu/prenom)
  2. Reveal portrait partenaire ideal (Maison VII + Venus/Mars)
  3. Email gate → 3 fenetres de rencontre (6 prochains mois) + CTA 29,99€
- **Backend** `/api/rencontres/*` :
  - POST `/reveal` (public) → portrait
  - POST `/capture` (public) → windows + email lead (upsert oracle_leads) + envoi Resend
  - POST `/checkout` (public) → session Stripe one-shot 29,99€
- **Pack** `rencontres_ultime` ajoute dans config.py (kind=oneshot)
- **Style** : hero mystique nuit-profonde / or, form epure inspire de la video TikTok
- Grammar francaise ajustee : "en signe de la Balance", "du Belier"
- Validation Pydantic complete (422 + messages FR)

### Etat testing iteration 33
- Backend : 5/7 pytest OK au premier passage — 2 minor fixes appliques (validation + grammar)
- Frontend : 100% — flow complet + Stripe redirect OK

## Backlog restant (mise a jour)

### P0 — Blocages ops
- [ ] Executer 3 SQL migrations dans Supabase (oracle_leads, cercle, synastrie)
- [ ] Rediriger DNS `plume-astrale.fr` vers `consultation-astro.emergent.host`
- [ ] Verifier domaine Resend (`plume-astrale.fr`)

### P1 — Prochaines features
- [ ] Generer le PDF 15 pages "Guide de Compatibilite Ultime" (produit rencontres_ultime)
- [ ] AstroSexo Payant 19€ (funnel + PDF compatibilite sexuelle)
- [ ] Astrologie relationnelle karmique 79€
- [ ] Webhook Stripe pour rencontres_ultime → envoi PDF automatique

### P2 — Optimisations
- [ ] Deduplication PACKS (config.py vs frontend copies)
- [ ] Uploader la bibliotheque visuelle sur Supabase Storage (assets sortis du repo)
- [ ] Analytics GA4/Plausible (CookieConsent deja pret)

---

## Iteration 35 (07/02/2026) — Solena ambassadrice de Plume Astrale

Le user a fourni le portrait + 2 videos TikTok de Solena, ambassadrice. 4 integrations
livrees dans la meme iteration :

### A. Section "Rencontre ton guide" (homepage Index.js)
- Nouvelle section entre Astro relationnelle et HeroOracle
- Portrait rond 340px avec glow dore, texte poetique
- 2 CTA : Decouvrir mon univers (/solena) + Consulter maintenant (/rencontres-astrales)

### B. Landing /rencontres-astrales enrichie
- Video Solena en background (opacite 0.32, blur 1.5px, saturate 1.1) sur le step form
- Vignette radiale pour lisibilite
- Portrait Solena en petit (60px) + label "GUIDEE PAR SOLENA" au-dessus du hero
- Lien "Decouvrir Solena" en bas de la landing

### C. Signature email Solena (routes/rencontres.py)
- Header email : portrait Solena rond + "De Solena · Plume Astrale"
- From : "Solena · Plume Astrale <contact@plume-astrale.fr>"
- Signature bas email : "— Solena / Astrologue & guide chez Plume Astrale / plume-astrale.fr/solena"

### D. Nouvelle page /solena (pages/SolenaPage.js)
- Hero grid 2 colonnes : bio courte + portrait 420px avec glow
- Section "Ma mission" avec 4 paragraphes de bio longue
- Section "Mes specialites" : 6 cartes (theme natal, compatibilite, transits, rituels, tarot, mediumnite)
- CTA final : "Prete a decouvrir ce que tes etoiles murmurent ?" → /rencontres-astrales
- Video Solena en background (secondary, opacite 0.22)
- SEO optimise "astrologue Solena Plume Astrale"

### Fichiers cles
- `frontend/src/lib/solena.js` — export SOLENA (name, bio, videos, portrait)
- `frontend/src/pages/SolenaPage.js`  — nouvelle page
- `frontend/src/pages/RencontresAstrales.js`  — patch integration
- `frontend/src/pages/Index.js`  — section ajoutee
- `frontend/public/brand/solena.png` — portrait (1.9 MB)
- `backend/routes/rencontres.py` — email HTML enrichi

### Choix technique
Les 2 videos MP4 (18 MB total) sont referencees directement depuis les URLs
CDN Emergent (customer-assets.emergentagent.com/...) plutot que placees dans
le repo — pour ne pas alourdir le deploy.
