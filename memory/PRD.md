# Plume Astrale - PRD (Product Requirements Document)

## Projet
Application de génération de thèmes astraux et chemins d'âme - Un outil spirituel qui combine numérologie, astrologie, tarot et lecture d'âme.

## Date de mise à jour
25 Février 2026 (Session 4 - Images zodiacales intégrées)

## Dernières modifications
- **12 illustrations zodiacales** intégrées dans le PDF manuscrit (images fournies par l'utilisateur)
- **PDF optimisé** : images redimensionnées (800px) et converties en JPEG pour réduire la taille (~800KB-950KB par PDF)
- **Tests complets** : Backend 86% (2 échecs liés au plan API externe), Frontend 100%
- **Flux complet validé** : Formulaire -> Aperçu -> Code promo ASTRO100 -> Résultats -> Téléchargement PDF

## Problème initial
L'utilisateur avait un site fonctionnel mais souhaitait une refonte complète avec un design ésotérique, un flux freemium corrigé, et un manuscrit PDF enrichi.

## Architecture technique
- **Frontend**: React 19 + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI (Python), uvicorn
- **PDF**: ReportLab (canvas) avec illustrations zodiacales
- **Paiement**: Stripe via emergentintegrations
- **Données Astro**: AstrologyAPI (plan Starter)
- **Base de données**: MongoDB (transactions, commandes)

## Structure Tarifaire

### Manuscrit de la Plume - 29,90€ (paiement unique)
- Analyse complète de votre âme
- Chemin de vie détaillé
- Année personnelle 2026
- Identité céleste (Soleil, Lune, Ascendant)
- Guidance personnalisée
- PDF téléchargeable (~18 pages avec illustrations)

### Le Livre de la Plume - 49,90€ (livre physique)
- Version imprimée reliée du manuscrit
- Livraison sous 5 jours
- Formulaire d'adresse de livraison

### Code promo
- **ASTRO100** : Accès gratuit complet (100% réduction)

## Ce qui a été implémenté

### Session 1 - Design Ésotérique
- Palette violet/or avec étoiles animées
- Formulaire style "rituel" (5 étapes)
- Flux freemium corrigé

### Session 2 - Nouvelles Fonctionnalités
- Pages: /choix, /tarot, /compatibilite, /horoscope
- Navbar post-paiement

### Session 3 - PDF + Livre physique
- Génération PDF du manuscrit (design ésotérique)
- Page Livre physique à 49,90€
- Commande livre via Stripe
- Intégration AstrologyAPI
- Code ASTRO100 fonctionnel

### Session 4 - Images zodiacales (25 Feb 2026)
- 12 illustrations de signes du zodiaque intégrées dans le PDF
- Images optimisées (PNG -> JPEG 800px, ~150-250KB chacune)
- PDF final: ~18 pages, ~800-950KB
- Tests complets passés (backend + frontend)

## Contenu du PDF Manuscrit
1. **Page titre** - Nom, signe, date
2. **Sommaire** - 7 chapitres
3. **Identité Céleste** - Soleil (avec illustration du signe)
4. **Suite Identité** - Forces et défis solaires
5. **Lune** - Monde émotionnel (avec illustration)
6. **Ascendant** - Masque social (avec illustration)
7. **Planètes** - Mercure, Vénus, Mars, Jupiter, Saturne
8. **Suite Planètes** - (si nécessaire)
9. **Chemin d'Âme** - Numérologie, mission de vie
10. **Prévisions 2026** - Carrière, amour, santé, finances, spiritualité
11. **Suite Prévisions** - Conseil clé, mois favorables
12. **Vision 5 ans** - 2026-2030
13. **Suite Vision** - (si nécessaire)
14. **Tirage du Tarot** - 3 cartes (Passé/Présent/Futur)
15. **Interprétation Tarot** - Messages détaillés
16. **Conseils de la Plume** - Guidance personnalisée
17. **Message final** - Bénédiction

## Images Zodiacales (12/12)
- Aries (Bélier), Taurus (Taureau), Gemini (Gémeaux)
- Cancer, Leo (Lion), Virgo (Vierge)
- Libra (Balance), Scorpio (Scorpion), Sagittarius (Sagittaire)
- Capricorn (Capricorne), Aquarius (Verseau), Pisces (Poissons)

Stockées dans: `/app/backend/assets/zodiac/` (format .jpg optimisé)

## Prochaines étapes (Backlog)

### P0 - Critique
- [x] Intégrer Stripe avec checkout
- [x] Connecter AstrologyAPI
- [x] Génération PDF fonctionnelle
- [x] Intégrer les 12 illustrations zodiacales

### P1 - Important
- [ ] Préparer le déploiement sur Railway (Dockerfile, railway.json)
- [ ] Dashboard admin avec KPIs
- [ ] Emails automatiques (confirmation + J+5)

### P2 - Nice to have
- [ ] Intégrer un service Print-on-Demand pour le livre physique
- [ ] Chat IA personnalisé
- [ ] Notifications push horoscope
- [ ] Aide sur Notion

## Key API Endpoints
- `POST /api/checkout/create` - Créer session Stripe
- `POST /api/discount/validate` - Valider code promo
- `POST /api/access/free` - Accès gratuit avec code promo
- `POST /api/astrology/planets` - Positions planétaires
- `POST /api/astrology/horoscope` - Horoscope occidental
- `POST /api/pdf/generate` - Générer PDF manuscrit
- `POST /api/order/book` - Commander livre physique

## Limitations connues
- Daily/Weekly horoscope API: 500 error (limitation plan Starter AstrologyAPI)
- Flux livre physique: collecte l'adresse + paiement, mais pas de Print-on-Demand automatisé
