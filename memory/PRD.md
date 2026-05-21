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

### Homepage Cosmique Interactive (6 Mars 2026)
- Fond anime avec etoiles brillantes, etoiles filantes, nebuleuses, parallaxe souris
- 400 etoiles canvas + 260 etoiles CSS avec halos lumineux dores/blancs
- Roue natale interactive SVG (12 signes zodiac, 7 planetes, rotation continue, hover)
- Widget "Indice Cosmique" avec barres animees (Amour, Carriere, Energie, Intuition)
- Carte profil cosmique partageable (PNG 1080x1350)
- Navbar doree 13px avec Cinzel + text-shadow dore

## Tests — 100% pass rate
- Iteration 23: Homepage cosmique interactive (16/16 backend + all frontend verified)

## Backlog

### P1
- [ ] Page historique des transactions
- [ ] Enrichir contenu Numerologie (donnees API dynamiques)
- [ ] Enrichir contenu Tarologie (interpretations plus profondes)
- [ ] Bonus automatique "1 credit gratuit/jour"

### P2
- [ ] Personnaliser les scores Alignement Cosmique avec donnees utilisateur
- [ ] Integration Astrology API enrichie
- [ ] PDF synthese tirage tarot
- [ ] Historique tirages par utilisateur
- [ ] Systeme de parrainage (+5cr par ami)

### Chat IA Astral (21 Mai 2026)
- Page /chat-astral connectee a AstrologyAPI AstroChat (json-chat.astrologyapi.com/api/chat)
- Reponses 100% en francais (language: "fr" + Accept-Language: fr)
- Gating : 3 messages gratuits anonymes (localStorage), puis CTA inscription
- Cout : 2 credits/message pour utilisateurs connectes (deduction via /api/credits/use)
- Pre-remplissage donnees natales depuis profil auth + fallback localStorage
- Body API complet : KUNDLI/WESTERN/STANDARD/astro-6
- Auth : Access Token (x-astrologyapi-key) prioritaire, fallback Basic Auth
- Variable env : ASTROLOGY_API_ACCESS_TOKEN (a ajouter quand active sur dashboard)
- Diagnostic clair quand produit AstroChat non actif sur le compte

### Packs Crédits Chat (21 Mai 2026)
- 3 nouveaux packs dedies au Chat dans /acheter-credits :
  - Lueur : 10 messages (20cr) / 4,99 EUR
  - Constellation : 30 messages (60cr) / 12,99 EUR — "Le plus choisi"
  - Voie Lactee : 75 messages (150cr) / 24,99 EUR — "Meilleure valeur"
- Section dediee + section "Packs Univers Complet" conservee
- Service "Chat Astral IA" ajoute dans le tableau des couts

## Derniere mise a jour
21 Mai 2026 — Chat IA AstrologyAPI en francais + packs conversation
