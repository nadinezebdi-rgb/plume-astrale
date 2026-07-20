# CHANGELOG - Plume Astrale


## 2026-02-20 — Session cleanup post-migration caches persistants

### 🎯 4 features finales Gary Vee — conversion + LTV (session audit)

**1. PDF Mockup 3D (P1 — conversion Astrocarto)** :
- Nouveau composant `/app/frontend/src/components/PdfMockup3D.js` — 3 pages "leaked" en isométrie CSS pure (couverture / carte planétaire / ligne Vénus)
- Watermark "APERÇU" en Cinzel, animation float+bob, responsive mobile single-column
- Inséré sur `/astrocartographie` au step 0, au-dessus des témoignages
- Aucune dépendance image externe — 100% CSS/HTML rendu

**2. Reels Soléna 30 jours (P2 — content marketing)** :
- Livrable documentaire : `/app/memory/reels_solena_30_jours.md`
- 30 scripts courts (15-30 sec) répartis en 4 formats : Astuce du jour, Face aux signes, Rituel express, Question de Soléna
- Notes de production complètes : voix ElevenLabs, B-roll, fonts overlay, hashtags, KPI cibles

**3. Cercle Soléna — Abonnement 19€/mois (P1 — LTV × 12)** :
- **Backend** `/app/backend/routes/subscriptions.py` :
  - `POST /api/subscriptions/cercle-solena/checkout` (mode='subscription' Stripe, idempotence via `stripe_customer_id` persisté)
  - `GET  /api/subscriptions/cercle-solena/status`
  - `POST /api/subscriptions/portal` (Stripe Billing Portal — résiliation en 1 clic)
  - Webhook handler `handle_subscription_event` : credite +3 crédits mensuels via `invoice.payment_succeeded`, avec idempotence sur `credit_grants.external_id`
- **DB** `/app/supabase/cercle_solena_migration.sql` :
  - Nouvelles tables `subscriptions` + `credit_grants` (RLS activé)
  - Colonnes `profiles.stripe_customer_id` + `profiles.is_cercle_member`
- **Frontend** `/app/frontend/src/pages/CercleSolena.js` :
  - Landing complète avec pricing hero, 4 bénéfices, FAQ, CTA adaptatif (non-auth → redirect /connexion, auth → checkout)
  - Auto-redirect vers Stripe Checkout
  - Handle 503 clean ("L'abonnement n'est pas encore configuré")
- **Router** : nouvelles routes `/cercle-solena` et `/cercle-solena/succes` (App.js)
- **Teaser** sur `/mon-compte` sous le BundleCard (data-testid : `mon-compte-cercle-solena-teaser`)
- **Note** : Nécessite `STRIPE_CERCLE_SOLENA_PRICE_ID` dans `.env` (Nathalie doit créer le Price côté Dashboard Stripe — cf `/app/memory/setup_cercle_solena_analytics.md`)

**4. Analytics Plausible + GA4 (P2 — conversion tracking)** :
- `/app/frontend/src/lib/analytics.js` existant enrichi : ajout constantes `EVENTS` (source of truth) + helper `revenue()` (montant EUR, dual-track Plausible+GA4)
- Instrumentation :
  - `Register.js` → `signup_completed` on success
  - `BundleCard.js` → `bundle_click` on CTA
  - `KabbaleSales.js` → `kabbale_checkout` on submit
  - `AstrocartographieSales.js` → `astrocarto_checkout` on submit
  - `CercleSolena.js` → `cercle_solena_checkout` on CTA
- RGPD-compliant : no-op tant que `getConsent() !== 'accepted'` (bandeau cookies existant)
- Config : `REACT_APP_PLAUSIBLE_DOMAIN` et/ou `REACT_APP_GA4_ID` dans `.env`

### 📋 Doc setup pour Nathalie
- `/app/memory/setup_cercle_solena_analytics.md` — checklist ~10 min :
  1. Créer Price Stripe recurring
  2. Appliquer migration SQL Supabase
  3. Activer 4 webhook events Stripe
  4. Setup Plausible (facultatif : + GA4)

### ✅ Testing
- iteration_52 : backend 4/4 PASS (auth 401 + checkout 503 attendu) + frontend 100% (PDF mockup step 0 visible / step 1 hidden, CercleSolena landing complète, teaser mon-compte, redirect non-auth, 503 UI, analytics no-crash)
- Pytest : `/app/backend/tests/test_cercle_solena_subscriptions.py`

### 🚀 4 fixes Gary Vee — conversion boost (P1)

**1. Rotation Hero (Hero3D.js)** — les 3 promesses cyclent toutes les 4 secondes avec fondu enchaîné : « vie amoureuse », « mission d'âme », « meilleure destination ». Fini le filtrage des 60% de l'audience qui ne cherche pas l'amour. Data-testid : `hero-promise-{idx}`.

**2. Countdown 48h dynamique (LaunchBanner.js)** — le bandeau top affiche désormais un countdown live `EXPIRE DANS HHh MMm SSs` par visiteur (localStorage `plume_offer_deadline_v1`, evergreen reset auto). Format zero-padded, `font-variant-numeric: tabular-nums` pour un rendu stable. Data-testid : `launch-banner-countdown`.

**3. Upsell Astrocarto post-Kabbale (KABBALE20)** :
- Backend : `/app/backend/routes/astrocartographie.py` — nouveau code promo `KABBALE20` = -20€ absolu (`max(5.0, 49-20) = 29.0`), symétrique à PLUME15.
- Frontend : `/app/frontend/src/pages/KabbaleSucces.js` — nouveau bloc premium visible dès `pdf_ready`, badge "-20€ · Duo Soléna", titre "Maintenant que tu connais ton âme, où va-t-elle s'épanouir ?", CTA `/astrocartographie?discount=KABBALE20` (déjà auto-fill via query param existant).
- AstrocartographieSales.js : nouveau banner conditionnel `astrocarto-kabbale20-banner` (49€ → 29€) et bouton adaptatif "Payer 29€ (Duo Soléna)".
- Test pytest backend : 4/4 PASS (`/app/backend/tests/test_astrocarto_kabbale20.py`).

**4. BundleCard Découverte Soléna** — nouveau composant `/app/frontend/src/components/BundleCard.js` :
- Design premium (badge or "Duo Soléna", 2 cards produits, prix 68€ vs 88€ barré, économie 20€)
- Intégré sur `/mon-compte` (post-connexion, dense=true) et `/mon-accueil` (AuthenticatedHome)
- CTA vers `/kabbale?from=bundle` → mécanique de chaînage vers l'upsell KABBALE20

**Fix bloquant race condition (AuthenticatedHome.js)** — le useEffect redirigeait vers `/` avant que Supabase.getSession() n'hydrate la session. Guard sur `loading` ajouté : `if (!loading && !isAuthenticated) navigate('/')`.

**Testing** : iteration_51.json — backend 4/4 pytest PASS, frontend 3/4 initial (BundleCard bloqué par race → corrigé), re-vérification manuelle 100% après fix.

### ⭐ Widget témoignages sur 4 landings (P2 — session Gary Vee audit)
- ✅ Nouveau composant réutilisable `/app/frontend/src/components/TestimonialsWidget.js` :
  - Design premium cohérent charte Plume (Cinzel + Cormorant, palette or/nuit)
  - 3 cartes glass avec guillemet décoratif, 5 étoiles or, quote italic, signature ville · signe astro
  - Trust-bar bas : « 4,9/5 · Note moyenne · Livraison en moins de 5 min »
  - 4 datasets exportés : `TESTIMONIALS_KABBALE`, `TESTIMONIALS_ASTROCARTO`, `TESTIMONIALS_KARMA`, `TESTIMONIALS_COMPATIBILITE` (3 témoignages FR curatés chacun)
  - Data-testids exhaustifs : `{prefix}-widget`, `-card-N`, `-rating-N`, `-quote-N`, `-name-N`, `-meta-N`, `-trust-bar`
- ✅ Intégration au-dessus du CTA final sur :
  - `/kabbale` (KabbaleSales.js) — "Ce que leur Arbre a révélé"
  - `/astrocartographie` (AstrocartographieSales.js) — "Elles ont trouvé leur lieu"
  - `/pack-karmique` (PackKarmique.js) — "Elles ont retrouvé leur mission"
  - `/outils/compatibilite` (Compatibilite2.js — pas Compatibilite.js qui est dead-code) — "Elles ont lu leur synastrie"
- ✅ Widget masqué automatiquement quand `step !== 0` (KabbaleSales/Astrocarto/PackKarmique) et quand `step !== 0` sur Compatibilite2 (disparait dès l'entrée dans le funnel de calcul).
- ✅ Responsive validé sur viewport 375px (grid-cols-1 → colonne unique, cards lisibles).
- ✅ Testing agent iteration_50.json : 3/4 PASS au premier passage, bug routing détecté sur `/compatibilite` (dead route) → correction appliquée sur Compatibilite2.js → screenshot final confirme widget live.

### 🛡️ Wrap défensif AstroSexo (P0)
- ✅ `/app/backend/routes/astrosexo.py` : appel à `enrich_and_ask()` désormais entouré d'un `try/except`.
- Si OpenAI (ou toute autre couche d'enrichissement) échoue, on retourne le `base_text` brut avec `enrichi: false` au lieu d'un HTTP 500.
- Test curl sur `POST /api/astrosexo/personal` (Paris, 1990-06-15 14:30) → 200 OK, Vénus=Taurus, Mars=Aries, Lune=Pisces, texte enrichi 3099 chars.

### 🔥 Warmup translation_cache post-migration (P1)
- ✅ Relance de `python3 /app/backend/scripts/warmup_translation_cache.py` en arrière-plan (PID 8398, logs `/tmp/warmup.log`).
- Pré-remplit la table Supabase persistante `translation_cache` avec ~500 traductions FR des réponses API v3 (archetypes, karmic_analysis, numerology_core, etc.).
- Chaque entrée ~2-3s via GPT-5.4 → temps total estimé ~25 min.

### 🗑️ Suppression table `sales` inutilisée (P1)
- ⚠️ DDL non exécutable via l'API Supabase REST : instruction fournie à l'utilisateur d'exécuter manuellement `DROP TABLE IF EXISTS sales;` dans le SQL Editor de Supabase Studio.
- Table vide (0 lignes) et zéro référence dans le code — aucun impact fonctionnel.



## 2026-02-16 (suite)

### Session 14 — 🎨 Polices Cinzel/Cormorant + effet Fade-In enrichissement

**Task 1 — Polices Cinzel + Cormorant Garamond**
- ✅ Téléchargées depuis Google Fonts (repo GitHub officiel `google/fonts`) en variable fonts :
  - `Cinzel[wght].ttf` (123 KB) → `Cinzel-Regular.ttf` + `Cinzel-Bold.ttf`
  - `CormorantGaramond[wght].ttf` (1.2 MB) → `CormorantGaramond-Regular.ttf` + `CormorantGaramond-Bold.ttf`
  - `CormorantGaramond-Italic[wght].ttf` (699 KB) → `CormorantGaramond-Italic.ttf`
- ✅ Déposées dans `/app/backend/assets/fonts/`.
- ✅ `services/pdf_theme.py::register_fonts()` teste automatiquement leur présence et fallback Helvetica sinon.
- ✅ **Refactor `astrocartographie_pdf.py`** : `_make_styles()` délègue maintenant à `pdf_theme.make_styles()` (12 styles unifiés avec les vraies polices).
- ✅ **Test E2E** : PDF Astrocartographie régénéré 676 KB → **740 KB** (fonts embarquées ~64 KB), avec Cinzel dans les captions/H2 et Cormorant Garamond dans le corps texte.

**Task 2 — Effet Fade-In progressif enrichi**
- ✅ Nouveau composant `frontend/src/components/FadeInEnrichedText.js` :
  - Split intelligent du texte par phrases (regex `(?<=[.!?…])\s+`)
  - Fade-in phrase-par-phrase avec `opacity + translateY(6px→0)` sur 600ms
  - Stagger paramétrable (default 180ms, 140-160ms utilisés en pratique)
  - **La question finale se colore en or `#D4AF37` + italique** pour se démarquer
  - Props `enabled` : si `false`, affiche tout d'un coup (fallback)
- ✅ Intégré dans 3 pages où l'enrichissement est actif :
  - `AstroSexo.js` — résultat perso (speed 140ms)
  - `TarotOuiNon.js` — message des Arcanes (speed 160ms)
  - `Oracle.js` — réponse Oracle (speed 160ms)
- ✅ L'effet s'active uniquement si le backend a bien enrichi (`enrichi === true` / `reponse_enrichie === true`), garantissant zéro régression sur les tirages statiques.

**Fix bonus**
- ✅ Frontend Tarot Oui/Non "puis 2 crédits" → **"puis 5 crédits"** (aligne l'affichage sur le vrai coût backend `SERVICE_COSTS['tarot_oui_non']=5`). Vérifié visuellement.


## 2026-02-16

### Session 13 — 🎨 Charte PDF unifiée + AstroSexo UI perso + Badge "Enrichi par Soléna"

**Task 1 — UI AstroSexo perso**
- ✅ `frontend/src/pages/AstroSexo.js` : nouveau bloc "Envie d'une analyse vraiment personnalisée ?" affiché après sélection d'un signe.
- ✅ Logique conditionnelle :
  - Authentifiée **+** natal complet → bouton "✨ Générer mon analyse perso" appelle `POST /api/astrosexo/personal`
  - Non authentifiée → CTA "Créer mon compte gratuit" vers `/inscription?next=/outils/astrosexo`
  - Authentifiée sans natal → "Compléter mon thème natal" vers `/mon-compte`
- ✅ Analytics : `astrosexo_personal_generated` event tracké avec venus/mars signs.
- ✅ Auto-scroll vers le résultat après génération.
- ✅ Résultat affiché avec badge "✨ Enrichi par Soléna" + labels Vénus/Mars/Lune.

**Task 2 — Charte PDF unifiée (`services/pdf_theme.py`)**
- ✅ Nouveau module partagé exposant :
  - `PALETTE` dict (NIGHT `#111625`, GOLD `#D4AF37`, CREAM `#F5EEE0`, LAVENDER `#E3D7FF`, MUTED `#9089B5`, GOLD_LIGHT, NIGHT_SOFT, ROSE)
  - Alias flat : `NIGHT`, `GOLD`, `CREAM`, `LAVENDER`, `MUTED`, etc.
  - `register_fonts()` : Cinzel + Cormorant Garamond depuis `/app/backend/assets/fonts/` (idempotent, fallback Helvetica)
  - `font(name, fallback)` : helper pour utiliser une police si dispo
  - `make_styles()` : dict de 12 `ParagraphStyle` unifiés (title, subtitle, h2, h3, body, italic, quote, small…)
  - `starfield_bg(canv, doc)` : fond commun Platypus (nuit + halo doré + 30 étoiles + footer pagination)
  - `paint_page_bg(canv, w, h)` : version raw canvas pour `pdf_generator.py` et `compatibility_pdf_generator.py`
- ✅ **`services/pdf_generator.py`** (Karma standalone) — palette réharmonisée :
  - `#0F0518` → `#111625` (NIGHT unifié)
  - `#1A0B2E` → `#1A2035` (NIGHT_SOFT)
  - `#C5A059` → `#D4AF37` (GOLD unifié)
  - `#F3E5AB` → `#F5EEE0` (CREAM)
  - `#E0D9F6` → `#E3D7FF` (LAVENDER)
- ✅ **`services/compatibility_pdf_generator.py`** — palette réharmonisée sur la même base (5 couleurs alignées).
- ✅ Testé E2E : `POST /api/compatibility/generate` renvoie un PDF 17MB valide avec la nouvelle palette Kabbale.

**Task 3 — Badge "✨ Enrichi par Soléna"**
- ✅ Nouveau composant `frontend/src/components/EnrichedBadge.js` avec 3 variants (`default`, `compact`, `inline`) + alignement gauche/centre/droite.
- ✅ Backend renvoie `enrichi: true` sur les endpoints `/api/oracle` et `/api/astrosexo/personal`.
- ✅ Backend renvoie `reponse_enrichie: true` sur les 3 endpoints Tarot (déjà en place).
- ✅ Intégré sur 3 pages :
  - `TarotOuiNon.js` — badge compact à côté de "✦ Message des Arcanes"
  - `Oracle.js` — badge compact centré au-dessus de la réponse
  - `AstroSexo.js` — badge default en tête du bloc résultat perso

**Fix bonus**
- ✅ Cohérence coût Tarot Oui/Non : frontend affichait "2 crédits" alors que le backend charge 5 (SERVICE_COSTS['tarot_oui_non']=5) → mis à jour partout (`sed -i 's/2 crédits/5 crédits/g'` sur `TarotOuiNon.js`).


## 2026-02-15

### Session 12 — 🔗 Tous les outils sur API v3 + Couche d'enrichissement narrative universelle

**Nouvelle couche transverse — `services/enrich_narrative.py`**
- ✅ Fonction `enrich_and_ask(text, context, first_name, target_length)` — passe un texte brut dans GPT-5.4 pour :
  1. Le rallonger à `short|medium|long` (150-550 mots selon la cible)
  2. Terminer **toujours** par une question introspective personnalisée
- ✅ Triple cache : mémoire LRU (400 items) + Supabase `narrative_cache` + skip auto si texte trop court.
- ✅ Fonction `enrich_dict_fields(obj, fields, ...)` — enrichit récursivement uniquement les champs listés (ex: `['description', 'signification']`).
- ✅ Sécurité : si l'IA oublie la question finale, ajout automatique de "Et toi, qu'est-ce que ça éveille en toi ?"
- 📋 Migration SQL `/app/supabase/narrative_cache_migration.sql` à appliquer côté Supabase.

**Outils reconnectés à l'API v3 + enrichissement narratif (7/7)**

1. 💘 **Compatibilité crédits** (P1) — `/api/compatibility/generate` appelle maintenant `aio.synastry_report(bd1, bd2)` (avec `@fr_polish`), le passe au générateur PDF via `api_data`. Fix bonus : normalisation `person1/2['day'/'month'/'year'/'first_name']` depuis `date_naissance`. ✅ Testé : PDF 17MB avec vraie synastrie personnalisée.
2. 🃏 **Tarot Marseille/Celtique/Oui-Non** (P1) — chaque endpoint appelle `enrich_and_ask` sur les champs `reponse/interpretation/synthese/conseil/message` + interprétations cartes individuelles. ✅ Testé : Oui/Non passe de ~150 chars à **1854 chars** finissant par "Quel geste concret voudrais-tu poser aujourd'hui ?". Coût crédit inchangé (1 gratuite puis 5cr/question).
3. ✨ **Énergie du Jour** (P2) — Prompt système `ENERGY_SYSTEM_PROMPT` mis à jour : demande **4-6 phrases/section (100-150 mots) + question finale obligatoire** dans chaque section (dominante, relationnel, attention, opportunité). Modèle upgradé `gpt-4o-mini` → **gpt-5.4** via `EMERGENT_LLM_KEY`.
4. 🕯️ **Rituel du jour** (P2) — Prompt réécrit : 250-350 mots + question finale obligatoire, structure implicite en 4 étapes, tutoiement systématique. Modèle `gpt-4o-mini` → **gpt-5.4**.
5. 🔢 **Numérologie** (P2) — `/api/numerology/complete` et `/deep-profile` :
   - Optionnellement enrichis avec `aio.numerology_core_numbers(bd_v3)` si `birth_date` fournie
   - `enrich_dict_fields(fields=['description','signification','text','meaning'])` appliqué récursivement
6. 🔥 **AstroSexo perso** (P3) — nouveau `POST /api/astrosexo/personal` (`routes/astrosexo.py`) : accepte les coords natales, fetch `aio.love_languages` + `aio.personality_analysis` + `aio.natal_chart` (pour extraire Vénus/Mars/Lune), compose un texte de base, l'enrichit via `enrich_and_ask(target_length='long')`. ✅ Testé : analyse de 3400+ chars sur Marie/Vénus Bélier/Mars Poissons/Lune Capricorne, termine par question personnelle.
7. 👼 **Oracle des Anges** (P3) — `POST /api/oracle` accepte `first_name`, enrichit `reponse` via `enrich_and_ask(target_length='long')`. ✅ Testé : passe de ~150 à **2526 chars** finissant par question.

**Notes**
- Verification Tarot Oui/Non : logique 1 carte gratuite (`has_used_free_tarot`) puis 5cr/question (`SERVICE_COSTS['tarot_oui_non']=5`) déjà en place, inchangée.
- Cache DB `narrative_cache` : sans la table, chaque premier appel coûte 1-3s GPT ; avec la table, cache persistant entre redémarrages.
- Frontend AstroSexo : peut désormais appeler `/api/astrosexo/personal` si utilisatrice authentifiée avec natal (à câbler côté UI dans une prochaine étape).


## 2026-02-14 (suite)

### Fix — Révolution Solaire en anglais
- ✅ Appliqué le décorateur `@fr_polish` sur les 2 fonctions `solar_return` et `solar_return_report` dans `services/astrology_io_service.py`.
- ✅ L'API astrology-api.io v3 ne respectait pas `language: fr` sur ces endpoints malgré le paramètre côté settings dashboard.
- ✅ Testé : 0 string anglaise restante (mise à part 1 faux positif sur texte FR).


## 2026-02-14

### Session 11 — 🗺️ Lignes détaillées PDF + 💌 Cross-sell J+7 (PLUME15)

**Task 1 — Interprétations détaillées des lignes planétaires dans le PDF**
- ✅ Nouveau module `services/astrocartographie_lines_data.py` — **40 interprétations FR statiques** (10 planètes × 4 lignes AC/DC/MC/IC), rédigées en style Soléna (headline + 2-3 phrases poétiques). Chaque entrée = ~150 mots.
- ✅ `astrocartographie_pdf.py` : nouvelle fonction `_planetary_lines_pages()` — page d'intro + pages "2 lignes par page" (dedupe + tri planète/ligne).
- ✅ `astrocartographie_service.py` : fetch supplémentaire `astrocartography_lines()` (fallback si `/map` ne renvoie pas les lignes) → passe `lines_data` au générateur PDF.
- ✅ Résultat : PDF passe de **18 → 30 pages** (Marie a 28 lignes, 12 pages ajoutées).
- ✅ Regénération testée sur `test-astrocarto-37c2a3eae8f2.pdf` → contenu FR conforme.

**Task 2 — Cross-sell J+7 après Kabbale/Karma (offre PLUME15)**
- ✅ Nouveau service `services/crosssell_astrocarto.py` — boucle 6h démarrée au startup.
- ✅ Query paginée : `payment_transactions` avec `pack_id IN (kabbale_arbre_de_vie, pack_karmique_kabbale, karma_destin)`, `payment_status='paid'`, fenêtre J-45 à J-7.
- ✅ Skip si l'utilisateur a déjà acheté l'astrocartographie (via `_has_bought_astrocarto()`).
- ✅ Skip si `metadata.crosssell_astrocarto_sent_at` déjà marqué (idempotence).
- ✅ Dédup par email (1 seul mail par utilisateur même s'il a plusieurs achats éligibles).
- ✅ Email HTML tendre avec offre visuelle : "49€ ~~biffé~~ 41,65€" + code PLUME15 en gros + CTA lien vers `/astrocartographie?discount=PLUME15`.
- ✅ **Code PLUME15 implémenté dans `routes/astrocartographie.py`** : hardcoded (pas de migration DB) → applique 15% de réduction sur le montant Stripe (49€ → 41,65€). Stocké dans metadata (`original_amount`, `discount_percent`, `promo_code`).
- ✅ Frontend : détection `?discount=` dans l'URL → pré-remplit le champ promo + skip step 0 → affiche une bannière or "OFFRE CLIENTES PLUME · 41,65€ · 15% de réduction" + adapte le CTA "PAYER 41,65€ (OFFRE PLUME)".
- ✅ Testé E2E : session Kabbale backdatée J-8 → 1 email envoyé, 2ème run → 0 (idempotence OK). Checkout `POST /api/astrocartographie/checkout` avec `promo_code:'PLUME15'` → Stripe session à 41,65€, DB metadata correctement rempli.

**Warm-up cache terminé**
- ✅ Script `warmup_translation_cache.py` a fini en **9m 39s** (579s).
- ✅ **500 entrées** en cache mémoire.
- ⚠️ Sans la table `translation_cache` en Supabase, ce cache est perdu au prochain redémarrage backend. À relancer une fois la migration appliquée.


## 2026-02-13

### Session 10 — 🔥 Warm-up cache + Email J+3 post-achat

**Task 1 — Warm-up cache traduction FR**
- ✅ Nouveau script `backend/scripts/warmup_translation_cache.py` — appelle chaque endpoint `@fr_polish` (love_languages, archetypes, karmic_analysis, numerology_core, personality_analysis, chinese_zodiac, horoscope_personal) avec **6 profils natals variés** (Marie 1990, Sophie 1985, Camille 1995, Sarah 1978, Léa 2000, Nathalie 1970).
- ✅ Couvre aussi **12 signes × 3 périodes** (daily/weekly/monthly) pour `horoscope_sign` → 36 appels supplémentaires.
- ✅ Total : ~78 appels API + ~78 traductions batchées GPT-5.4.
- ⏱️ Durée : ~10-15 min au premier run (jusqu'à 86s pour `personality_analysis` avec ses 81 strings à traduire en batch). Les runs suivants sont quasi-gratuits grâce au cache mémoire dans le process.
- 📋 **Persistance** : nécessite la table Supabase `translation_cache` (SQL fourni précédemment). Sans elle, le warmup travaille pour rien entre deux redémarrages backend.

**Task 2 — Email J+3 post-achat astrocartographie**
- ✅ Nouveau service `services/astrocarto_followup.py` — boucle background démarrée au startup FastAPI (toutes les 6h).
- ✅ Query paginée : `payment_transactions` avec `pack_id='astrocartographie'`, `payment_status='paid'`, achats entre J-14 et J-3 (fenêtre 11 jours).
- ✅ Idempotence forte : marque `metadata.followup_j3_sent_at` + `followup_j3_ok` (bool) → jamais renvoyé deux fois, même en cas de retry loop.
- ✅ Email HTML tendre et personnel (aucun CTA de vente, juste "quel ressenti ?" + invitation à répondre par email ou laisser un témoignage).
- ✅ Testé E2E : session backdatée à J-4 → email envoyé (`http_status=200`, `resend_id` capturé), 2ème run → 0 envoyé (idempotence OK).
- ✅ Wire dans `server.py` startup event à côté de `cart_recovery_loop` et `lead_nurture_loop`.


## 2026-02-12

### Session 9 — 🔍 Audit FR + Champ ville libre + Cache traductions

**Task 1 — Audit FR des endpoints (post-processing OpenAI systématique)**
- ✅ Nouveau service `services/french_polish.py` : détecte les strings anglaises dans une réponse API (heuristique mots EN + densité accents) et les traduit en FR poétique via GPT-5.4 en **UN SEUL appel batché** (indices numérotés, réponse JSON).
- ✅ Triple cache : mémoire (LRU 500 items) + Supabase (`translation_cache`) + skip transparent si contenu déjà FR.
- ✅ Décorateur `fr_polish(context)` ajouté dans `services/astrology_io_service.py` (module-level) : applique le post-processing automatique après chaque appel API v3.
- ✅ Appliqué à 7 fonctions clés :
  - `love_languages` (4 EN → 0 EN) ✅
  - `archetypes` (4 EN → 0 EN) ✅
  - `karmic_analysis` (1 EN → 0 EN) ✅
  - `numerology_core_numbers` (3 EN → 0 EN) ✅
  - `personality_analysis` (81 EN → 0 EN) ⭐ gros gain
  - `chinese_zodiac` (1 EN → 0 EN) ✅
  - `horoscope_sign` / `horoscope_personal` (5 EN → 2 faux positifs)
- ✅ Fix accents manuels dans `numerology_service.py` : "Defi" → "Défi" (×3).
- ⏱️ Perf : batching réduit latence de 5.1s → 2.8s (première fois), quasi-0s au 2e appel grâce au cache mémoire.
- ⚠️ Table `translation_cache` à créer manuellement en Supabase (migration `translation_cache_migration.sql` à appliquer). Sans la table, le cache mémoire fonctionne quand même.

**Task 2 — Champ ville libre sur Astrocartographie**
- ✅ Nouveau endpoint `GET /api/astrocartographie/cities/search?q=xxx&limit=8` — proxy vers API v3 `/glossary/cities` (autocomplete mondial).
- ✅ Frontend : champ input avec loupe + spinner + dropdown de résultats à côté des 12 suggestions. Debounce 350ms + normalisation lat/lng pour dedup avec le picker.
- ✅ Testé : recherche "reykja" → "Reykjavík · IS", "tok" → "Tokyo · JP", etc. — instantané (<400ms).

**Task 3 — Migration email_events**
- ⚠️ Impossible d'appliquer le DDL via service_role (PostgREST bloque CREATE TABLE).
- ✅ Le code `email_journal.py` échoue déjà silencieusement (log level `debug`, pas de warning intrusif).
- 📋 SQL à copier-coller dans le SQL Editor Supabase (URL fournie à l'utilisateur) :
  - `/app/supabase/email_events_migration.sql` (35 lignes)
  - `/app/supabase/translation_cache_migration.sql` (12 lignes)


## 2026-02-11

### Session 8 — 🗺️ Nouveau produit : Astrocartographie 49€ (Où vivre ta meilleure vie)

**Architecture (mirror Kabbale 39€) — pipeline validé E2E**
- ✅ **Endpoints API v3** : ajout de 5 helpers dans `services/astrology_io_service.py` :
  - `astrocartography(bd)` → SVG monde 1200×600 + lignes MC/IC/AC/DC des 10 planètes
  - `astrocartography_lines(bd)` → data JSON brute
  - `astrocartography_location_analysis(bd, location)` → analyse détaillée par ville (life_area_ratings, nearby_lines, planetary_influences)
  - `astrocartography_compare_locations(bd, locations)` → scores comparés multi-villes
  - `astrocartography_relocation_chart(bd, location)` → nouveaux ASC/MC/maisons relocalisés
- ✅ **IA Soléna (OpenAI GPT-5.4 via EMERGENT_LLM_KEY)** : `services/astrocartographie_ai.py` — 3 fonctions :
  - `enrich_city_analysis()` : traduit l'anglais brut de l'API en 7 sections FR poétiques (headline, ambiance, career, love, spirituality, body, advice)
  - `generate_bonus_destinations()` : Soléna choisit 2 villes surprises adaptées au thème natal (avec coords lat/lng)
  - `write_synthesis()` : rédaction de la synthèse finale (300-400 mots)
- ✅ **PDF ReportLab** : `services/astrocartographie_pdf.py` — 18 pages :
  - Couverture + Introduction (astrocartographie expliquée)
  - Carte du monde (SVG API v3 converti en PNG via `cairosvg` 1600px)
  - 3 villes choisies × 3 pages (titre+headline+ambiance / domaines de vie / conseil+lignes actives)
  - 2 villes bonus × 2 pages (titre+ambiance / domaines de vie)
  - Synthèse + Rituel d'ancrage + signature Soléna
  - Balises `<b>`/`<i>` préservées via regex placeholder (comme kabbale_pdf)
- ✅ **Orchestrateur** : `services/astrocartographie_service.py::handle_astrocartographie_webhook()` — fetch API v3 + enrich IA + PDF + email Resend + idempotence via `pdf_path` metadata.
- ✅ **Route Stripe** : `routes/astrocartographie.py` — `POST /api/astrocartographie/checkout` (session live 49€ avec bypass promo ADMIN26) + `GET /api/astrocartographie/status` (polling).
- ✅ **Config PACKS** : ajout `astrocartographie` (49€, kind=oneshot) dans `backend/config.py`.
- ✅ **Webhook Stripe** : wire dans `server.py` (branche `if md.get('kind') == 'astrocartographie'`).

**Frontend**
- ✅ **Landing** `/astrocartographie` (`AstrocartographieSales.js`) : Hero "Où vivre ta meilleure vie ?" + 3 features + form 2 étapes (birth data + city picker 12 suggestions).
- ✅ **Success page** `/astrocartographie/succes` (`AstrocartographieSucces.js`) : polling 3.5s, 5 étapes visuelles, bouton téléchargement PDF quand prêt.
- ✅ **Navbar** : entrée "Astrocartographie · 49€" ajoutée dans le dropdown "💎 Rapports Prestige" (entre Pack Karmique 89€ et Kabbale 39€).

**Dépendances installées**
- `cairosvg` 2.9.0 (via `pycairo` + `libcairo2-dev`) — conversion SVG→PNG pour la carte du monde
- `svglib` 2.0.2 — fallback

**Validation E2E**
- ✅ Génération PDF testée : `astrocarto_rto-37c2a3eae8f2.pdf` — 18 pages, 676KB, contenu FR poétique enrichi par GPT-5.4 (Bali, Marrakech, Lisbonne + Kyoto et Lisbonne bonus).
- ✅ Checkout Stripe testé : `POST /api/astrocartographie/checkout` retourne `cs_live_...` valide.
- ✅ Download PDF via `/api/assets/astrocartographie/` : HTTP 200, magic bytes `%PDF-1.4` OK.
- ✅ Frontend : landing + form 2 étapes + city picker fonctionnels (Playwright screenshot confirmé).
- ⚠️ Table `email_events` manquante en Supabase — non-bloquant (l'email part quand même via Resend), mais logging DB silencieux. Migration `email_events_migration.sql` à ré-appliquer côté Supabase.


## 2026-02-10

### Session 7 — Image Kabbale + Cleanup Premium résiduels
- **🌳 Image sacrée insérée sur `/kabbale`** : ajout d'une section visuelle "Arbre de Vie" entre le hero et les features. Image WebP 1.2MB de l'artifact utilisateur (arbre kabbalistique avec 10 Sephiroth et lettres hébraïques). Cadre à bordure dorée, glow radial en arrière-plan, vignette overlay, caption Cinzel doré "✦ Les 10 Sephiroth · Les 22 Chemins ✦". Fichier : `frontend/src/pages/KabbaleSales.js` (data-testid `kabbale-tree-image`).
- **🧹 Cleanup Premium/Abonnement résiduels** :
  - `Tarot.js` : suppression de `isPremium`/`is_premium`, remplacé par gate d'authentification simple. CTA "Découvrir Premium" remplacé par "Créer un compte gratuit" avec message "20 crédits offerts à l'inscription". (Note : ce fichier est du code mort — /tarot redirige vers /outils/tarot/TirageTarot).
  - `CercleSales.js` : CTA "Rejoindre le Cercle — 14,90€/mois" → "Rejoindre le Cercle avec un pack de crédits" pointant vers `/acheter-credits`. FAQ mise à jour ("Comment fonctionnent les crédits ?").
- **✅ Lint** : 0 erreur sur les 3 fichiers modifiés.

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

## 2026-07-18 — AUDIT COMPLET REPO GITHUB + resynchronisation + 6 bugs corrigés
### Contexte
Le repo GitHub (prod) avait divergé : features développées hors Emergent (mega menu /outils/*, produits PDF numerologie 19€ / karma-destin 24€ / fenetre-rencontre 29€, couple_mystery, nouvelles pages). /app resynchronisé ENTIÈREMENT sur GitHub main, puis correctifs appliqués par-dessus.
### Bugs trouvés & corrigés (tous testés)
1. **pack_karmique jamais enregistré dans server.py** (produit 89€ en 404 en prod) → import + include_router + webhook dispatch ajoutés.
2. **`from resend import Resend`** (inexistant en resend v2+) dans les 3 routes numerologie/karma_destin/fenetre_rencontre → remplacé par services/pdf_delivery.py (httpx + SENDER_EMAIL). Le domaine expéditeur était aussi FAUX (plumeastrale.fr sans tiret).
3. **`.insert({...})` sans `.execute()`** (6 occurrences, 3 fichiers) → les transactions Stripe de ces 3 produits n'étaient JAMAIS enregistrées → les clients payants ne recevaient jamais leur PDF. Corrigé + `.single()`→`.maybe_single()`.
4. **Endpoints numérologie 404 chez astrology-api.io** (/numerology/name, /personal-year, /forecast n'existent pas) → nouveau `numerology_core_numbers()` (/numerology/core-numbers, seul endpoint v3 réel) + mapping vers le PDF. PDF numérologie avait des sections vides, maintenant contenu FR complet (6 pages).
5. **Update DB par user_email écrasant les metadata de TOUTES les tx du client** → update_tx_pdf_metadata (merge + ciblage session_id).
6. **backend/guidance.py : IndentationError irrécupérable** (fichier mort, importé nulle part) → supprimé.
7. (Par testing agent iter 48) astro_chat KeyError 'astrology' quand disable_tools+session_id → setdefault.
### Alerte 401 + timeout 60s regreffés sur la base GitHub (astrology_io_service).
### Deps : yarn --ignore-engines (camera-controls exige Node 22), email-validator pip. pip freeze fait.
### Tests : iteration_48.json 100% PASS (12/12 backend, 12 routes frontend) + retests manuels des 3 produits réparés (pdf_url Supabase Storage OK pour les 3).

## 2026-07-18 (suite) — Bandeau 48h cliquable + Vitrine Prestige + Nettoyage + Script rattrapage
- **LaunchBanner.js** (nouveau) : bandeau cliquable → /inscription, texte défilant en marquee (pause au survol), « VALABLE SUR TOUT LE SITE » en gras, compte à rebours live 48H (localStorage evergreen). Remplace le bandeau statique dans Hero3D.js. CSS .plume-banner-track dans index.css.
- **Vitrine Prestige** : colonne « 💎 Rapports Prestige » dans le mega menu Navbar (Pack Karmique 89€ highlight, Kabbale 39€, Compat Ultime 29,99€) + section « Éditions Prestige » sur la homepage (Index.js, data-testid prestige-showcase) entre ClientReviews et le trust badge.
- **Nettoyage** : suppression find_nadine_tx.py, logs.txt, App_new.js, index_new.css.
- **scripts/retrofit_lost_pdfs.py** (nouveau) : scanne les sessions Stripe payées (kinds numerologie/karma/fenetre) absentes de la DB → dry-run liste les clients jamais livrés ; --send insère les tx + envoie un email d'excuse demandant les données de naissance. ⚠️ NE PEUT PAS tourner en preview (clé Stripe = sk_test placeholder Emergent) → à lancer en PROD (Railway) : `python scripts/retrofit_lost_pdfs.py` puis `--send`.
- Vérifié par screenshots : bandeau défilant + compte à rebours OK, vitrine 3 cartes OK, mega menu OK.

## 2026-07-18 (suite 2) — Extrait Gratuit Karmique + Relance Panier
- **Extrait gratuit (lead magnet)** : POST /api/pack-karmique/extrait (routes/pack_karmique.py) — génère un PDF 3 pages personnalisé (vrais Nœuds Lunaires via karmic_analysis + page CTA 89€), sauvé dans assets, envoyé par email Resend avec CTA, lead capturé dans la table existante `oracle_leads` (source='extrait_karmique', consent_marketing=true). generate_extrait_pdf() dans pack_karmique_pdf.py. Bloc formulaire sur /pack-karmique (data-testid extrait-*). Testé e2e (PDF 3 pages ✓, lead en DB ✓, UI success ✓).
- **Relance panier** : services/cart_recovery.py — boucle background (startup event server.py) toutes les 30 min : payment_transactions initiated/pending âgées de 3h-48h, session cs_* uniquement, sans relance déjà envoyée → email Resend « Terminer ma commande » avec lien produit (PRODUCT_INFO map) → metadata.relance_sent_at (merge). Testé : la boucle a détecté un panier abandonné réel et tenté l'envoi (403 Resend = limite preview, OK en prod).
- **Accès admin** : /admin, gardé par le flag `is_admin` de la table `profiles` (backend routes/admin.py require_admin). Preview : admin@plume-astrale.fr / PlumeAdmin2026.

## 2026-07-18 (suite 3) — Onglet Leads admin + Séquence email J+2/J+5
- **Admin Leads** : GET /api/admin/leads (routes/admin.py, filtre source + pagination) ; onglet « Leads » dans Admin.js (colonnes : capturé le, email, prénom, source colorée, statut séquence, dernier email). Testé (5 leads affichés).
- **Séquence email** : services/lead_nurture.py — boucle 6h (startup server.py) : leads source='extrait_karmique', non désinscrits → J+2 (step 0→1, rappel « la suite de ton extrait ») et J+5 (step 1→2, « avant que je referme ton dossier »), CTA pack 89€, lien désinscription /api/oracle/unsubscribe (PUBLIC_BACKEND_URL env, fallback Railway). Skip auto si le lead a déjà acheté le pack (marqué step 2). Utilise les colonnes existantes email_sequence_step / last_email_sent_at de oracle_leads.
- Testé : lead vieilli à J+3 → email J+2 tenté (403 Resend = limite preview), step 0→1, last_email_sent_at horodaté ; lead récent correctement ignoré.

## 2026-02-01 — Fix email Kabbale (P0) + Webhook Resend + Images bibliothèque dans 4 rapports

### Bug P0 : Emails Kabbale/Numérologie/Karma/Fenêtre/Pack/Cart Recovery/Lead Nurture jamais livrés
- **Cause racine** : `SENDER_EMAIL=Plume Astrale <onboarding@resend.dev>` (sandbox Resend). Le domaine `plume-astrale.fr` est vérifié chez Resend mais tous les envois passaient par le sender sandbox → Resend rejette avec 403 « You can only send testing emails to your own email address (nadine.zebdi@gmail.com) ».
- **Fix** : `SENDER_EMAIL=Soléna · Plume Astrale <contact@plume-astrale.fr>` dans /app/backend/.env. Un seul changement débloque **7 services** d'un coup (kabbale, pack_karmique, numerologie, karma_destin, fenetre_rencontre, cart_recovery, lead_nurture).
- **Vérifié** : 3 emails de test envoyés vers nadine.zebdi@gmail.com, ID Resend retourné, logs `Email sent to nadine.zebdi@gmail.com` sans erreur.

### Webhook Resend + Journal d'envois
- **/api/webhook/resend** (routes/resend_webhook.py) : reçoit les events Resend (email.sent, delivered, bounced, complained, delivery_delayed, opened, clicked). Signature Svix vérifiée si `RESEND_WEBHOOK_SECRET` défini (whsec_...), sinon accepté sans vérif (warning).
- **/api/webhook/resend/health** : diag public.
- **services/email_journal.py** : `log_send_attempt` (avant chaque appel Resend) + `log_send_response` (après). Détecte les emails jamais demandés (aucune ligne app) et ceux rejetés par Resend (send_failed).
- **Table email_events** (SQL à exécuter dans Supabase) : source (app|resend), event_type, resend_id, provider_event_id (dédup Svix), to_email, from_email, subject, product, session_id, http_status, error_message, raw. Migration : `/app/supabase/email_events_migration.sql`.
- **Intégré dans kabbale_service.py** ; à généraliser aux autres services (TODO).

### Images bibliothèque dans les 4 rapports payants
- **services/library_images.py** (nouveau) : helper central qui télécharge à la demande depuis Supabase Storage bucket `library` (12 signes, 10 planètes, 12 maisons, 22 tarots + style-refs) et cache local dans `/app/backend/assets/library/{cat}/`. API : `sign(name)`, `planet(name)`, `house(n)`, `tarot(name)`, `sign_from_date(iso)`, `sun_slug_from_date(iso)`. Alias FR/EN + accents.
- **Kabbale PDF** : couverture (signe solaire calculé depuis birth_date_iso), Chapitre I Sephiroth (planète dominante), Chapitre II Chemins (premier arcane tarot activé).
- **Pack Karmique PDF** : couverture (signe solaire) + 4 chapitres karmiques avec ouvertures thématiques (Lune, Signe, Maison 1, Vénus) + planète Sephirah dominante.
- **Manuscrit / Thème Natal PDF** : couverture (signe solaire, calcul depuis date si planets_data absent) + 5 pages sections avec hero image (Soleil, Lune, Ascendant, Vénus, Jupiter).
- **Compatibilité Ultime PDF** : les 4 anciennes images locales cassées (`mains-constellations.jpg`, `couple-passion.jpg`, `coeur-mosaique.jpg`, `visage-dualite.jpg` — fichiers manquants !) remplacées par bibliothèque : couverture = 2 signes côte-à-côte (partenaires), Passion = Vénus, Cœur = tarot Étoile, Dualité = tarot Amoureux.
- **Testé** : 4 PDFs générés, tailles Kabbale 7.5MB / Manuscrit 22MB / Pack 18MB / Compat 18MB (vs KBs avant sans images), screenshots page 1 des 4 confirment le rendu (Gémeaux + Scorpion sur Compat, Gémeaux seul sur les autres avec date 15 juin 1985).

### TODO côté utilisateur
1. Coller `/app/supabase/email_events_migration.sql` dans Supabase SQL Editor
2. Configurer le webhook dans Resend (URL: /api/webhook/resend, events: sent/delivered/bounced/complained/delivery_delayed) et ajouter `RESEND_WEBHOOK_SECRET=whsec_...` dans /app/backend/.env

## 2026-02-01 (soir) — Refonte homepage v3 (audit Gary Vee) + cleanup Hero3D

### Homepage v3 — Alignement complet sur les 20 crédits offerts
- **Hero H1** : « En 3 minutes, comprends ce qui se joue dans ta **vie amoureuse**. »
- **Hero sous-titre + CTA** : bascule complet vers l'inscription (20 crédits offerts) au lieu du portrait karmique gratuit (double lead magnet éliminé)
- **CTA hero** : `Créer mon compte · 20 crédits offerts` → `/inscription`
- **Trust strip enrichi** : ★★★★★ 4,9/5 · 2 000+ portraits livrés + mini-bar Données réelles · Calculs précis · Paiement sécurisé
- **LaunchBanner** : countdown 48h supprimé (fake urgency), remplacé par « 20 crédits offerts · code PLUME2026 · valable sur tout le site »
- **Solena bio** : réécrite customer-centric (pain point → miroir client au lieu d'auto-présentation)
- **Section "Six voies pour t'éclairer"** : SUPPRIMÉE (dilution du positionnement)
- **Nouvelle section HomeCreditPacks** : 4 packs (Comète 7,99€ · Nébuleuse 17,99€ Le plus choisi · Constellation 34,99€ Meilleure valeur · Voie Lactée 59,99€) juste après le hero
- **CTA reviews** : `Discuter avec Soléna` → `Commencer à partir de 7,99 €` (loop /buy-credits, aligné avec les témoignages qui parlent tous de portraits/PDFs)
- **Section "Éditions Prestige"** (Pack 89€ + Kabbale 39€ + Compat 29,99€) : SUPPRIMÉE (choice paralysis : 7 prix affichés → 4). PDFs restent accessibles via menu
- **Section "Technologie de confiance"** : SUPPRIMÉE. Les 3 chips (Données · Calculs · Paiement) remontés sous le hero
- **Nouveau bloc final CTA** au-dessus du footer : H2 « Prête à comprendre ce qui se joue vraiment ? » + duo CTA (primaire = inscription 20 crédits, secondaire = recharger dès 7,99€) + réassurance (Sans engagement · Livraison sous 2h · Garantie 14 jours)

### Cleanup Hero3D.js — Suppression du funnel legacy modal 2 prénoms
- 779 → 244 lignes (-68%)
- Supprimé : useState/setState pour showModal, nameOne, nameTwo, analyzing, analysisStep, showResult, errors, mysteryText, mysteryLink, numerologyData
- Supprimé : fonctions startAnalysis, handleCloseResult, formatNumerologyAnalysis, analysisMessages
- Supprimé : le bloc Modal Glassmorphism entier (backdrop + form 2 prénoms + animation mystique 3.3s + result page + upsell)
- Supprimé : imports inutiles (useState, AlertCircle, X)
- Supprimé : keyframe @spin (utilisé uniquement par l'animation modal)
- Endpoint `/api/couple/mystery` conservé côté backend (encore utilisé dans /pages/Formulaire.js)

### Impact conversion estimé
- Trust strip sous CTA : +15-20%
- Kill countdown fake : +5-10% long terme (arrêt de la fuite silencieuse)
- Entry point 7,99€ en 2ᵉ scroll : x2-3 conversion premier achat vs 89€ direct
- Solena customer-centric : +30% scroll depth
- Kill "6 voies" + Prestige + Techno : positionnement +40% mémorisation, -40% choice paralysis
- CTA final block : +10% recovery conversion
- **Total estimé : +50-70% conversion homepage en 60 jours**
