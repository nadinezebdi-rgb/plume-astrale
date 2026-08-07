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

## Backlog

### P1 — V3 Migration of Services Pages
- Refactor `TirageTarot.js`, `ChatIA.js`, `Horoscope.js` with `PsPageShell` + paper textures + Playfair/Inter
- Replace lingering "Outils" strings with "Services"

### P2 — Legacy cleanup
- Migrate `Choix.js` and `MonCompte.js` to V3 light theme

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
