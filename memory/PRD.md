# Plume Astrale - PRD (Product Requirements Document)

## Projet
**Plume Astrale** - Plateforme de guidance astrologique et symbolique

## Architecture
- **Frontend**: React.js avec Tailwind CSS
- **Backend**: Python FastAPI
- **Base de données**: MongoDB
- **APIs externes**: Astrology API (Plan Growth), Stripe

## Ce qui a été implémenté

### Session du 4 Mars 2026 (Fork précédent)

#### 1. Page Tirage Tarot en Direct
**Route: `/tirage-tarot`**
- Formulaire de question avec champ texte et exemples
- 6 domaines : Amour, Travail, Argent, Santé, Spirituel, Général
- 2 types de tirage : Marseille (3 cartes - 19€) et Celtique (10 cartes - 29€)
- Animation en direct : révélation carte par carte
- Images tarot : Fond décoratif avec images tarot

#### 2. Nouveaux Produits Premium

| Produit | Prix | Description |
|---------|------|-------------|
| Numérologie Complète | 49€ | Chemin de vie, Âme, Expression, Défis |
| Horoscope Premium Annuel | 69€ | 12 mois avec transits personnalisés |
| Tarot de Marseille | 19€ | Tirage 3 cartes avec question |
| Tirage Croix Celtique | 29€ | Tirage 10 cartes - Analyse complète |
| Analyse Amour Premium | 49€ | Compatibilité + Synastrie |
| Le Cercle (mensuel) | 14,90€ | Tarot + Lune + Horoscope quotidien |

#### 3. 22 Arcanes Majeurs Complets
- Chaque arcane contient nom français/anglais, mots-clés, élément, planète, interprétations

### Session du 4 Mars 2026 (Fork actuel)

#### 4. Tirage du Jour (P0) ✅
- Composant `TirageDuJour` intégré sur la page d'accueil
- Endpoint `GET /api/tarot/jour` fonctionnel
- Date affichée en format français (ex: "04 mars 2026")
- Badge GRATUIT visible
- Carte face cachée avec bouton "Révéler ma carte"
- Carte révélée : nom, orientation, mots-clés, interprétation, message énergie
- Détails dépliables : Affirmation du jour, En Amour, Au Travail, Rituel suggéré
- Même carte pour tous les utilisateurs chaque jour (seed basé sur la date)

#### 5. Audit des accents français (P1) ✅
- **Backend** : Corrections dans tarot_interpretations.py, astro_content_extended.py, premium_service.py, pdf_generator_v2.py, premium_pdf_generator.py, astrology_pdf_api.py, server.py (PRODUCTS)
- **Frontend** : Corrections dans Navbar.js, SEO.js, Choix.js, Paiement.js, PremiumLanding.js, Tarologie.js, Quotidien.js, TarotOuiNon.js, Apercu.js, CharteConfiance.js
- Tous les textes visibles par l'utilisateur ont les accents français corrects

### Endpoints API

| Endpoint | Description |
|----------|-------------|
| `GET /api/tarot/jour` | Tirage du jour gratuit |
| `GET /api/tarot/domaines` | 6 domaines de questions |
| `POST /api/tarot/marseille` | Tirage 3 cartes avec question |
| `POST /api/tarot/celtique` | Tirage Croix Celtique 10 cartes |
| `GET /api/tarot/arcanes` | Liste des 22 arcanes majeurs |

## Backlog

### P0 - Terminé ✅
- [x] Tirage du Jour intégré sur la page d'accueil
- [x] Accents français corrigés dans toute l'application
- [x] Formulaire de question pour tirages
- [x] Animation révélation cartes en direct
- [x] Tirage Celtique 10 cartes avec question

### P1 - À faire
- [ ] Vérifier et améliorer la mise en page des PDFs (grands espaces blancs, centrage)
- [ ] Intégrer paiement Stripe avant tirage
- [ ] Images individuelles des 22 arcanes

### P2 - Nice to have
- [ ] Visualisation natal_wheel_chart
- [ ] PDF de synthèse du tirage
- [ ] Voix off pour tirage guidé
- [ ] Historique des tirages par utilisateur
- [ ] Partage social des tirages
- [ ] Génération PDF pour nouveaux rapports premium

## Dernière mise à jour
4 Mars 2026 - Session Fork actuelle
