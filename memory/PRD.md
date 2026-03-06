# Plume Astrale - PRD (Product Requirements Document)

## Projet
**Plume Astrale** - Plateforme de guidance astrologique et symbolique

## Architecture
- **Frontend**: React.js avec Tailwind CSS + Shadcn UI
- **Backend**: Python FastAPI
- **Base de données**: MongoDB
- **Paiement**: Stripe (via emergentintegrations)
- **Authentification**: JWT (PyJWT + bcrypt)
- **APIs externes**: Astrology API (Plan Growth)

## Ce qui a été implémenté

### Sessions précédentes (forks antérieurs)

#### Application complète
- Page d'accueil, formulaire thème astral, numérologie, tarologie, compatibilité, quotidien, horoscope
- Génération PDF thème astral (pdf_generator_v2.py - 28+ pages)
- Tirage Tarot Oui/Non, Tirage en Croix, Tirage Tarot de Marseille/Celtique
- Premium Landing & Parcours guidé
- Rapport de Compatibilité Astrale enrichi (11 pages PDF)
- Tirage du Jour gratuit
- Paywalls Stripe par service
- Correction accents français
- Health check Kubernetes

### Session du 6 Mars 2026 — Système de Crédits (P0)

#### Phase 1 : Backend Auth & Wallet
- `POST /api/auth/register` — inscription avec profil astrologique + 20 crédits bonus
- `POST /api/auth/login` — connexion JWT + solde crédits
- `GET /api/auth/me` — profil utilisateur + solde (protégé)
- `GET /api/wallet/balance` — solde crédits (protégé)
- `GET /api/wallet/transactions` — historique des transactions (protégé)
- Modèles MongoDB : `users`, `user_wallets`, `credit_transactions`
- Services : `auth_service.py`, `wallet_service.py`
- Bonus quotidien : +1 crédit/jour (dès J+1, automatique à la requête)

#### Phase 2 : Stripe Credit Packs
- `GET /api/credits/packs` — 3 packs (public)
- `GET /api/credits/service-costs` — coûts des services (public)
- `POST /api/credits/checkout` — session Stripe pour achat (protégé)
- `GET /api/credits/checkout/status/{session_id}` — polling + ajout crédits (protégé)
- Packs : Découverte (10 cr / 9€), Exploration (50 cr / 24,99€), Premium (100 cr / 44,99€)
- Idempotence : pas de double crédit pour une même session Stripe

#### Phase 3 : Frontend Auth & UI
- `AuthContext` global (register, login, logout, useCredits, refreshBalance)
- Page Connexion (`/connexion`)
- Page Inscription en 2 étapes (`/inscription`) — identifiants + profil astrologique
- Page Acheter des crédits (`/acheter-credits`) — 3 packs avec prix, badge "Populaire"
- Page Succès paiement crédits (`/credits/succes`) — polling statut
- Navbar : affiche Connexion/Inscription (déconnecté) ou solde crédits/Déconnexion (connecté)
- Input heure de naissance en format 24h (champs séparés H:M, 0-23)

#### Phase 4 : Gating des services
- `POST /api/credits/use` — déduction crédits par service
- `GET /api/credits/check-free-tarot` — vérification tirage gratuit
- Tarot Oui/Non : 1er tirage gratuit par compte, puis 2 crédits
- Coûts définis serveur : tarot_oui_non=2, lecture_tarot=10, lecture_astrologique=10, numerologie=10, cartographie_premium=60

## Endpoints API

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/health` | GET | Non | Health check Kubernetes |
| `/api/auth/register` | POST | Non | Inscription + 20 crédits bonus |
| `/api/auth/login` | POST | Non | Connexion JWT |
| `/api/auth/me` | GET | Oui | Profil + solde |
| `/api/wallet/balance` | GET | Oui | Solde crédits |
| `/api/wallet/transactions` | GET | Oui | Historique transactions |
| `/api/credits/packs` | GET | Non | Packs disponibles |
| `/api/credits/service-costs` | GET | Non | Coûts des services |
| `/api/credits/checkout` | POST | Oui | Checkout Stripe |
| `/api/credits/checkout/status/{id}` | GET | Oui | Statut paiement + ajout crédits |
| `/api/credits/use` | POST | Oui | Déduction crédits |
| `/api/credits/check-free-tarot` | GET | Oui | Vérif tirage gratuit |
| `/api/tarot/jour` | GET | Non | Tirage du jour gratuit |
| `/api/compatibility/generate` | POST | Non | Rapport compatibilité PDF |
| `/api/tarot/domaines` | GET | Non | 6 domaines de questions |
| `/api/tarot/marseille` | POST | Non | Tirage 3 cartes |
| `/api/tarot/celtique` | POST | Non | Tirage Croix Celtique 10 cartes |

## Backlog

### P0 — En cours
- [ ] Intégrer le gating crédits dans les pages frontend des services (TarotOuiNon, TirageTarot, etc.)
- [ ] Convertir tous les services premium au système de crédits

### P1 — À faire
- [ ] Page historique des transactions pour l'utilisateur
- [ ] Compléter l'intégration Astrology API (natal_wheel_chart, enrichment)
- [ ] Améliorer la mise en page du PDF thème astral principal

### P2 — Nice to have
- [ ] Visualisation natal_wheel_chart
- [ ] PDF de synthèse du tirage tarot
- [ ] Historique des tirages par utilisateur
- [ ] Partage social des tirages
- [ ] Page de vente optimisée / modèle abonnement

## Dernière mise à jour
6 Mars 2026 — Système de crédits Phase 1-4 backend + frontend complet
