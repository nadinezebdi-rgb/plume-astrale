# Plume Astrale - PRD

## Date: 01 Mars 2026

## Produit
Plateforme esoterique complete proposant des analyses astrologiques, numerologiques et de tarologie personnalisees.

## Deploiement
- **VPS Hostinger** : plume-astrale.fr (Docker Compose + Nginx + SSL)
- **Github** : https://github.com/nadinezebdi-rgb/plume-astrale
- **Code Promo** : PLUME2026 (acces gratuit a tout)

## Completed - 28 Fev 2026

### 1. Enrichissement PDF "Theme Astral Pro" (V4) — 28+ pages
- Carte du ciel SVG reelle (AstrologyAPI natal_wheel_chart)
- Equilibre elementaire, aspects, retrogrades, Chiron/Lilith/Noeud Nord
- Tests: 22/22 (iteration_7)

### 2. Carte Astrale Partageable (Instagram/WhatsApp)
- PNG 1080x1350 avec profil astral + 3 boutons partage
- Tests: 13/13 (iteration_8)

### 3. Integration AstrologyAPI Phase 1
- natal_wheel_chart SVG dans le PDF, moon_phase_report en francais sur /quotidien
- Tests: 20/20 (iteration_9)

### 4. Refonte Page d'Accueil + Flux Tarot Oui/Non
- 2 CTAs principaux (Tarot/Astrologie) + section "Nos Services"
- Compteur 3 tirages gratuits + formulaire capture donnees natales au 4eme
- Tests: 12/12 (iteration_10)

### 5. Numerologie + Traduction IA
- Page /numerologie complete (chemin de vie, expression, ame, personnalite, anniversaire, annee personnelle)
- Service de traduction GPT-4o-mini via Emergent LLM key (cache en memoire)
- Tests: 12/12 (iteration_11)

## Completed - 01 Mars 2026

### 6. Code Promo PLUME2026 sur toutes les pages de paiement
- Ajoute sur: Paiement.js, Livre.js, Compatibilite.js
- Deja present sur: Tarologie.js, Compatibilite2.js, Apercu.js, Resultats.js
- 7 pages de paiement au total avec code promo fonctionnel
- Tests: 13/13 (iteration_12)

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
  pages/
    Index.js                   # Accueil (2 CTAs + Nos Services)
    TarotOuiNon.js             # Tarot Oui/Non (3 tirages gratuits)
    Numerologie.js             # Profil numerologique (gratuit)
    Quotidien.js               # Guidance du jour + phase lunaire
    Resultats.js               # Resultats + partage social + promo
    Formulaire.js              # Formulaire astrologie
    Tarologie.js               # Tarologie complete + promo
    Compatibilite.js           # Compatibilite simple + promo
    Compatibilite2.js          # Compatibilite detaillee + promo
    Apercu.js                  # Apercu du manuscrit + promo
    Paiement.js                # Finalisation paiement + promo
    Livre.js                   # Commande livre physique + promo
    Choix.js                   # Selection de plan
  components/
    Navbar.js                  # Navigation
```

## Endpoints API
| Methode | Route | Description |
|---------|-------|-------------|
| POST | /api/numerology/complete | Profil numerologique complet |
| POST | /api/translate | Traduction IA anglais->francais |
| POST | /api/share/generate-card | Carte partageable PNG |
| POST | /api/pdf/pro-horoscope | PDF Theme Astral Pro |
| POST | /api/pdf/generate | PDF alternatif |
| POST | /api/pdf/preview | Apercu PDF |
| POST | /api/tarot/oui-non | Tirage Oui/Non |
| GET | /api/moon-phase | Phase lunaire actuelle |
| GET | /api/daily/{sign} | Guidance du jour + lune |
| POST | /api/discount/validate | Validation code promo |
| POST | /api/access/free | Acces gratuit via code promo |
| POST | /api/checkout/create | Creation session Stripe |

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
- [ ] Print-on-Demand, emails automatiques, React Context, deploy.sh
- [ ] Nettoyage fichiers legacy (pdf_service.py, astrology_pdf_api.py)

## Notes API AstrologyAPI
- Plan Starter actuel: planets, western_horoscope, natal_wheel_chart, house_cusps, moon_phase, geo_details
- Plan Growth (99$/mois recommande): +Tarot, Synastry, Compatibility, Natal Interpretations, Numerology avancee
- Plan Business (199$/mois): +Daily/Monthly Horoscope, Solar Return, Transits

## Deploiement Manuel
L'utilisateur doit executer les commandes suivantes sur son VPS:
```bash
cd /root/plume-astrale
git pull origin main
docker compose down
docker compose up -d --build
```
