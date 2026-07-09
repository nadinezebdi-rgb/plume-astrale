# CHANGELOG - Plume Astrale

## 2026-02-09

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
