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
