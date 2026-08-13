# Plume Astrale — PRD

## Original Problem Statement (v3, 2026-08-13 · strategic repositioning)
Plume Astrale n'est plus positionné comme un « site d'astrologie » mais comme une **marque française de développement personnel** aidant les gens à comprendre les **grandes périodes de leur vie**. L'astrologie devient le moteur de calcul invisible. Concurrents : Headspace, Petit Bambou, The Pattern, coachs de vie, livres de développement personnel.

**Vocabulaire à bannir** : destin, magie, prédiction, voyance, pouvoirs, révélations.
**Vocabulaire cible** : périodes, cycles, compréhension, évolution, réflexion, décisions, équilibre, chemin, confiance, moments clés.

**Soléna** : présence discrète (guide qui apparaît au bon moment), plus le personnage principal. Modèle Apple/Airbnb/Headspace : la marque > le porte-parole.

**Language**: French — all UI copy and agent responses.

## Design System (v3.1, 2026-08 repositionnement)
- Palette : **#0A1128** (navy profond) + **#0F1A3C** (navy standard) + **#1E2A5E** (indigo subtil) + **#B8935A** (or Hermès) + **#C9A24B** (gold accent) + **#F7F5F0** (ivoire) + **#8F6E24** (deep gold, textes sur clair)
- Typography : Playfair Display (headings, italics editorial) + Inter (body)
- Univers visuel : cosmique cinématique — lune dorée, constellations filigrane, champ d'étoiles animées procédural, textures dorées
- Zones vide, respiration, layout premium (Apple/Hermès)

## What's implemented
### Sécurité (2026-02-08 — SEC-001/002/003)
- **SEC-001** — `/api/plume-chat` et `/api/plume-chat/stream` : auth JWT requise + `charge_or_premium('chat_astral', ...)` AVANT tout appel LLM → impossible de bypasser la déduction crédits (401 sans token, 402 si solde insuffisant, HTTP 200 sinon).
- **SEC-002** — `services/wallet_service.py` : verrou `asyncio.Lock` par `user_id` autour de `deduct_credits`, `add_credits`, `deduct_chat_or_credits`, `add_chat_credits`, `redeem_promo`, `mark_free_tarot_used`. Nouveau helper atomique `claim_free_tarot(user_id)` (check+mark dans le même verrou) → `/api/credits/use` (tarot_oui_non) refactorisé. Tests pytest de concurrence (`tests/test_wallet_race_condition.py`) : 20 déductions concurrentes → 8 succès + 12 refus 402, jamais de double-spend.
- **SEC-003** — `GET /api/plume-chat/history/{session_id}` : `Depends(get_current_user)` + `get_session_history(session_id, user_id)` filtre systématiquement par `user_id` → impossible de lire l'historique d'un autre utilisateur.

### Repositionnement (2026-08-13)
- **CinematicHero.js** — nouveau hero cinématique : fond bleu nuit profond radial, canvas starfield animé (90 étoiles twinkle), lune dorée qui monte, constellations SVG en filigrane, H1 « Comprendre les périodes de votre vie. », CTA « Découvrir mon parcours »
- **SolenaGuideCard.js** — apparition douce au scroll (IntersectionObserver), petit avatar circulaire, « Bonjour, je suis Soléna. Je serai votre guide tout au long de votre parcours. »
- **PremiumPillars.js** — 4 cartes premium (Cycles / Relations / Décisions / Évolution), chacune pointant vers `/decouvrir?theme=...`
- **Decouvrir.js** — nouvelle page `/decouvrir` : questionnaire situation-first 6 choix, mapping intelligent → recommandation produit, apparition émotionnelle de Soléna en étape 2
- **6 pages produit** : H1 réécrits en langage universel (Thème Natal, Kabbale, Astrocartographie, Karma & Destin, Numérologie, Synastrie) — bannit destin/magie/prédiction, adopte périodes/cycles/comprendre

### Historique (voir sections suivantes pour détails)
- V3 visual rollout on 7 PDF sales pages (unified `SalesPageV3`)
- Unified `NavbarV2` (mega menu Services) + `FooterV2`
- `LiveConstellation` (dynamic zodiac by date) + `CelestialBackdrop` site-wide
- `ApercuLectureModal` (email capture, 10% MERCI10) via `/api/apercu/discount`
- `GiftModal` (Offrir) via `/api/gift/reserve` (Resend emails)
- Removed dormant Roman/Livre PDF logic
- **[2026-02-08] Credits Info strategy**:
  - `CreditsInfoModal.js` (modal + shared content) fully implemented
  - `/credits` page (`CreditsInfo.js`) using `PsPageShell` + shared `CreditsInfoContent`
  - "?" HelpCircle wiring on ChatIA quota badge + MonCompte credit banner + MonCompte credits tab
  - Footer link "Comprendre les crédits" → `/credits`
- **[2026-02-08] Admin PDF Test analytics + tier=ultra** (iteration 74 — 14/14 backend + 5/5 frontend + self-verified):
  - Fixed React Hooks violation in `/app/frontend/src/pages/AdminPdfTest.js` (moved `useState`/`useCallback`/`useEffect` above the auth-gate early returns)
  - MongoDB analytics collection `admin_pdf_test_logs` stores {admin_email, product, first_name, partner_name, tier, pdf_size, ip, created_at} on every generation
  - `GET /api/admin/pdf-test/_logs/recent?limit=N` returns `{ logs, stats, total }` with per-product aggregate counts (admin-only)
  - Admin dashboard displays live analytics widget with product stat chips + recent logs table (product, destinataire, tier, size, date)
  - `tier=ultra` toggle on Thème Natal generates the FULL Prestige Book (86 pages / ~32 MB vs 13 pages / ~10 MB in flash) — mock `book_data` now includes `_source='gpt'`, `_em` with element+modality counts, complete `acte3_chapters` (5 chapters × 10 blocks each), `dedication`, `element_analysis`, `modality_analysis`, `trio_synthesis`, aspect headers, and 12 house bodies
  - Fixed missing `book_data` kwarg pass-through in `_fixture()` → `build_natal_pdf_v2(..., book_data=...)`
- **[2026-02-08] GSC verification + Interactive Flipbook** (self-verified):
  - Google Search Console verification enabled TWO ways (redundant, safest) : meta tag `_HIsHjWgL61kcCdFBHvhPT4p3PE8AqPnADtRj42Sha8` in `public/index.html` + HTML file `public/google20ef3e9042a818bc.html`
  - New backend endpoints `GET /api/pdf-preview/{product}/pages/meta` and `GET /api/pdf-preview/{product}/page/{n}.jpg` — rasterise the 3-page PDF preview to 150 DPI JPEGs via `pdf2image` (poppler), cached in-memory per product
  - New React component `PdfFlipbook.jsx` — CSS 3D `perspective` + `rotateY` animation for realistic page-flip, keyboard nav (← → esc), preload of adjacent pages, close overlay
  - New "Feuilleter le livre" button on each `/livres` card opens the flipbook modal — verified end-to-end via screenshot on theme-natal (page 1 cover → page 2 sommaire)
- **[2026-02-08] V3 Services & Legacy migration** (iteration 68 — 100% frontend passed):
  - `PsPageShell background="light"` désormais expose la palette V3 via CSS variables
  - `TirageTarot`, `ChatIA`, `Horoscope`, `Choix`, `MonCompte` migrés en cream V3 + Playfair Display
  - Scoped overrides `[data-shell="light"]` dans `index.css` pour `card-mystical`, `btn-mystical`, `plume-glass`
  - `BundleCard` refondu palette V3 (navy/or sur blanc)
- **[2026-02-08] Admin PDF test sécurisé + Thème Natal double-passe** (iteration 73 — 100% backend 14/14 + frontend 3/3):
  - `/api/admin/pdf-test/{product}` protégé par `Depends(require_admin)` (Supabase JWT + profiles.is_admin) → 401/403 sans token admin
  - Frontend `/admin/pdf-test` : triple-gate (spinner loading → redirect /connexion si anonyme → 'Accès réservé' si non-admin → dashboard complet), fetch(Bearer) pour ouvrir chaque PDF en blob
  - `natal_pdf_v2.py` refactorisé avec `_build_story(page_map)` closure + `chapter_marker` aux 6 diviseurs de partie + `build_with_toc` 2-pass → TOC affiche vrais numéros de page pour les 6 parties du livre
  - `pdf_book_pages.table_of_contents_page` accepte désormais `page` sur chaque entry avec feuillet pointillé doré vers numéro de page
  - Tests pytest ajoutés : `/app/backend/tests/test_admin_pdf_security.py`

- **[2026-02-08] Double-passe généralisé + Synastrie personnalisée + admin PDF test** (iteration 72):
  - `build_with_toc` (double-passe) appliqué à **Kabbale**, **Karma Destin**, **Numérologie** → sommaires affichent maintenant les vrais numéros de page (I·3, II·5, III·7…)
  - Synastrie : `_page_01_cover` refondu, deux prénoms en dorure gaufrée façon livre imprimé — filet + "ÉDITION PERSONNELLE POUR" + PRÉNOM 1 letter-spacé en or vif + "&" + PRÉNOM 2 + filet
  - Nouveau endpoint admin `GET /api/admin/pdf-test/{product}?first_name=X&partner_name=Y` (data factices réalistes, pas de cache, pas de crédits débités)
  - Nouvelle page `/admin/pdf-test` (`AdminPdfTest.js`) : dashboard V3 avec inputs prénom/partenaire + 6 cards produits + boutons OUVRIR/DL. Bannière rouge "ADMIN INTERNE"
  - Note review : endpoint volontairement non-auth (interne dev). À protéger par `is_admin` avant expo publique

- **[2026-02-08] Cover personnalisée + TOC double-passe + landing /livres** (iteration 71):
  - `services/pdf_cover_personalization.py` : helper `embossed_name` (dorure gaufrée façon livre imprimé — filet doré + "ÉDITION PERSONNELLE" + prénom letter-spacé en or vif) intégré dans Kabbale, Karma Destin, Numérologie, Astrocarto, Thème Natal
  - `services/pdf_multipass_toc.py` : `ChapterMarker` (flowable invisible) + `build_with_toc()` fonction 2-passes (dry-run tracking + rebuild) → Astrocarto affiche maintenant les vrais numéros de page dans le sommaire
  - Nouvelle page `/livres` (`LivresLanding.js`) : landing V3 des 6 rapports prestige (Astrocarto, Kabbale, Karma Destin, Numérologie, Thème Natal, Synastrie) avec cover thumbnails, prix, bouton "Aperçu 3 pages gratuit" + CTA "Découvrir" → page produit
  - Mount `/api/assets/pdf_covers/*` en StaticFiles pour servir les 6 PNG covers au frontend
  - Nouveau footer link "Nos livres prestige" → `/livres` (aux côtés de "Comprendre les crédits")

- **[2026-02-08] TOC + illustrations hero + PDF preview** (iteration 70 — backend 100% 7/7, frontend 100% 6/6):
  - Nouveau `services/pdf_hero_illustrations.py` : 5 illustrations SVG signature (tree_of_life, karmic_nodes, entwined_hearts, natal_wheel, life_path)
  - Nouveau `services/pdf_book_intro.py` : `svg_to_png` + `render_hero_image` helpers
  - 6 PNGs générés dans `/app/backend/assets/pdf_covers/` (astrocarto + 5 hero illustrations)
  - Kabbale, Karma Destin, Numérologie : TOC (`toc_page`) + chapter openers romans (`chapter_opener` I..VII) + hero PNG en couverture
  - Thème Natal (via `pdf_luxury_theme.cover_page`) : fallback local `natal_hero.png` (garanti même sans réseau)
  - Synastrie (`_bg_cover`) : fallback local `synastrie_hero.png`
  - Nouveau endpoint public `GET /api/pdf-preview/{product}` (cache mémoire) : PDF 3 pages téléchargeable (couverture + sommaire + chapter I + intro)
  - Nouveau `components/PdfPreviewButton.js` avec prop `previewProduct` sur `SalesPageV3` → 6 pages produits affichent le bouton "Aperçu 3 pages gratuit"

- **[2026-02-08] PDF prestige unifié** (iteration 69-70):
  - Nouveau module `services/pdf_prestige.py` : `prestige_bg`, `ornament`, `chapter_opener` (numérotation romaine I-VII), `toc_page` (sommaire éditorial), `simple_world_map_svg` (fallback carte du monde)
  - `services/pdf_bg.make_bg_canvas()` upgradé : cadre or pointillé + soleil ornemental + footer éditorial "PLUME ASTRALE · PRODUCT — n —" → propage à Karma Destin + Numérologie
  - `Kabbale` : `_bg_canvas` redirige vers `pdf_bg.make_bg_canvas('Ton Arbre de Vie')`
  - `Synastrie` : `_bg_cream` ajoute cadre or pointillé + soleil + footer éditorial
  - `Thème Natal luxury_bg` : cadre or pointillé + soleil ornemental + footer éditorial
  - `Astrocartographie PDF` : sommaire (I-VII) + chapter openers numérotés + carte du monde de secours embarquée (garantit une belle carte à chaque livre imprimé)

- **[2026-02-08] Astrocarto + V3 children + /services/ rebranding** (iteration 69 — 100% frontend passed):
  - `AstroCartoHero.js` : nouveau visuel SVG (carte du monde stylisée + 7 lignes planétaires + 3 villes + boussole) remplaçant la planète Uranus sur `/astrocartographie`
  - `SalesPageV3` accepte désormais `heroNode` (ReactNode) en plus de `heroImage`
  - NatalCompletionPrompt, TransitsToday, ReferralPanel, CreditsPaywallModal → palette V3 (Playfair, #C9A24B, navy)
  - Routes canoniques `/services/*` (16 routes) avec redirections legacy `/outils/*` conservées

## Backlog

### P1 — DONE (iteration 68)
- ~~Refactor `TirageTarot.js`, `ChatIA.js`, `Horoscope.js`, `Choix.js`, `MonCompte.js` with `PsPageShell` + paper textures + Playfair/Inter~~ ✅
- Replace lingering "Outils" strings with "Services" (route paths kept as `/outils/*` for backward compat)

### P2 — Polish
- Audit remaining hardcoded dark palette references in child components (NatalCompletionPrompt, TransitsToday, ReferralPanel, NatalEssentials, CreditsPaywallModal etc.) inside light-shell pages
- Fully migrate the remaining chat bubbles interior (avatar tags, cost reminder) if visual polish desired

### P3 — Future
- Generate real PDF gift vouchers (Resend currently emails checkout link only)
- Mini-lecture personnalisée gratuite on birthdays
- Validate GSC in production

## Key API Endpoints
- `POST /api/gift/reserve` — Resend gift email
- `POST /api/apercu/discount` — 10% discount email
- `POST /api/contact` — Contact form
- `POST /api/credits/use` — Deduct credits
- `POST /api/credits/promo` — Redeem code
- `GET /api/plume-chat/history/{sid}` — Chat history

## Data Models (Supabase)
- `profiles` : {id, email, credits, cercle_tier, metadata}
- `journal_email_logs` : {id, user_id, email, sent_date, variant}

## Integrations
- OpenAI GPT-5 / Sora 2 / TTS (via Emergent LLM Key)
- Astrology-API.io v3
- Supabase (auth + DB)
- Stripe (checkout)
- Resend (transactional emails)

## Credentials (test)
- Admin : `admin@plume-astrale.fr` / `PlumeAdmin2026`
- Test user : `test@plume-astrale.fr` / `TestPlume2026!`

## Credits Pricing (backend/config.py)
- `chat_astral` : 10 cr / question
- `lecture_tarot` : 10 cr / tirage
- `tarot_marseille` / `tarot_celtique` / `tarologie` : 30 cr
- `numerologie` : 30 cr
- `lecture_astrologique` : 40 cr
- `theme_natal_pdf` : 30 cr (flash 5-page)
- `cartographie` / `synastrie` / `revolution_solaire` / `karma_destin` : 60 cr

## Packs
- Comète : 30 cr — 7,99€
- Nébuleuse : 80 cr — 17,99€ (badge "Le plus choisi")
- Constellation : 180 cr — 34,99€ (badge "Meilleure valeur")
- Voie Lactée : 350 cr — 59,99€
