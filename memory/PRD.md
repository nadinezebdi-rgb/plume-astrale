# Plume Astrale - PRD

## Projet
**Plume Astrale** - Plateforme de guidance astrologique et symbolique

## Architecture
- **Frontend**: React.js + Tailwind CSS + Shadcn UI
- **Backend**: Python FastAPI
- **Base de données**: MongoDB (users, user_wallets, credit_transactions, streaks, payment_transactions)
- **Paiement**: Stripe (via emergentintegrations)
- **Auth**: JWT (PyJWT + bcrypt)
- **APIs**: Astrology API (Plan Growth)

## Implémenté — Session 6 Mars 2026

### Système de Crédits (Phases 1-4)
- Auth JWT : inscription profil astrologique + 20 crédits bonus, connexion, /me
- Wallet : solde, transactions, bonus quotidien (+1/jour)
- Stripe : 3 packs (Découverte 10cr/9€, Exploration 50cr/24,99€, Premium 100cr/44,99€)
- Gating crédits sur tous les services premium
- Page Acheter des crédits optimisée Gary Vee (projections, "Le plus choisi", CTAs)

### Codes Promo
- PLUMEASTRALE (100cr), TESTPLUME (200cr), BIENVENUE (50cr)
- UI : bouton "J'ai un code promo" sur page achat

### Contenu Enrichi
- Numérologie : section éducative (Qu'est-ce que?, Nombres clés, À qui s'adresse)
- Tarologie : intro éducative (Qu'est-ce que?, À quoi ça sert?, 5 positions Croix)

### Le Cercle — Hub Communautaire
- Page /cercle : insights quotidiens, carte du jour, zodiac, services
- Accessible depuis Navbar et Accueil

### Streak System
- Check-in quotidien : +1 crédit/jour
- Paliers bonus : 7j (+3cr), 14j (+5cr), 30j (+10cr), 60j (+15cr), 100j (+25cr)
- Streak brisé si un jour manqué → retour à 1
- Visual : flamme avec badge compteur, barre de progression, timeline 5 paliers
- Popup récompense après check-in (modal avec flamme, crédits gagnés, prochain palier)
- Collection MongoDB : streaks {user_id, streak_count, longest_streak, total_checkins, last_checkin}
- Endpoints : GET /api/streak/status, POST /api/streak/checkin

## Tests — 100% pass rate
- Iteration 19: Auth + Wallet + Credits (21/21)
- Iteration 20: Credit Gating frontend (13/13)
- Iteration 21: Promo codes + Education + Cercle (12/12)
- Iteration 22: Streak system (9/9 + all frontend flows)

## Backlog

### P1
- [ ] Page historique des transactions
- [ ] Insights du Cercle dynamiques (API quotidienne)
- [ ] Intégration Astrology API enrichie (natal_wheel_chart)

### P2
- [ ] Visualisation natal_wheel_chart
- [ ] PDF synthèse tirage tarot
- [ ] Historique tirages par utilisateur
- [ ] Système de parrainage (+5cr par ami)
- [ ] Page de vente optimisée / abonnement

## Dernière mise à jour
6 Mars 2026 — Streak system complet + tests 100%
