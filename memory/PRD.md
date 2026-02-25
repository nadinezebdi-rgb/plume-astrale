# Plume Astrale - PRD

## Date de mise à jour
25 Février 2026

## Architecture
- Frontend: React 19 + Tailwind + shadcn/ui
- Backend: FastAPI + MongoDB
- PDF: ReportLab (custom) + AstrologyAPI PDF (pro)
- Paiement: Stripe via emergentintegrations

## Structure Tarifaire

| Produit | Prix | Type |
|---------|------|------|
| Theme Astral Pro | 24,90€ | PDF 68 pages (AstrologyAPI) |
| Compatibilite Astrale | 29,90€ | PDF 24 pages (AstrologyAPI) |
| Tarologie & Mediumnite | 35,00€ | PDF custom + 7 cartes |
| Tarot Oui/Non | 4,99€ | Consultation arcane |
| Livre physique | 49,90€ | Version imprimée |
| Abonnement Quotidien | 14,99€/mois | A FAIRE |

## Codes Promo
- **ASTRO100** : 100% gratuit sur le manuscrit uniquement
- **PLUME2026** : 100% gratuit sur TOUS les services

## Pages
| Route | Page | Statut |
|-------|------|--------|
| / | Accueil ("Devenez qui vous etes") | OK |
| /formulaire | Formulaire 6 étapes (avec genre) | OK |
| /apercu | Aperçu + preview PDF | OK |
| /resultats | Résultats + PDF Pro download | OK |
| /compatibilite-amoureuse | Compatibilité (produit d'appel) | OK |
| /quotidien | Guidance quotidienne 12 signes | OK |
| /tarot-oui-non | Tarot Oui/Non avec images | OK |
| /tarologie | Tarologie & Médiumnité | OK |
| /livre | Commande livre physique | OK |

## Assets
- 12 illustrations zodiacales (fournies par l'utilisateur) - /app/backend/assets/zodiac/
- 22 cartes Tarot de Marseille (générées IA, style ésotérique or/noir) - /app/backend/assets/tarot/

## API Endpoints
- GET /api/daily/{sign} - Contenu quotidien
- POST /api/tarot/oui-non - Tirage Oui/Non
- POST /api/tarologie/tirage - Tirage 7 cartes
- POST /api/tarologie/pdf - PDF médiumnité
- POST /api/pdf/preview - Aperçu visuel PDF
- POST /api/pdf/pro-horoscope - PDF Pro 68 pages
- POST /api/pdf/generate - PDF custom (fallback)
- POST /api/compatibility/generate - Compatibilité 24 pages
- POST /api/checkout/create - Session Stripe
- POST /api/discount/validate - Valider code promo
- POST /api/access/free - Accès gratuit
- POST /api/order/book - Commander livre
- GET /api/assets/* - Images statiques

## Backlog
- [ ] Abonnement mensuel 14,99€/mois (Stripe Subscription)
- [ ] Déploiement Railway
- [ ] Dashboard admin KPIs
- [ ] Print-on-Demand livre physique
- [ ] Emails automatiques
