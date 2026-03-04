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
- ✅ `astro_content_extended.py` - Planètes, aspects, rétrogrades
- ✅ `pdf_generator_v2.py` - Textes d'introduction, titres
- ✅ `premium_service.py` - Titres et réflexions

#### 2. Amélioration mise en page PDF
- ✅ `_draw_centered_block()` - Gestion adaptative des espaces
- ✅ `_draw_short_phrase()` - Petites phrases centrées avec décoration
- ✅ `_draw_quote_box()` - Citations élégantes
- ✅ `_fill_remaining_space()` - Éviter les grands espaces blancs
- ✅ `_draw_info_box()` - Hauteur adaptative, styles multiples

#### 3. Intégration Astrology API Premium (Plan Growth)
Nouveau fichier: `/app/backend/services/astrology_api_premium.py`

**Endpoints créés:**

| Endpoint | Produit | Prix | Description |
|----------|---------|------|-------------|
| `/api/premium/love-analysis` | Offre Amour | 49€ | Compatibilité + Synastrie + Profils romantiques |
| `/api/premium/circle-daily` | Le Cercle | 14,90€/mois | Tarot + Lune + Horoscope quotidien |
| `/api/premium/user-profile` | Profil Complet | 39€ | Karma + Personnalité + Numérologie |
| `/api/premium/natal-chart` | Carte du ciel | - | SVG visuel |
| `/api/premium/lunar-metrics` | Métriques lunaires | - | Phase, énergie, rituels |
| `/api/premium/tarot-daily` | Tarot du jour | - | Carte, signification, conseil |
| `/api/premium/numerology` | Numérologie | - | Chemin de vie, Âme, Expression |
| `/api/premium/horoscope/{sign}` | Horoscope Premium | - | Prévisions par domaine |

## Produits configurés (PRODUCTS)

```python
"amour_premium": 49.00€   # Analyse Amour Premium
"cercle_mensuel": 14.90€  # Abonnement mensuel
"profil_complet": 39.00€  # Profil Astro-Numérologique
```

## Backlog / P0-P1-P2

### P0 - Critique
- [ ] Configurer les clés Astrology API en production
- [ ] Tester les endpoints avec l'API réelle
- [ ] Intégrer Stripe Checkout pour les nouveaux produits

### P1 - Important
- [ ] Créer les pages frontend pour les nouveaux produits
- [ ] Générer les PDF Premium pour chaque offre
- [ ] Système d'abonnement pour Le Cercle

### P2 - Nice to have
- [ ] Cache des réponses API fréquentes
- [ ] Notifications email pour les abonnés du Cercle
- [ ] Dashboard utilisateur avec historique

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
