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
- Application complète : accueil, formulaire thème astral, numérologie, tarologie, compatibilité, quotidien, horoscope
- Génération PDF thème astral (28+ pages)
- Tirages Tarot (Oui/Non, Croix, Marseille, Celtique)
- Premium Landing & Parcours guidé
- Rapport de Compatibilité Astrale enrichi (11 pages PDF)
- Tirage du Jour gratuit
- Correction accents français, health check Kubernetes

### Session du 6 Mars 2026 — Système de Crédits Complet

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
- `POST /api/credits/checkout` — session Stripe pour achat (protégé)
- `GET /api/credits/checkout/status/{session_id}` — polling + ajout crédits (protégé)
- Packs : Découverte (10 cr / 9€), Exploration (50 cr / 24,99€), Premium (100 cr / 44,99€)

#### Phase 3 : Frontend Auth & UI
- `AuthContext` global (register, login, logout, useCredits, refreshBalance)
- Page Connexion (`/connexion`)
- Page Inscription 2 étapes (`/inscription`) — identifiants + profil astrologique (input heure 24h)
- Page Acheter des crédits (`/acheter-credits`) — optimisée Gary Vee :
  - Projections d'usage par pack
  - Badge "Le plus choisi" sur Exploration
  - Note "Les crédits n'expirent pas"
  - Rappel "expérience personnalisée"
  - Table des coûts de services
  - CTAs "Continuer l'exploration" (tirage, thème, numérologie)
  - Banner "20 crédits offerts à l'inscription"
- Page Succès paiement crédits (`/credits/succes`)
- Navbar : solde crédits/Déconnexion (connecté) ou Connexion/Inscription (déconnecté)

#### Phase 4 : Gating des services par crédits
Tous les services premium requièrent connexion + déduction crédits côté serveur :
- **Tarot Oui/Non** : 1er tirage gratuit par compte, puis 2 crédits
- **Tirage Tarot** (Marseille/Celtique) : 10 crédits (gate step 0)
- **Numérologie** : 10 crédits (gate inline)
- **Compatibilité Amoureuse** : 10 crédits (gate step 0)
- **Cartographie Premium** : 60 crédits (gate full-screen)
- Composant réutilisable `CreditGate.js` disponible
- Chaque page affiche le coût, le solde, et redirige vers achat si insuffisant

## Endpoints API

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/health` | GET | Non | Health check |
| `/api/auth/register` | POST | Non | Inscription + 20 crédits |
| `/api/auth/login` | POST | Non | Connexion JWT |
| `/api/auth/me` | GET | Oui | Profil + solde |
| `/api/wallet/balance` | GET | Oui | Solde crédits |
| `/api/wallet/transactions` | GET | Oui | Historique transactions |
| `/api/credits/packs` | GET | Non | Packs disponibles |
| `/api/credits/service-costs` | GET | Non | Coûts des services |
| `/api/credits/checkout` | POST | Oui | Checkout Stripe |
| `/api/credits/checkout/status/{id}` | GET | Oui | Statut paiement |
| `/api/credits/use` | POST | Oui | Déduction crédits |
| `/api/credits/check-free-tarot` | GET | Oui | Vérif tirage gratuit |

## Backlog

### P1 — À faire
- [ ] Page historique des transactions pour l'utilisateur
- [ ] Compléter l'intégration Astrology API (natal_wheel_chart, enrichment)

### P2 — Nice to have
- [ ] Visualisation natal_wheel_chart
- [ ] PDF de synthèse du tirage tarot
- [ ] Historique des tirages par utilisateur
- [ ] Partage social des tirages
- [ ] Page de vente optimisée / modèle abonnement
- [ ] Système de parrainage (+5 crédits par ami inscrit)

## Dernière mise à jour
6 Mars 2026 — Système de crédits complet (Phases 1-4) + Améliorations Gary Vee
