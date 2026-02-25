# Plume Astrale - PRD (Product Requirements Document)

## Projet
Application de génération de thèmes astraux et chemins d'âme - Un outil spirituel combinant numérologie, astrologie, tarot et lecture d'âme.

## Date de mise à jour
25 Février 2026 (Session 5 - Contenu quotidien + Tarot + Tarologie + PDF Preview)

## Architecture technique
- **Frontend**: React 19 + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI (Python), uvicorn
- **PDF**: ReportLab (canvas) + PyMuPDF (previews)
- **Paiement**: Stripe via emergentintegrations
- **Données Astro**: AstrologyAPI (plan Starter)
- **Base de données**: MongoDB (transactions, commandes)

## Structure Tarifaire

| Produit | Prix | Type | Description |
|---------|------|------|-------------|
| Le Manuscrit de la Plume | 29,90€ | PDF unique | Guide spirituel complet (~15 pages avec illustrations) |
| Le Livre de la Plume | 49,90€ | Livre physique | Version imprimée reliée |
| Tarot Oui/Non | 4,99€ | Consultation | Tirage d'un Arcane Majeur |
| Tarologie & Médiumnité | 35,00€ | PDF + lecture | 7 cartes + lecture médiumnique + PDF |
| Abonnement Quotidien | 14,99€/mois | Abonnement | Horoscope, conseils, phrase du jour (A FAIRE) |

Code promo: **ASTRO100** = accès gratuit au manuscrit

## Pages Frontend

| Route | Page | Statut |
|-------|------|--------|
| `/` | Page d'accueil | OK |
| `/formulaire` | Formulaire 5 étapes | OK |
| `/apercu` | Aperçu gratuit + prévisualisation PDF | OK |
| `/resultats` | Résultats complets + téléchargement PDF | OK |
| `/quotidien` | Guidance quotidienne (12 signes) | OK - NOUVEAU |
| `/tarot-oui-non` | Tarot Oui/Non | OK - NOUVEAU |
| `/tarologie` | Tarologie & Médiumnité | OK - NOUVEAU |
| `/paiement` | Page de paiement | OK |
| `/paiement/succes` | Confirmation paiement | OK |
| `/livre` | Commande livre physique | OK |
| `/commande/succes` | Confirmation commande livre | OK |
| `/tarot` | Tarot avancé (premium) | OK |
| `/compatibilite` | Compatibilité (premium) | OK |
| `/horoscope` | Horoscope | OK |

## Key API Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/daily/{sign}` | Contenu quotidien par signe | NOUVEAU |
| POST | `/api/tarot/oui-non` | Tirage Tarot Oui/Non | NOUVEAU |
| POST | `/api/tarologie/tirage` | Tirage 7 cartes médiumnité | NOUVEAU |
| POST | `/api/tarologie/pdf` | PDF tarologie médiumnité | NOUVEAU |
| POST | `/api/pdf/preview` | Aperçu visuel des pages du PDF | NOUVEAU |
| POST | `/api/checkout/create` | Créer session Stripe |
| POST | `/api/discount/validate` | Valider code promo |
| POST | `/api/access/free` | Accès gratuit avec code promo |
| POST | `/api/astrology/planets` | Positions planétaires |
| POST | `/api/pdf/generate` | Générer PDF manuscrit |
| POST | `/api/order/book` | Commander livre physique |

## Ce qui a été implémenté

### Session 1-3 (Précédent)
- Design ésotérique complet, formulaire rituel, flux freemium
- Stripe, AstrologyAPI, PDF manuscrit, livre physique

### Session 4 - Images zodiacales
- 12 illustrations de signes du zodiaque dans le PDF
- Images optimisées (PNG→JPEG 800px)

### Session 5 - Nouvelles fonctionnalités (25 Feb 2026)
- **Contenu quotidien intelligent**: Horoscope, conseil, phrase spirituelle par signe. Système déterministe basé sur signe+date pour un contenu unique chaque jour.
- **Aperçu visuel du PDF**: 3 pages prévisualisées sur la page Aperçu avec PyMuPDF, + compteur de pages verrouillées.
- **Tarot Oui/Non**: 22 Arcanes Majeurs, réponse oui/non/neutre avec interprétation. Prêt pour paiement Stripe (4,99€).
- **Tarologie & Médiumnité**: Tirage 7 cartes, lecture médiumnique (passé/présent/futur/conseil d'âme), PDF généré. Prêt pour paiement Stripe (35€).
- **Navbar enrichie**: Liens vers Guidance du Jour, Tarot Oui/Non, Tarologie visibles sur toutes les pages post-formulaire.
- **Tests**: Backend 100% (20/20), Frontend 100%.

## Prochaines étapes (Backlog)

### P0 - Critique
- [x] Intégrer Stripe avec checkout
- [x] Connecter AstrologyAPI
- [x] Génération PDF fonctionnelle
- [x] Intégrer les 12 illustrations zodiacales
- [x] Contenu quotidien intelligent
- [x] Aperçu visuel du PDF
- [x] Tarot Oui/Non (4,99€)
- [x] Tarologie & Médiumnité (35€)

### P1 - Important
- [ ] Abonnement mensuel 14,99€/mois (Stripe Subscription) pour contenu quotidien
- [ ] Préparer le déploiement sur Railway (Dockerfile, railway.json)
- [ ] Dashboard admin avec KPIs

### P2 - Nice to have
- [ ] Print-on-Demand pour le livre physique
- [ ] Emails automatiques (confirmation + J+5)
- [ ] Chat IA personnalisé
- [ ] Aide sur Notion
