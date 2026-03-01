# Plume Astrale - PRD

## Date: 01 Mars 2026

## Produit
Espace digital de guidance symbolique, alliant calculs astrologiques precis et interpretation experte pour accompagner avec clarte et discernement.

## Deploiement
- **VPS Hostinger** : plume-astrale.fr (Docker Compose + Nginx + SSL)
- **Github** : https://github.com/nadinezebdi-rgb/plume-astrale
- **Code Promo** : PLUME2026 (acces gratuit a tout)

## Direction Artistique (v2 — Mars 2026)
- **Inspiration** : Aesop, Apple, editorial haut de gamme
- **Fond** : #0B0B0F (noir profond et subtil)
- **Texte** : #E8E4DD (headings), #A9A5A0 (body), #6B6862 (muted)
- **Accent** : #C4A882 (or antique subtil)
- **Typographie** : Cormorant Garamond (headings), DM Sans (body)
- **Boutons** : Ghost buttons avec bordures fines
- **Cartes** : Pas de cadres lourds, separations fluides
- **Ton** : Chaleureux, responsable, non sensationnaliste

## Completed - 28 Fev 2026

### 1. Enrichissement PDF "Theme Astral Pro" (V4) — 28+ pages
### 2. Carte Astrale Partageable (Instagram/WhatsApp)
### 3. Integration AstrologyAPI Phase 1
### 4. Refonte Page d'Accueil + Flux Tarot Oui/Non
### 5. Numerologie + Traduction IA
### 6. Code Promo PLUME2026 sur toutes les pages de paiement

## Completed - 01 Mars 2026

### 7. Refonte Design Editoriale Complete
- Nouvelle direction artistique : abandon SaaS mystique, passage editorialde type Aesop/Apple
- Nouveau systeme CSS avec variables (--pa-bg, --pa-heading, --pa-body, --pa-accent)
- Fonts : Cormorant Garamond (headings) + DM Sans (body)
- Homepage redesignee : 8 sections editoriales avec contenu fourni par l'utilisateur
  - Hero, Notre Cadre, Reponse Immediate, Comprehension Approfondie, Notre Methode, Pour Aller Plus Loin, Notre Posture, Section Finale
- Navbar editorial : cachee sur la homepage, visible sur les pages interieures
- Pages interieures redesignees : Formulaire (step-by-step epure), TarotOuiNon, Numerologie, Quotidien, Apercu, Choix, Paiement, Tarologie, Livre, Compatibilite, Compatibilite2
- Toute la logique metier preservee (codes promo, paiements, APIs)
- Tests : 100% backend (10/10) + 100% frontend (iteration_13)

## Architecture Actuelle
```
/app/backend/
  server.py                    # FastAPI - tous les endpoints
  services/
    astrology_api.py           # Client AstrologyAPI
    astro_content.py           # Contenu astrologique de base
    astro_content_extended.py  # Contenu etendu
    pdf_generator_v2.py        # Generateur PDF 28+ pages
    share_card_generator.py    # Generateur carte partageable
    translation_service.py     # Traduction IA (Emergent LLM key)
    tarot_service.py           # Service tarot local
    daily_content.py           # Contenu quotidien
    pdf_service.py             # PDF legacy
    astrology_pdf_api.py       # PDF API legacy

/app/frontend/src/
  index.css                    # Systeme de design editorial complet
  pages/
    Index.js                   # Homepage (8 sections editoriales)
    TarotOuiNon.js             # Tarot Oui/Non
    Numerologie.js             # Profil numerologique
    Quotidien.js               # Guidance du jour + phase lunaire
    Formulaire.js              # Formulaire step-by-step
    Apercu.js                  # Apercu + upsell
    Choix.js                   # Selection de plan
    Paiement.js                # Finalisation paiement + promo
    Tarologie.js               # Tarologie + promo
    Compatibilite.js           # Compatibilite simple + promo
    Compatibilite2.js          # Compatibilite detaillee + promo
    Livre.js                   # Commande livre + promo
    Resultats.js               # Resultats + partage social + promo
  components/
    Navbar.js                  # Navigation editoriale
```

## Backlog

### P1 - Prochaines etapes
- [ ] Integration SendGrid (emails captures Tarot + newsletter)
- [ ] Endpoints Growth (quand user upgrade): Tarot API, Synastry, Zodiac Compatibility, Natal Interpretations
- [ ] Upsell Tarot approfondi (29 EUR)
- [ ] Upsell "Lecture Clarte" Astrologie (49 EUR)

### P2
- [ ] Cartographie annuelle Premium (199 EUR) - Solar Return API
- [ ] Abonnement Stripe 14,99 EUR/mois - Transit API
- [ ] Tableau de bord admin

### P3
- [ ] Emails automatiques, React Context, deploy.sh
- [ ] Nettoyage fichiers legacy (pdf_service.py, astrology_pdf_api.py)
- [ ] Accents francais dans les textes (actuellement sans accents pour compatibilite)

## Notes
- Deploiement MANUEL par l'utilisateur sur son VPS
- BLOCKER : Plan AstrologyAPI Growth ($99/mois) requis pour fonctionnalites avancees
- Toute nouvelle donnee API doit passer par translation_service.py (anglais -> francais)
