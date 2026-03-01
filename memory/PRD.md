# Plume Astrale - PRD

## Date: 01 Mars 2026

## Produit
Espace digital de guidance symbolique, alliant calculs astrologiques precis et interpretation experte.

## Direction Artistique (v3)
- Fond violet profond (#0C0918) avec etoiles scintillantes et orbes
- Ecriture doree (#C5A059), headings (#F0E6D3)
- Typo: Cormorant Garamond (headings), DM Sans (body)
- Symboles: plume doree (hero), soleil dore (section astrologie)
- Code Promo: PLUME2026

## Tech Stack
- Frontend: React, React Router, TailwindCSS, Lucide React
- Backend: FastAPI (Python), reportlab (PDF), emergentintegrations (LLM + Stripe)
- APIs: AstrologyAPI, Emergent LLM (gpt-4o-mini) pour traduction + interpretations
- Paiement: Stripe
- Deploiement: Docker Compose, Nginx (manuel par l'utilisateur)

## Completed
1. PDF Theme Astral Pro 28+ pages
2. Carte Astrale Partageable PNG
3. Integration AstrologyAPI Phase 1
4. Flux Tarot Oui/Non (3 tirages gratuits)
5. Numerologie + Traduction IA
6. Code Promo PLUME2026 toutes pages
7. Refonte design editoriale complete
8. Retour violet + etoiles scintillantes
9. Integration symboles (plume + soleil), espaces resserres, titre agrandi
10. **Experience Premium 199 EUR** (01 Mars 2026):
    - Backend: premium_service.py (generation contenu LLM 5 etapes), premium_pdf_generator.py (PDF violet/dore)
    - Endpoints: /api/premium/generate, /api/premium/pdf
    - Frontend: PremiumLanding.js (page de vente), PremiumExperience.js (parcours guide avec sidebar)
    - Parcours guide en 5 etapes: Fondement, Chemin d'Ame, Cycle Actuel, Schemas Repetitifs, Projection 12 Mois
    - Menu lateral avec progression, acces libre apres completion
    - PDF Premium telechargeale apres parcours complet
    - Code promo PLUME2026 fonctionne pour acces gratuit
    - Lien Premium dore dans la navbar + CTA sur homepage
    - Tests: 100% backend (12/12) + 100% frontend

## Backlog
### P1
- [ ] Integration SendGrid (emails + newsletter)
- [ ] Endpoints Growth AstrologyAPI (bloque par plan utilisateur)

### P2
- [ ] Abonnement Stripe 14,99 EUR/mois (contenu recurrent)
- [ ] Tableau de bord admin

### P3
- [ ] Emails automatiques
- [ ] React Context pour etat global
- [ ] Script de deploiement automatise
- [ ] Nettoyage fichiers legacy

## Architecture
```
/app
├── backend
│   ├── server.py                    (API principale)
│   ├── services/
│   │   ├── astrology_api.py         (AstrologyAPI)
│   │   ├── translation_service.py   (LLM traduction)
│   │   ├── premium_service.py       (contenu LLM 5 etapes)
│   │   ├── premium_pdf_generator.py (PDF Premium)
│   │   ├── pdf_generator_v2.py      (PDF Theme Astral)
│   │   ├── tarot_service.py         (Tarot Oui/Non + En Croix)
│   │   └── ...
│   └── tests/
├── frontend/src
│   ├── App.js                       (routes + StarField global)
│   ├── components/
│   │   ├── Navbar.js                (nav + lien Premium dore)
│   │   └── StarField/
│   ├── pages/
│   │   ├── Index.js                 (accueil + CTA Premium)
│   │   ├── PremiumLanding.js        (page vente 199 EUR)
│   │   ├── PremiumExperience.js     (parcours guide 5 etapes)
│   │   ├── Formulaire.js            (saisie donnees naissance)
│   │   └── ...
│   └── index.css                    (design system violet/dore)
```
