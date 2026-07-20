# AUDIT — Menu "Outils" & Analyse des PDFs
_Généré le 20 février 2026 (session préview)_

---

## 🧰 Partie 1 — Chaque outil du menu appelle-t-il l'API ?

Statut de chacun des **14 outils** listés dans le menu `/outils/*` :

| Outil | Frontend | Endpoint backend | Source réelle | Verdict |
|---|---|---|---|---|
| 📜 **Thème Natal** | `/outils/theme-natal` | `POST /api/couple/mystery` | OpenAI + numérologie + astrology-api.io v3 (via `generate_couple_detailed_analysis`) | ✅ Appelle API v3 |
| 🃏 **Tarot Marseille** | `/outils/tarot` | `POST /api/tarot/marseille` | `tarot_premium.py` — données statiques FR (22 arcanes majeurs) | ❌ 100 % statique |
| 🃏 **Tarot Celtique** | `/outils/tarot` | `POST /api/tarot/celtique` | idem — tirage 10 cartes croix celtique | ❌ 100 % statique |
| 🃏 **Tarot Oui / Non** | `/outils/tarot/oui-non` | `POST /api/tarot/oui-non` | idem | ❌ 100 % statique |
| 🌙 **Horoscope** | `/outils/horoscope` | `POST /api/astrology/natal-chart` + `/horoscope-prediction` | `aio.natal_chart(...)` (API v3) | ✅ Appelle API v3 |
| 🔢 **Numérologie** | `/outils/numerologie` | `POST /api/numerology/complete` + `/deep-profile` | `numerology_service.py` — calculs locaux Python | ❌ 100 % local (mais 100 % FR) |
| 🎭 **Archétype** | `/outils/archetype` | `POST /api/archetype/generate` | `aio.archetypes(...)` (API v3 `/analysis/archetypes`) + polish FR | ✅ Appelle API v3 |
| 💞 **Compatibilité (crédits)** | `/outils/compatibilite` | `POST /api/compatibility/generate` | `generate_compatibility_pdf(...)` sans `api_data` → **contenu générique** | ⚠️ Enrichi possible mais pas branché sur API v3 |
| 🌞 **Révolution Solaire** | `/outils/revolution-solaire` | `POST /api/astrology/v3/solar-return` | `aio.solar_return` + `solar_return_report` **(avec `@fr_polish` depuis hier)** | ✅ Appelle API v3 |
| 👼 **Oracle des Anges** | `/outils/oracle` | `POST /api/oracle` | `oracle_service.py` (données statiques + OpenAI) | ⚠️ Mix statique + OpenAI, pas API v3 |
| ✨ **Énergie du Jour** | `/outils/energie` | `GET /api/energy/today` | `energy_service.py` — GPT-4o-mini directement (transits perso) | ⚠️ GPT direct, pas API v3 |
| 🕯️ **Rituel Personnel** | `/outils/rituel` | `GET /api/ritual/today` | Données **statiques** (rituels pré-écrits) | ❌ 100 % statique |
| 💬 **Chat Astral (IA)** | `/outils/consultation` | `POST /api/astrology/v3/chat` | `aio.astro_chat(...)` (API v3) + OpenAI | ✅ Appelle API v3 |
| 🔥 **AstroSexo** | `/outils/astrosexo` | ✗ AUCUN | **100 % frontend** (`/src/lib/astrosexo-data.js`) | ❌ Aucun appel |
| 💗 **Love Languages** | `/outils/love-languages` | `POST /api/astrology/v3/love-languages` | `aio.love_languages(...)` **(avec `@fr_polish`)** | ✅ Appelle API v3 |

### 🎯 Verdict synthétique

- **6 outils** utilisent réellement l'API `astrology-api.io v3` : Thème Natal, Horoscope, Archétype, Révolution Solaire, Chat Astral, Love Languages.
- **3 outils** sont sur **OpenAI direct** (Énergie, Oracle, partie IA de Thème Natal) — bonne qualité FR mais aucun calcul astro réel.
- **5 outils** sont **statiques / calculés localement** : les 3 Tarot, la Numérologie, le Rituel du jour, AstroSexo.

### 🚨 Points d'attention

1. **AstroSexo** est du contenu figé dans le code frontend → chaque signe a le même texte pour tous les visiteurs. Envisager de brancher sur `aio.astro_sexo(...)` (à créer) ou au minimum le personnaliser avec la Vénus/Mars du natal.
2. **Compatibilité (crédits)** — le PDF est généré sans appeler l'API v3 : il donne le même contenu quel que soit le vrai thème natal. Recommandation : appeler `aio.synastry(...)` avant de générer le PDF.
3. **Rituel du jour** — 100 % statique, à personnaliser via le natal (Lune actuelle × Lune natale par exemple).

---

## 📄 Partie 2 — Analyse Design des 5 PDFs

Voici l'inventaire complet des 5 générateurs de PDF, pour t'aider à décider une **charte visuelle unifiée**.

### 1. 🌳 **Kabbale — Arbre de Vie** (39 €)
- **Fichier** : `services/kabbale_pdf.py` — 502 lignes
- **Moteur** : ReportLab **Platypus** (moderne, flowables)
- **Nombre de pages** : ~15 (11 `PageBreak`)
- **Palette** :
  - Fond : `#111625` (nuit profonde)
  - Or : `#D4AF37`
  - Crème : `#F5EEE0`
  - Lavande : `#E3D7FF`
- **Typographie** : Cinzel (caption/titre en small caps) + Cormorant Garamond (corps texte)
- **Images** : 2 (glyphes des 10 Sephiroth via `library_images.py` — Supabase Storage 2048 px)
- **Structure** :
  1. Couverture (titre or, sous-titre italique, citation Zohar)
  2. Introduction (Kabbale expliquée)
  3. Les 10 Sephiroth (une page par Sephira dominante)
  4. Les 22 chemins hébraïques (grille)
  5. Synthèse Soléna
  6. Rituel signature
- **Signature visuelle** : starfield 30 étoiles + halo doré radial en haut
- **Statut** : ✅ Design de référence à généraliser

### 2. 💎 **Pack Karmique + Kabbale** (89 €)
- **Fichier** : `services/pack_karmique_pdf.py` — 376 lignes
- **Moteur** : ReportLab **Platypus**
- **Nombre de pages** : ~12-14 (10 `PageBreak`)
- **Palette** : identique Kabbale
- **Typographie** : Cinzel + Cormorant Garamond
- **Images** : 1 seule (couverture)
- **Structure** :
  1. Couverture "Le Rendez-vous de ton Âme"
  2. Introduction karmique
  3. Nœuds Nord/Sud (identifiés via API v3)
  4. Saturne · Chiron · Pluton (transformations)
  5. Rétrogrades natales (leçons du passé)
  6. Signature Soléna
- **Statut** : ✅ Cohérent avec Kabbale mais **moins riche en visuel** (1 seule image) → à enrichir avec glyphes planétaires

### 3. 🌟 **Karma & Destin standalone** (via `pdf_generator.py`)
- **Fichier** : `services/pdf_generator.py` — 538 lignes
- **Moteur** : ReportLab **canvas bas-niveau** (⚠️ approche ancienne, différente des autres)
- **Nombre de pages** : ~7 (via `showPage()`)
- **Palette** :
  - Fond : `#0F0518` (violet profond — **DIFFÉRENT** du #111625 des autres)
  - Or : `#C5A059` (**DIFFÉRENT** du #D4AF37 des autres)
  - Crème : `#F3E5AB`
- **Typographie** : Helvetica (par défaut, pas de Cinzel/Cormorant)
- **Images** : 4 (via `library_images.py`)
- **Structure** : Couverture + horoscope + planètes + rituels
- **Statut** : ⚠️ **HORS CHARTE** — palette légèrement différente, pas de typo Plume Astrale → À réharmoniser en priorité

### 4. 💘 **Compatibilité Ultime** (29,99 €)
- **Fichier** : `services/compatibility_pdf_generator.py` — 950 lignes (le plus gros)
- **Moteur** : ReportLab **canvas bas-niveau**
- **Nombre de pages** : ~14 (via `showPage()`)
- **Palette** : ?
- **Images** : 4
- **Structure** : Analyse détaillée par domaine (communication, physique, projets, spiritualité…)
- **Statut** : ⚠️ **HORS CHARTE** aussi + `api_data=None` par défaut → contenu générique

### 5. 🗺️ **Astrocartographie** (49 €) — nouveauté 2026-02
- **Fichier** : `services/astrocartographie_pdf.py` — 464 lignes
- **Moteur** : ReportLab **Platypus**
- **Nombre de pages** : ~30 (10 `PageBreak` + génération dynamique de pages "2 lignes/page")
- **Palette** : identique Kabbale (`#111625` + or `#D4AF37`)
- **Typographie** : Helvetica (⚠️ pas de Cinzel car pas embarqué — à corriger)
- **Images** : 3 (couverture + carte du monde SVG → PNG via cairosvg + citations)
- **Structure** :
  1. Couverture "Où vivre ta meilleure vie ?"
  2. Introduction astrocartographie
  3. Carte du monde SVG (lignes planétaires)
  4. Lignes détaillées (12 pages, 40 combinaisons planète × ligne)
  5. 3 villes choisies (3 pages chacune)
  6. 2 villes bonus (2 pages chacune)
  7. Synthèse + Rituel d'ancrage
- **Signature visuelle** : starfield + radial gold glow
- **Statut** : ✅ Design cohérent avec Kabbale mais **manque les polices custom**

---

## 🎨 Recommandations pour la charte PDF unifiée

### Points de convergence à figer
1. **Palette** :
   - Fond principal : `#111625` (nuit profonde Plume)
   - Or accent : `#D4AF37`
   - Or clair : `#E8C766` (h2)
   - Crème corps : `#F5EEE0`
   - Lavande italique : `#E3D7FF`
   - Muted : `#9089B5`
2. **Typographie unifiée** :
   - `Cinzel` (small caps or) pour captions, sous-titres, signatures
   - `Cormorant Garamond` (serif italique) pour corps texte + citations
   - À **embarquer via `pdfmetrics.registerFont`** dans chaque générateur (aujourd'hui seul Kabbale + Karmique les enregistrent)
3. **Éléments décoratifs récurrents** :
   - Starfield 30 étoiles seed par page (déjà présent Kabbale, Karmique, Astrocarto)
   - Radial gold glow en haut de page (idem)
   - Bordure or fine 1px opacity 0.15 → à ajouter partout
   - Séparateur en fin de section : `✦ · ✦`
4. **Pagination bas de page** :
   - `Plume Astrale · [Produit] · page X` en gris `#9089B5` centré 8pt

### Chantier prioritaire
1. **Réharmoniser** `pdf_generator.py` (Karma standalone) et `compatibility_pdf_generator.py` avec la palette Kabbale (`#111625` + `#D4AF37`) → 1-2h de refactor.
2. **Embarquer** les polices Cinzel + Cormorant dans **tous** les générateurs pour un rendu identique.
3. **Ajouter des images** au Pack Karmique (glyphes planétaires des noeuds, Saturne, Chiron, Pluton) — utilisable via `library_images.load_planet(...)`.
4. **Créer un module `pdf_theme.py`** partagé qui expose :
   - `PALETTE` (dict couleurs)
   - `STYLES` (dict ParagraphStyle unifiés)
   - `register_fonts()` (Cinzel + Cormorant)
   - `starfield_bg(canvas, page)` (fond commun)
   - Chaque générateur importe `from services.pdf_theme import ...`
