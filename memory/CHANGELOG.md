# CHANGELOG - Plume Astrale

## 2026-02-09

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
