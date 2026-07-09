# CHANGELOG - Plume Astrale

## 2026-02-09

### Session 2 — Harmonisation Visuelle Absolue (P0)
- **Fix cassure Lune ↔ Page** : Hero3D background passé de `radial(#1a1147→#0C0918→#050308)` (violet/noir agressif) à `radial(#1A2035→#141A2C→#111625)` — parfaite continuité avec le reste de l'app.
- **Emissif Lune** : `0x2a1e4a` (violet indigo) → `0x1A2035` (Nuit Douce). Intensité réduite 0.08 → 0.06.
- **Shader aura** : palette violet/indigo remplacée par gold + midnight blue. L'aura se fond désormais dans le fond de la page.
- **TestimonialsMarquee** (`/app/frontend/src/components/design/TestimonialsMarquee.js`) : bandeau de preuve sociale animé sous le Hero, 5 bulles glass (Léa/Camille/Marion/Sophie/Alice), verbatims 5⭐, effet Cormorant italic + Cinzel uppercase, pauseOnHover.
- **Index.js** : `<TestimonialsMarquee />` intercalé entre `<Hero3D />` et `<ServicesShowcase />`. Body background `#111625` explicite pour éviter tout flash.

### Session 1 — Fix Three.js Deprecation
- Remplacement de `THREE.Clock` par `performance.now()` dans `Moon3D.js`. Warning console éliminé.
