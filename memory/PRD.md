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

### Sessions précédentes
- Application complète : accueil, formulaire thème astral, numérologie, tarologie, compatibilité, quotidien, horoscope
- Génération PDF thème astral (28+ pages), Tirages Tarot multiples, Premium Landing & Parcours
- Rapport de Compatibilité Astrale enrichi (11 pages PDF), Tirage du Jour gratuit
- Correction accents français, health check Kubernetes

### Session du 6 Mars 2026

#### Système de Crédits (Phases 1-4)
- Auth JWT : inscription avec profil astrologique + 20 crédits bonus, connexion, /me
- Wallet : solde, historique transactions, bonus quotidien (+1/jour dès J+1)
- Stripe : 3 packs (Découverte 10cr/9€, Exploration 50cr/24,99€, Premium 100cr/44,99€)
- Gating crédits sur tous les services premium
- Page Acheter des crédits optimisée (projections usage, "Le plus choisi", no-expiry, CTAs)

#### Codes Promo
- `POST /api/credits/promo` — application de codes promo (un usage par user)
- Codes : PLUMEASTRALE (100cr), TESTPLUME (200cr), BIENVENUE (50cr)
- UI : bouton "J'ai un code promo" sur la page achat de crédits

#### Contenu enrichi
- **Numérologie** : section éducative complète (Qu'est-ce que?, Nombres clés, À qui s'adresse), CTA avant formulaire
- **Tarologie** : intro éducative (Qu'est-ce que?, À quoi ça sert?, 5 positions du tirage en Croix), CTA avant formulaire

#### Le Cercle — Hub communautaire
- Page `/cercle` accessible depuis la Navbar et l'accueil
- 3 insights quotidiens (Énergie, Nombre, Arcane du jour)
- Carte du jour depuis l'API `/api/tarot/jour`
- Sélecteur de zodiaque (12 signes, auto-détection depuis date de naissance)
- Navigation vers les 6 services avec coûts en crédits
- Footer crédits (connecté) ou CTA inscription (déconnecté)

## Backlog

### P1 — À faire
- [ ] Page historique des transactions pour l'utilisateur
- [ ] Rendre les insights du Cercle dynamiques (API quotidienne)
- [ ] Compléter l'intégration Astrology API (natal_wheel_chart)

### P2 — Nice to have
- [ ] Visualisation natal_wheel_chart
- [ ] PDF synthèse tirage tarot
- [ ] Historique des tirages par utilisateur
- [ ] Système de parrainage (+5 crédits par ami)
- [ ] Page de vente optimisée / modèle abonnement

## Dernière mise à jour
6 Mars 2026 — Codes promo, contenu éducatif enrichi, Le Cercle
