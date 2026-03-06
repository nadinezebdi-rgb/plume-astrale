# Plume Astrale - PRD

## Projet
**Plume Astrale** - Plateforme de guidance astrologique et symbolique

## Architecture
- **Frontend**: React.js + Tailwind CSS + Shadcn UI
- **Backend**: Python FastAPI
- **Base de donnees**: MongoDB (users, user_wallets, credit_transactions, streaks, payment_transactions)
- **Paiement**: Stripe (via emergentintegrations)
- **Auth**: JWT (PyJWT + bcrypt)
- **APIs**: Astrology API (Plan Growth)

## Implemente — Session 6 Mars 2026

### Systeme de Credits (Phases 1-4)
- Auth JWT : inscription profil astrologique + 20 credits bonus, connexion, /me
- Wallet : solde, transactions, bonus quotidien (+1/jour)
- Stripe : 3 packs (Decouverte 10cr/9eur, Exploration 50cr/24,99eur, Premium 100cr/44,99eur)
- Gating credits sur tous les services premium
- Page Acheter des credits optimisee Gary Vee (projections, "Le plus choisi", CTAs)

### Codes Promo
- PLUMEASTRALE (100cr), TESTPLUME (200cr), BIENVENUE (50cr)
- UI : bouton "J'ai un code promo" sur page achat

### Contenu Enrichi
- Numerologie : section educative (Qu'est-ce que?, Nombres cles, A qui s'adresse)
- Tarologie : intro educative (Qu'est-ce que?, A quoi ca sert?, 5 positions Croix)

### Le Cercle — Hub Communautaire
- Page /cercle : insights quotidiens, carte du jour, zodiac, services
- Accessible depuis Navbar et Accueil

### Streak System
- Check-in quotidien : +1 credit/jour
- Paliers bonus : 7j (+3cr), 14j (+5cr), 30j (+10cr), 60j (+15cr), 100j (+25cr)
- Streak brise si un jour manque -> retour a 1
- Visual : flamme avec badge compteur, barre de progression, timeline 5 paliers
- Popup recompense apres check-in (modal avec flamme, credits gagnes, prochain palier)
- Collection MongoDB : streaks {user_id, streak_count, longest_streak, total_checkins, last_checkin}
- Endpoints : GET /api/streak/status, POST /api/streak/checkin

### Homepage Cosmique Interactive (6 Mars 2026)
- Fond anime avec etoiles, etoiles filantes, nebuleuses, effet parallaxe souris
- Roue natale interactive SVG (12 signes zodiac, 7 planetes, rotation continue, hover interactif)
- Widget "Indice Cosmique" avec barres de progression animees (Amour, Carriere, Energie, Intuition)
- Carte profil cosmique partageable (telechargement PNG 1080x1350 via /api/share/generate-card)
- Sections: Hero, Roue Natale, Tirage du Jour, Indice Cosmique, Services (6 cartes), Le Cercle CTA, Final CTA
- Composants: NatalWheel.js, ShareableCard.js, CosmicBg (canvas), CosmicScore

## Tests — 100% pass rate
- Iteration 19: Auth + Wallet + Credits (21/21)
- Iteration 20: Credit Gating frontend (13/13)
- Iteration 21: Promo codes + Education + Cercle (12/12)
- Iteration 22: Streak system (9/9 + all frontend flows)
- Iteration 23: Homepage cosmique interactive (16/16 backend + all frontend verified)

## Backlog

### P1
- [ ] Page historique des transactions
- [ ] Enrichir contenu Numerologie (donnees API dynamiques au lieu de texte statique)
- [ ] Enrichir contenu Tarologie (interpretations plus profondes)
- [ ] Bonus automatique "1 credit gratuit/jour" (au lieu du check-in manuel)

### P2
- [ ] Integration Astrology API enrichie (natal_wheel_chart, planet reports)
- [ ] Personnaliser les scores "Alignement Cosmique" avec donnees utilisateur
- [ ] PDF synthese tirage tarot
- [ ] Historique tirages par utilisateur
- [ ] Systeme de parrainage (+5cr par ami)
- [ ] Page de vente optimisee / abonnement

## Derniere mise a jour
6 Mars 2026 — Homepage cosmique interactive complete + tests 100%
