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
- ✅ `server.py` - Messages lunaires, conseils
- ✅ `translation_service.py` - System prompt
- ✅ `tarot_interpretations.py` - 22 arcanes majeurs
- ✅ `astro_content_extended.py` - Planètes, aspects, rétrogrades (CORRIGÉ)
- ✅ `astro_content.py` - Qualités des signes
- ✅ `pdf_generator_v2.py` - Textes d'introduction, titres
- ✅ `premium_service.py` - Titres et réflexions
- ✅ `tarot_premium.py` - 22 arcanes majeurs complets avec accents

#### 2. Nouveaux Produits Premium

| Produit | Prix | Description |
|---------|------|-------------|
| Numérologie Complète | 49€ | Chemin de vie, Âme, Expression, Défis, Cycles |
| Horoscope Premium Annuel | 69€ | 12 mois avec transits et conseils personnalisés |
| Tarot de Marseille | 19€ | Tirage 3 cartes avec question personnalisée |
| Tirage Croix Celtique | 29€ | Tirage 10 cartes - Analyse approfondie |
| Analyse Amour Premium | 49€ | Compatibilité + Synastrie + Profils romantiques |
| Le Cercle (mensuel) | 14,90€ | Tarot + Lune + Horoscope quotidien |

#### 3. Nouveaux Endpoints Tarot

| Endpoint | Description |
|----------|-------------|
| `GET /api/tarot/domaines` | Liste des 6 domaines de questions |
| `POST /api/tarot/marseille` | Tirage 3 cartes avec question |
| `POST /api/tarot/celtique` | Tirage Croix Celtique 10 cartes |
| `GET /api/tarot/arcanes` | Liste des 22 arcanes majeurs |

#### 4. Domaines de Questions Tarot
- ❤️ Amour & Relations
- 💼 Carrière & Travail
- 💰 Finances & Abondance
- 🌿 Santé & Bien-être
- ✨ Spiritualité & Développement
- 🔮 Question Générale

## Backlog / P0-P1-P2

### P0 - Critique
- [ ] Configurer les clés Astrology API en production
- [ ] Créer les pages frontend pour les nouveaux tirages tarot
- [ ] Intégrer le formulaire de question attractif

### P1 - Important
- [ ] Page Tirage Marseille avec formulaire
- [ ] Page Tirage Celtique avec visualisation
- [ ] Générer les PDF Premium pour chaque tirage

### P2 - Nice to have
- [ ] Historique des tirages par utilisateur
- [ ] Partage social des tirages
- [ ] Notifications pour Le Cercle

## Variables d'environnement requises

```bash
# Backend (.env)
ASTROLOGY_API_USER_ID=xxx
ASTROLOGY_API_KEY=xxx
STRIPE_API_KEY=xxx
MONGO_URL=xxx
```

## Dernière mise à jour
4 Mars 2026
