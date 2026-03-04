# Plume Astrale - PRD (Product Requirements Document)

## Projet
**Plume Astrale** - Plateforme de guidance astrologique et symbolique

## Architecture
- **Frontend**: React.js avec Tailwind CSS
- **Backend**: Python FastAPI
- **Base de données**: MongoDB
- **APIs externes**: Astrology API (Plan Growth)

## Ce qui a été implémenté

### Session du 4 Mars 2026 (Forks précédents)

#### 1. Application complète
- Page d'accueil, formulaire thème astral, numérologie, tarologie, compatibilité, quotidien, horoscope
- Génération PDF thème astral (pdf_generator_v2.py - 28+ pages)
- Tirage Tarot Oui/Non gratuit
- Tirage en Croix (Tarologie & Médiumnité)
- Premium Landing & Parcours guidé

#### 2. Tirage Tarot en Direct
- Formulaire de question avec domaines
- Tirage Marseille (3 cartes - 19€) et Celtique (10 cartes - 29€)
- Animation révélation carte par carte

### Session du 4 Mars 2026 (Fork actuel) ✅

#### 3. Tirage du Jour (P0) ✅
- Composant `TirageDuJour` intégré sur la page d'accueil
- Endpoint `GET /api/tarot/jour` fonctionnel
- Date en français, badge GRATUIT, révélation interactive
- Détails dépliables : Affirmation, Amour, Travail, Rituel

#### 4. Audit des accents français (P1) ✅
- Corrections dans ~20 fichiers (backend + frontend)
- Navbar, SEO, Choix, Paiement, Tarologie, Quotidien, TarotOuiNon, Apercu, CharteConfiance
- PRODUCTS server.py, tarot_interpretations.py, pdf_generator_v2.py, premium_service.py

#### 5. Rapport de Compatibilité Astrale enrichi ✅
- **NOUVEAU** : Générateur PDF custom (`compatibility_pdf_generator.py`) - 11 pages de contenu riche
- Remplace l'ancien API externe (AstrologyAPI match_making_pdf) qui produisait un PDF vide
- **Frontend** : Formulaire 4 étapes (Partenaire 1 → Partenaire 2 → Question → Téléchargement)
- **Contenu du rapport** :
  - Couverture avec noms et signes
  - Profils astrologiques distincts des 2 partenaires
  - Portrait détaillé de chaque partenaire (forces, vigilance, chemin de vie)
  - Analyse élémentaire avec score de compatibilité (barre visuelle)
  - Comment les différences deviennent une force
  - Attraction et passion (ce que chacun trouve chez l'autre)
  - Communication et complicité (styles de communication distincts)
  - Défis et résolution de conflits (zones de tension + stratégies concrètes)
  - Compatibilité réelle avec score global + réponse à la question de l'utilisateur
  - Clés de réussite pour l'avenir
  - Message final personnalisé

#### 6. Fix déploiement ✅
- Ajout endpoint `/health` pour Kubernetes health check

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Health check Kubernetes |
| `/api/tarot/jour` | GET | Tirage du jour gratuit |
| `/api/compatibility/generate` | POST | Rapport compatibilité PDF (person1, person2, question) |
| `/api/tarot/domaines` | GET | 6 domaines de questions |
| `/api/tarot/marseille` | POST | Tirage 3 cartes |
| `/api/tarot/celtique` | POST | Tirage Croix Celtique 10 cartes |

## Backlog

### P1 - À faire
- [ ] Améliorer la mise en page du PDF thème astral principal (pdf_generator_v2.py) — grands espaces blancs, accents restants
- [ ] Intégrer paiement Stripe pour tous les produits
- [ ] Images individuelles des 22 arcanes dans les tirages

### P2 - Nice to have
- [ ] Visualisation natal_wheel_chart
- [ ] PDF de synthèse du tirage tarot
- [ ] Historique des tirages par utilisateur
- [ ] Partage social des tirages

## Dernière mise à jour
4 Mars 2026 - Fork actuel
