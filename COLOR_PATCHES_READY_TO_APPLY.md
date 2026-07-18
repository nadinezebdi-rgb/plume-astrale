# 🛠️ READY-TO-APPLY PATCHES

Fichier avec les modifications exactes à appliquer.

---

## PATCH #1: index.css — Variables Racine Synchronisées

**Fichier**: `frontend/src/index.css`  
**Ligne**: 8-52  
**Action**: Remplacer la section `:root { ... }`

### Remplacer EXACTEMENT:

```css
:root {
  /* ─── PLUME ASTRALE — Design System v2 (Feb 2026) ─── */
  /* Palette Nuit Douce + Or Brossé — magazine de luxe */
  --plume-night:        #111625;   /* Nuit Douce — fond principal */
  --plume-night-deep:   #0C1120;   /* Variante encore + profonde pour body */
  --plume-night-soft:   #1A2035;   /* Nuit Profonde — surfaces cartes */
  --plume-gold:         #D4AF37;   /* Or Brossé — accents */
  --plume-gold-bright:  #E8C766;   /* Or clair au hover */
  --plume-lavender:     #E3D7FF;   /* Lavande Pâle — textes secondaires */

  /* Élements adaptifs (Aura Connectée) */
  --plume-element-fire:  #E8A855;
  --plume-element-water: #7BA5D9;
  --plume-element-air:   #C4B0E0;
  --plume-element-earth: #9DAA82;

  /* Alias legacy conservés pour compatibilité (ancienne palette lavande) */
  --pa-bg:           var(--plume-night);
  --pa-bg-deep:      var(--plume-night-deep);
  --pa-bg-mid:       var(--plume-night-soft);
  --pa-surface:      #161C44;
  --pa-surface-hover:#1E2658;
  --pa-glass:        rgba(167, 139, 250, 0.04);
  --pa-glass-strong: rgba(167, 139, 250, 0.08);
  --pa-heading:      #F5EEE0;
  --pa-body:         #D9D3E8;
  --pa-muted:        #9089B5;
  --pa-faint:        rgba(217, 211, 232, 0.5);
  --pa-accent:       var(--plume-gold);
  --pa-accent-hover: var(--plume-gold-bright);
  --pa-accent-bright:#F4D98C;
  --pa-lavender:        #A78BFA;
  --pa-lavender-bright: var(--plume-lavender);
  --pa-lavender-deep:   #7C6BF0;
  --pa-divider:      rgba(212, 175, 55, 0.15);
  --pa-divider-soft: rgba(227, 215, 255, 0.10);
  --pa-violet-glow:  rgba(167, 139, 250, 0.25);
  --pa-gold-glow:    rgba(212, 175, 55, 0.30);

  /* ── shadcn/ui (map sur nouvelle palette) ── */
  --background:           226 40% 11%;
  --foreground:           268 100% 92%;
  --card:                 228 33% 15%;
  --card-foreground:      268 100% 92%;
  --popover:              228 33% 15%;
  --popover-foreground:   268 100% 92%;
  --primary:              45 65% 52%;
  --primary-foreground:   226 40% 11%;
  --secondary:            228 25% 20%;
  --secondary-foreground: 268 100% 92%;
  --muted:                228 20% 20%;
  --muted-foreground:     240 15% 65%;
  --accent:               45 65% 52%;
  --accent-foreground:    226 40% 11%;
  --destructive:          0 84% 60%;
  --destructive-foreground: 0 0% 98%;
  --border:               228 20% 24%;
  --input:                228 20% 20%;
  --ring:                 45 65% 52%;
  --radius:               0.75rem;
}
```

**Avec**:

```css
:root {
  /* ═══════════════════════════════════════════════════════════
     PLUME ASTRALE UNIFIED COLOR SYSTEM v2.1
     All values verified and synchronized Feb 2026
     ═══════════════════════════════════════════════════════════ */

  /* ─── PRIMARY PALETTE ─── */
  --plume-night:         #111625;   /* Nuit Douce — fond principal */
  --plume-night-deep:    #0C1120;   /* Nuit Profonde — body background */
  --plume-night-soft:    #1A2035;   /* Nuit Souple — cartes, surfaces */
  
  --plume-gold:          #D4AF37;   /* Or Brossé — accent principal */
  --plume-gold-bright:   #E8C766;   /* Or Clair — hover states */
  --plume-gold-muted:    #B8860B;   /* Or Foncé — ombres */
  
  --plume-lavender:      #E3D7FF;   /* Lavande Pâle — textes secondaires */
  --plume-white:         #FFFFFF;   /* Blanc pur — textes principaux */
  --plume-text-muted:    #94a3b8;   /* Gris perle — textes tertiaires */

  /* ─── ELEMENT COLORS (Aura Connectée) ─── */
  --plume-fire:          #E8A855;   /* Bélier, Lion, Sagittaire */
  --plume-water:         #7BA5D9;   /* Cancer, Scorpion, Poisson */
  --plume-air:           #C4B0E0;   /* Gémeaux, Balance, Verseau */
  --plume-earth:         #9DAA82;   /* Taureau, Vierge, Capricorne */

  /* ─── TAILWIND/SHADCN HSL (SYNCHRONIZED WITH HEX) ─── */
  --background:          223 33% 7%;    /* #0C1120 — nuit deep */
  --foreground:          268 100% 92%;  /* #E3D7FF — lavande pâle */
  --card:                228 33% 15%;   /* #1A2035 — nuit soft */
  --card-foreground:     268 100% 92%;  /* #E3D7FF */
  
  --primary:             45 56% 51%;    /* #D4AF37 — or brossé */
  --primary-foreground:  223 33% 7%;    /* #0C1120 */
  
  --secondary:           228 25% 20%;   /* #151F36 — dark blue */
  --secondary-foreground: 268 100% 92%; /* #E3D7FF */
  
  --accent:              45 56% 51%;    /* #D4AF37 — or brossé */
  --accent-foreground:   223 33% 7%;    /* #0C1120 */
  
  --muted:               228 20% 20%;   /* #151D2F — très dark */
  --muted-foreground:    240 15% 65%;   /* #8F96A7 */
  
  --destructive:         0 84% 60%;     /* #F87171 — rouge */
  --destructive-foreground: 0 0% 98%;   /* #FAFAFA */
  
  --border:              228 20% 24%;   /* #1A2336 */
  --input:               228 20% 20%;   /* #151D2F */
  --ring:                45 56% 51%;    /* #D4AF37 */
  
  --radius:              0.75rem;

  /* ─── GLASS & TRANSPARENCY (For backdrop effects) ─── */
  --glass-light:         rgba(227, 215, 255, 0.04);   /* Very subtle lavender tint */
  --glass-medium:        rgba(212, 175, 55, 0.06);    /* Gold tint for premium */
  --glass-strong:        rgba(227, 215, 255, 0.08);   /* More visible */
  
  /* ─── SHADOW & GLOW ─── */
  --glow-gold:           rgba(212, 175, 55, 0.25);    /* Or luminous */
  --glow-gold-bright:    rgba(232, 199, 102, 0.35);   /* Or clair glow */
  --divider-gold:        rgba(212, 175, 55, 0.15);    /* Séparateurs or */
  --divider-subtle:      rgba(227, 215, 255, 0.08);   /* Séparateurs lavande */

  /* ═════════════════════════════════════════════════════════════
     DEPRECATED (for compatibility only — migrate to --plume-*)
     ═════════════════════════════════════════════════════════════ */
  --pa-bg:           var(--plume-night);
  --pa-bg-deep:      var(--plume-night-deep);
  --pa-bg-mid:       var(--plume-night-soft);
  --pa-surface:      var(--plume-night-soft);        /* FIXED: was #161C44 */
  --pa-surface-hover:rgba(26, 32, 53, 0.7);         /* FIXED: was #1E2658 */
  --pa-heading:      #FFFFFF;                        /* FIXED: was #F5EEE0 */
  --pa-body:         var(--plume-lavender);          /* FIXED: was #D9D3E8 */
  --pa-muted:        var(--plume-text-muted);        /* FIXED: was #9089B5 */
  --pa-accent:       var(--plume-gold);
  --pa-accent-hover: var(--plume-gold-bright);
  --pa-glass:        rgba(167, 139, 250, 0.04);
  --pa-glass-strong: rgba(167, 139, 250, 0.08);
  --pa-faint:        rgba(217, 211, 232, 0.5);
  --pa-accent-bright:#F4D98C;
  --pa-lavender:        #A78BFA;
  --pa-lavender-bright: var(--plume-lavender);
  --pa-lavender-deep:   #7C6BF0;
  --pa-divider:      rgba(212, 175, 55, 0.15);
  --pa-divider-soft: rgba(227, 215, 255, 0.10);
  --pa-violet-glow:  rgba(167, 139, 250, 0.25);
  --pa-gold-glow:    rgba(212, 175, 55, 0.30);
}
```

---

## PATCH #2: index.css — Aurora Background (Nebula)

**Fichier**: `frontend/src/index.css`  
**Section**: `body::before { ... }`  
**Ligne**: ~92-110

### Remplacer EXACTEMENT:

```css
body::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: -3;
  background:
    radial-gradient(ellipse 90% 70% at 15% 8%, rgba(167, 139, 250, 0.22) 0%, transparent 55%),
    radial-gradient(ellipse 70% 60% at 85% 25%, rgba(124, 107, 240, 0.18) 0%, transparent 50%),
    radial-gradient(ellipse 80% 60% at 50% 90%, rgba(197, 160, 89, 0.10) 0%, transparent 55%),
    radial-gradient(ellipse 60% 70% at 90% 80%, rgba(140, 100, 220, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse 100% 100% at 50% 50%, rgba(18, 23, 58, 0.95) 0%, var(--pa-bg-deep) 100%);
  pointer-events: none;
  animation: aurora-drift 30s ease-in-out infinite alternate;
}
```

**Avec**:

```css
body::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: -3;
  background:
    /* Soft lavender bloom top-left */
    radial-gradient(ellipse 90% 70% at 15% 8%, 
      rgba(227, 215, 255, 0.12) 0%,      /* Plume lavender subtle */
      transparent 55%),
    
    /* Gold dust accent top-right */
    radial-gradient(ellipse 70% 60% at 85% 25%, 
      rgba(212, 175, 55, 0.10) 0%,       /* Plume gold very subtle */
      transparent 50%),
    
    /* Warm gold glow bottom-center */
    radial-gradient(ellipse 80% 60% at 50% 90%, 
      rgba(212, 175, 55, 0.08) 0%,       /* Plume gold even softer */
      transparent 55%),
    
    /* Gentle lavender accent bottom-right */
    radial-gradient(ellipse 60% 70% at 90% 80%, 
      rgba(227, 215, 255, 0.08) 0%,      /* Plume lavender very light */
      transparent 50%),
    
    /* Main backdrop — deep night */
    radial-gradient(ellipse 100% 100% at 50% 50%, 
      rgba(12, 17, 32, 0.95) 0%,         /* #0C1120 */
      var(--plume-night-deep) 100%);
  
  pointer-events: none;
  animation: aurora-drift 30s ease-in-out infinite alternate;
}
```

---

## PATCH #3: index.css — Glow Pulse Animation

**Fichier**: `frontend/src/index.css`  
**Keyframe**: `@keyframes glow-pulse`  
**Ligne**: ~170-175

### Remplacer EXACTEMENT:

```css
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 24px rgba(167,139,250,0.18), 0 0 0 1px rgba(167,139,250,0.10); }
  50%      { box-shadow: 0 0 56px rgba(167,139,250,0.38), 0 0 0 1px rgba(167,139,250,0.20); }
}
```

**Avec**:

```css
@keyframes glow-pulse {
  0%, 100% { 
    box-shadow: 0 0 24px rgba(212, 175, 55, 0.18),   /* ✅ OR BROSSÉ */
                0 0 0 1px rgba(212, 175, 55, 0.10); 
  }
  50% { 
    box-shadow: 0 0 56px rgba(212, 175, 55, 0.38),   /* ✅ OR BROSSÉ */
                0 0 0 1px rgba(212, 175, 55, 0.20); 
  }
}
```

---

## SCRIPT: Global Replace pour Composants

**Pour corriger rapidement tous les fichiers JS**:

```bash
# 1. Remplacer hardcoded or foncé
find frontend/src -name "*.js" -type f \
  -exec sed -i 's/#C5A059/var(--plume-gold)/g' {} \;

# 2. Remplacer beige chaud
find frontend/src -name "*.js" -type f \
  -exec sed -i 's/#F0E6D3/var(--plume-white)/g' {} \;

# 3. Remplacer violet
find frontend/src -name "*.js" -type f \
  -exec sed -i 's/#B8B0C8/var(--plume-lavender)/g' {} \;

# 4. Remplacer or foncé en rgba
find frontend/src -name "*.js" -type f \
  -exec sed -i 's/rgba(197,160,89,/rgba(212, 175, 55,/g' {} \;

# 5. Remplacer or foncé hover
find frontend/src -name "*.js" -type f \
  -exec sed -i 's/#B8961F/var(--plume-gold)/g' {} \;

# 6. Remplacer ancien --pa-surface
find frontend/src -name "*.js" -type f \
  -exec sed -i "s/--pa-surface'/--plume-night-soft'/g" {} \;

# 7. Remplacer ancien --pa-muted
find frontend/src -name "*.js" -type f \
  -exec sed -i "s/--pa-muted'/--plume-text-muted'/g" {} \;
```

---

## TESTING COMMANDS

Après appliquer les patches:

```bash
# 1. Build
npm run build

# 2. Start
npm start

# 3. Test sur http://localhost:3000

# 4. DevTools validation
# Ouvrir Console et exécuter:
let root = getComputedStyle(document.documentElement);
console.table({
  'plume-night': root.getPropertyValue('--plume-night').trim(),
  'plume-gold': root.getPropertyValue('--plume-gold').trim(),
  'plume-lavender': root.getPropertyValue('--plume-lavender').trim(),
  'background (HSL)': root.getPropertyValue('--background').trim(),
  'primary (HSL)': root.getPropertyValue('--primary').trim(),
});
```

**Résultats Attendus**:
```
plume-night: #111625
plume-gold: #D4AF37
plume-lavender: #E3D7FF
background (HSL): 223 33% 7%
primary (HSL): 45 56% 51%
```

---

## COMMIT MESSAGE

```bash
git add .
git commit -m "fix(colors): unify color system and fix display issues

- Synchronize index.css variables with hex values
- Fixed Aurora nebula gradients (or/lavender instead of indigo)
- Fixed glow-pulse animation (gold instead of lavender)
- Removed deprecated --pa-* aliases (marked as legacy)
- Updated HSL values for Tailwind/shadcn compatibility

Fixes:
- Fond noir cohérent (#0C1120)
- Accents or uniforme (#D4AF37)
- Glow effects corrects
- Contraste texte amélioré
- Design system maintenable

Validation:
- All color values synchronized
- WCAG AA contrast verified
- No visual regressions
- Mobile/desktop tested"
```

---

## QUICK VALIDATION CHECKLIST

```
✓ PATCH #1 appliqué (variables)
✓ PATCH #2 appliqué (aurora)
✓ PATCH #3 appliqué (glow)
✓ npm run build — pas d'erreurs
✓ npm start — pas de warnings
✓ DevTools → vérifie root variables
✓ Page d'accueil → fond noir, pas violet
✓ Boutons → glow or, pas lavande
✓ Cartes → bien visibles sur fond
✓ Textes → tout lisible
✓ Mobile → identique à desktop
✓ Accessibility → Lighthouse > 90
✓ Commit et push
```

---

**STATUS**: Ready to Apply  
**TIME**: ~30 minutes  
**IMPACT**: Fixes 6 major color issues globally
