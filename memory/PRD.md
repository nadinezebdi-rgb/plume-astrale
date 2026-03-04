# Plume Astrale - PRD (Product Requirements Document)

## Projet
**Plume Astrale** - Plateforme de guidance astrologique et symbolique

## Architecture
- **Frontend**: React.js avec Tailwind CSS
- **Backend**: Python FastAPI
- **Base de données**: MongoDB
- **APIs externes**: Astrology API (Plan Growth), Stripe

## Ce qui a été implémenté

### Session du 4 Mars 2026

#### 1. Corrections des accents français
- ✅ Tous les fichiers backend corrigés avec accents français complets
- ✅ 269 occurrences d'accents dans `tarot_premium.py`
- ✅ Messages, descriptions, interprétations tous en français

#### 2. Nouveaux Produits Premium

| Produit | Prix | Description |
|---------|------|-------------|
| Numérologie Complète | 49€ | Chemin de vie, Âme, Expression, Défis, Cycles |
| Horoscope Premium Annuel | 69€ | 12 mois avec transits et conseils personnalisés |
| Tarot de Marseille | 19€ | Tirage 3 cartes avec question personnalisée |
| Tirage Croix Celtique | 29€ | Tirage 10 cartes - Analyse approfondie |
| Analyse Amour Premium | 49€ | Compatibilité + Synastrie + Profils romantiques |
| Le Cercle (mensuel) | 14,90€ | Tarot + Lune + Horoscope quotidien |

#### 3. Page Tirage Tarot en Direct ✨
**Route: `/tirage-tarot`**

Fonctionnalités:
- 📝 **Formulaire de question** avec champ texte et exemples
- 🎯 **6 domaines** : Amour, Travail, Argent, Santé, Spirituel, Général
- 🃏 **2 types de tirage** : Marseille (3 cartes) et Celtique (10 cartes)
- ✨ **Animation en direct** : révélation carte par carte avec effet de retournement
- 📊 **Synthèse complète** avec tendance, messages et conseils

#### 4. Endpoints API Tarot

| Endpoint | Description |
|----------|-------------|
| `GET /api/tarot/domaines` | 6 domaines de questions |
| `POST /api/tarot/marseille` | Tirage 3 cartes avec question |
| `POST /api/tarot/celtique` | Tirage Croix Celtique 10 cartes |
| `GET /api/tarot/arcanes` | Liste des 22 arcanes majeurs |

#### 5. 22 Arcanes Majeurs Complets
Chaque arcane contient:
- Nom français et anglais
- Mots-clés, élément, planète
- Description poétique
- Interprétations droit/renversé pour: général, amour, travail, conseil

## Fichiers Créés/Modifiés

### Nouveaux fichiers:
- `/app/backend/services/tarot_premium.py` - Service complet tarot
- `/app/backend/services/astrology_api_premium.py` - API Astrology premium
- `/app/frontend/src/pages/TirageTarot.js` - Page tirage en direct

### Fichiers modifiés:
- `/app/backend/server.py` - Nouveaux endpoints et produits
- `/app/frontend/src/App.js` - Route tirage-tarot
- `/app/frontend/src/App.css` - Animations cartes

## Backlog / P0-P1-P2

### P0 - Terminé ✅
- [x] Formulaire de question pour tirages
- [x] Animation révélation cartes en direct
- [x] Tirage Celtique 10 cartes
- [x] Accents français partout

### P1 - À faire
- [ ] Intégrer paiement Stripe avant tirage
- [ ] Images des 22 arcanes majeurs
- [ ] PDF de synthèse du tirage

### P2 - Nice to have
- [ ] Historique des tirages par utilisateur
- [ ] Partage social des tirages
- [ ] Mode sombre/clair

## Dernière mise à jour
4 Mars 2026

