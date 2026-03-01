# Plume Astrale - PRD

## Date: 01 Mars 2026

## Produit
Espace digital de guidance symbolique, alliant calculs astrologiques precis et interpretation experte.

## Domaine
https://plume-astrale.fr

## Direction Artistique (v3)
- Fond violet profond (#0C0918) avec etoiles scintillantes et orbes
- Ecriture doree (#C5A059), headings (#F0E6D3)
- Typo: Cormorant Garamond (headings), DM Sans (body)
- Symboles: plume doree (hero), soleil dore (section astrologie)
- Code Promo: PLUME2026

## Tech Stack
- Frontend: React, React Router, TailwindCSS, Lucide React, react-helmet-async
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
    - Backend: premium_service.py, premium_pdf_generator.py, endpoints /api/premium/generate + /api/premium/pdf
    - Frontend: PremiumLanding.js, PremiumExperience.js (parcours guide 5 etapes avec sidebar)
    - Tests: 100% backend + frontend
11. **SEO Complet** (01 Mars 2026):
    - react-helmet-async: meta tags dynamiques par page (title, description, keywords, OG, Twitter)
    - JSON-LD structured data (WebSite + ProfessionalService + OfferCatalog)
    - sitemap.xml (9 pages publiques avec priorites et frequences)
    - robots.txt (crawl autorise, pages privees exclues)
    - Canonical URLs pointant vers plume-astrale.fr
    - Open Graph + Twitter Cards avec image generee
    - Nettoyage fonts inutilisees (Cinzel/Quicksand supprimees)
    - SEO ajoute sur: Index, Premium, TarotOuiNon, Formulaire, Numerologie, Quotidien, Tarologie, Compatibilite, Horoscope

## Backlog
### P1
- [ ] Integration emails (SendGrid/Resend/Brevo) — capture leads + envoi PDF
- [ ] Endpoints Growth AstrologyAPI (bloque par plan utilisateur)

### P2
- [ ] Abonnement Stripe 14,99 EUR/mois (contenu recurrent)
- [ ] Tableau de bord admin

### P3
- [ ] Emails automatiques relance
- [ ] React Context pour etat global
- [ ] Script de deploiement automatise

## Architecture
```
/app
├── backend
│   ├── server.py
│   ├── services/
│   │   ├── premium_service.py
│   │   ├── premium_pdf_generator.py
│   │   ├── pdf_generator_v2.py
│   │   ├── translation_service.py
│   │   ├── tarot_service.py
│   │   └── ...
├── frontend
│   ├── public/
│   │   ├── index.html              (meta tags, JSON-LD, OG)
│   │   ├── sitemap.xml
│   │   └── robots.txt
│   └── src/
│       ├── components/
│       │   ├── SEO.js              (meta tags dynamiques par page)
│       │   ├── Navbar.js
│       │   └── StarField/
│       ├── pages/
│       │   ├── Index.js
│       │   ├── PremiumLanding.js
│       │   ├── PremiumExperience.js
│       │   └── ...
│       └── index.js                (HelmetProvider)
```
