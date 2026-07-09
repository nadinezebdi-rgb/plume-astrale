# Plume Astrale — Design System v2 (Feb 2026)

> **Source de vérité** : `/app/design_guidelines.json`
>
> Ce fichier `.md` est un résumé exécutable pour l'implémentation. En cas de conflit, se référer au JSON.

## Vision
SaaS premium d'astrologie française. Design type magazine de luxe, fluide, sans friction, rassurant. Rejet total de l'imagerie "cheap" (boules de cristal, gothique). Utilisation de géométrie sacrée, line-art doré et transitions brumeuses.

**Vibe** : Application de bien-être premium (Calm/Headspace) croisée avec un magazine de luxe.

## Palette
| Rôle | Hex | Nom | Usage |
|---|---|---|---|
| Fond principal | `#111625` | Nuit Douce | Body, base app |
| Fond secondaire | `#1A2035` | Nuit Profonde | Cartes, blocs |
| Accent primaire | `#D4AF37` | Or Brossé | Boutons, icônes, line-art |
| Accent secondaire | `#E3D7FF` | Lavande Pâle | Textes secondaires |

**Éléments adaptifs** (une fois connecté, remplace subtilement le `#D4AF37` global) :
- 🔥 Feu (Bélier/Lion/Sagittaire) → `#E8A855`
- 💧 Eau (Cancer/Scorpion/Poissons) → `#7BA5D9`
- 🌬️ Air (Gémeaux/Balance/Verseau) → `#C4B0E0`
- 🌍 Terre (Taureau/Vierge/Capricorne) → `#9DAA82`

## Typographie
- **Titres H1/H2** : `Cinzel` (déjà en usage — continuité de marque)
- **Emphase italique dans les titres** : `Cormorant Garamond Italic`
- **Corps** : `Plus Jakarta Sans`

### Scale
- H1 : `text-4xl md:text-5xl lg:text-6xl tracking-tighter leading-none`
- H2 : `text-3xl md:text-4xl tracking-tight`
- H3 : `text-2xl md:text-3xl`
- Body : `text-base md:text-lg`
- Caption : `text-xs md:text-sm uppercase tracking-[0.2em]`

## Système de mouvement
- Durées : `fast=200ms`, `medium=400ms`, `slow=800ms`
- Easing : `cubic-bezier(0.22, 1, 0.36, 1)` (silk)
- Cascade : 80ms entre éléments
- **Respect strict de `prefers-reduced-motion`**
- Éviter `transition-all` — cibler `transition-colors`, `transition-opacity`, `transition-transform`

## Signatures créatives (uniques Plume Astrale)
1. **Le Souffle Astral** — L'opacité du grain de fond pulse subtilement (2%→4%) toutes les 12s pour un effet "vivant".
2. **Fil d'Ariane** — Ligne 1px verticale au centre du viewport (`rgba(212,175,55,0.15)`) qui descend en scrollant, connectant les sections spirituellement.
3. **Aura Connectée** — Une fois connectée, l'icône active de la Tab Bar mobile luit de la couleur de l'élément astral de l'utilisateur (pas de l'or standard).

## Composants clés
### Boutons (3 niveaux STRICTS)
- **Primary** : `bg-[#D4AF37] text-[#111625] shadow-[0_0_24px_rgba(212,175,55,0.35)] hover:shadow-[0_0_32px_rgba(212,175,55,0.5)] transition-shadow duration-400`
- **Secondary** : `border border-[#D4AF37]/40 text-[#D4AF37] hover:bg-[#D4AF37]/10 transition-colors duration-400`
- **Ghost** : `text-[#E3D7FF] hover:text-white hover:underline`

### Cartes
- Base glass : `bg-[#1A2035]/40 backdrop-blur-xl border border-[#D4AF37]/20 rounded-2xl p-6`
- Featured pricing (pack Clarté) : + `shadow-[0_0_40px_rgba(212,175,55,0.15)] scale-[1.02]`

### Navigation
- Desktop : sticky top, `bg-[#111625]/80 backdrop-blur-md border-b border-[#D4AF37]/10` (JAMAIS 100% transparent)
- Mobile Tab Bar : sticky bottom, 3 icônes fines (Mon Espace / Tarifs / Consulter), `bg-[#111625]/90 backdrop-blur-lg border-t border-[#D4AF37]/20`

### Transitions de sections
Utiliser `radial-gradient(ellipse at top, rgba(212,175,55,0.06), transparent 70%)` en background — PAS de changements de couleur solide.

## Grid & Layout
- Desktop : 12 colonnes, spacing 80px entre sections, asymétrique
- Mobile : 1 col fluide, padding-x 16px, spacing 48px entre sections
- Hero : split-screen gauche (texte + CTA) / droite (Solena + Moon 3D fondus)

## Overlays globaux
- **Grain SVG** 3% opacité `pointer-events-none fixed inset-0` — évite le banding OLED
- **Custom cursor** desktop : cercle doré 8px, délai 40ms, s'agrandit sur `[data-cursor="hover"]`
- **Fil d'Ariane** : `position:fixed; left:50%; top:0; bottom:0; width:1px; background:rgba(212,175,55,0.15)`
- **Toggle audio** discret dans la Tab Bar (défaut MUTE)

## Anti-patterns absolus
- ❌ Gradients violets/blancs
- ❌ Boules de cristal pixellisées
- ❌ Polices gothiques / grimoire
- ❌ Hard edges / lignes de coupe entre sections
- ❌ Noir pur (#000) / Blanc chirurgical (#FFF)
- ❌ `transition: all`
- ❌ Emojis dans les icônes (utiliser `lucide-react` avec `strokeWidth={1.5}`)

## Accessibilité
- Contraste minimum textes : `#94a3b8` ou `#E3D7FF` sur `#111625`
- Tous les éléments interactifs → `data-testid` unique
- Respect `prefers-reduced-motion` sur toutes les animations
