# Plume Astrale — PRD

## Original Problem Statement
Massive UX/UI refactoring for the premium astrology SaaS "Plume Astrale" toward an elegant, literary, celestial aesthetic. Unify visual identity (Navy #0F1A3C, Gold #C9A24B, Cream #F7F5F0), migrate legacy pages to V3 template, improve sales conversion (Aperçu preview modal + email capture with MERCI10 discount), add "Offrir" (gift) option to product pages, clarify Credits value proposition. Rename "Outils" → "Services" site-wide.

**Language**: French — all UI copy and agent responses.

## Design System (V3)
- Palette : #0F1A3C (Navy), #C9A24B (Gold), #F7F5F0 (Cream), #232323 (Anthracite)
- Typography : Playfair Display (headings) + Inter (body)
- Paper textures via `feTurbulence` SVG on light backgrounds
- Celestial backdrops + LiveConstellation (auto-zodiac) on dark backgrounds

## What's implemented
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
