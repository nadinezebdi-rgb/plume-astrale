# Plume Astrale - PRD

## Date: 28 Fevrier 2026

## Produit
Plateforme esoterique complete proposant des analyses astrologiques, numerologiques et de tarologie personnalisees.

## Produits & Prix
| Produit | Prix | Description |
|---------|------|-------------|
| Theme Astral Pro | 29,90 EUR | PDF francais enrichi 28+ pages avec design Plume Astrale |
| Compatibilite Amoureuse | 29,90 EUR | Rapport de compatibilite via AstrologyAPI |
| Chemin d'Ame | 24,90 EUR | Manuscrit personnalise avec illustrations |
| Tarologie & Mediumnite | 35,00 EUR | Tirage en Croix 5 cartes + interpretations |
| Livre Physique | 49,90 EUR | Edition reliee (Print-on-Demand) |

## Codes Promo
- `PLUME2026` : Acces gratuit a TOUS les produits
- `ASTRO100` : Acces gratuit au Chemin d'Ame uniquement

## Deploiement
- **VPS Hostinger** : KVM 1, Ubuntu 24.04, IP 187.124.9.214
- **Domaine** : plume-astrale.fr (DNS A record -> VPS)
- **SSL** : Let's Encrypt, expire le 27 mai 2026
- **Stack** : Docker Compose (MongoDB + Backend + Frontend + Nginx)
- **Github** : https://github.com/nadinezebdi-rgb/plume-astrale

## Completed - 28 Fev 2026 (session actuelle)

### 1. Enrichissement Massif du PDF "Theme Astral Pro" (V3 -> V4)
- Carte du ciel calculee avec positions reelles des planetes
- Section Equilibre Elementaire (Feu/Terre/Air/Eau + Modalites)
- Pages individuelles pour Mercure, Venus, Mars avec interpretations par signe
- Page combinee Jupiter & Saturne avec interpretations detaillees
- Section Planetes Retrogrades avec explications personnalisees
- Section Aspects Planetaires (harmonieux + defis de croissance)
- Maisons Astrologiques personnalisees (planetes dans chaque maison)
- Section Chiron, Lilith Noire & Noeud Nord (guerison/ombre/destinee)
- 60+ descriptions planete-en-signe dans `astro_content_extended.py`
- Tests: 22/22 (iteration_7)

### 2. Carte Astrale Partageable (Instagram / WhatsApp)
- Endpoint POST /api/share/generate-card genere image PNG 1080x1350
- 3 boutons: Instagram (download), WhatsApp (texte), Copier
- Tests: 13/13 (iteration_8)

### 3. Integration AstrologyAPI Phase 1
- `natal_wheel_chart` : Vraie carte du ciel SVG integree au PDF via cairosvg
- `moon_phase_report` : Phase lunaire en francais sur /quotidien + endpoint /api/moon-phase
- `house_cusps/tropical` : Endpoint ajoute au service
- Tests: 20/20 (iteration_9)

### 4. Refonte Page d'Accueil (P0)
- 2 boutons d'entree principaux : Tarot / Astrologie
- Section "Nos Services" avec Compatibilite, Guidance du Jour, Tarologie
- Temoignages + trust indicators
- Tests: Pass (iteration_10)

### 5. Flux Tarot Oui/Non avec Conversion (P0)
- Compteur 3 tirages gratuits via localStorage
- Formulaire de capture au 4eme tirage (prenom, email, date/heure naissance, ville)
- Cross-sell astrologie apres inscription
- Donnees sauvegardees dans localStorage pour upsell astrologie
- Tests: 12/12 backend + frontend (iteration_10)

## Completed - 26 Fev 2026
- [x] Tirage en Croix (5 cartes) avec interpretations detaillees
- [x] PDF Theme Astral Pro en FRANCAIS
- [x] Code promo PLUME2026 sur toutes les prestations
- [x] Favicon esoterique + badge "Made with Emergent" retire
- [x] Deploiement VPS Hostinger avec Docker Compose + SSL

## Completed - 25 Fev 2026
- [x] Integration illustrations zodiacales dans PDF
- [x] Generation 22 cartes Tarot de Marseille
- [x] Produit Compatibilite Amoureuse
- [x] Produit Chemin d'Ame (24,90 EUR)
- [x] Pages: /quotidien, /tarot-oui-non, /tarologie, /compatibilite
- [x] Apercu visuel du PDF avant achat

## Backlog (Nouvelle Strategie)

### P1 - En attente
- [ ] Integration SendGrid (capture emails des inscriptions Tarot)
- [ ] Upsell Tarot approfondi (29 EUR) - utiliserait tarot_predictions API (bloque par plan)
- [ ] Upsell "Lecture Clarte" Astrologie (49 EUR)

### P2 - Futur
- [ ] Cartographie annuelle Premium (199 EUR) - utiliserait solar_return API (bloque par plan)
- [ ] Abonnement Stripe 14,99 EUR/mois
- [ ] Tableau de bord admin (suivi ventes/KPI)

### P3 - Nice to have
- [ ] Print-on-Demand automatise
- [ ] Emails automatiques J+5
- [ ] React Context pour centraliser l'etat frontend
- [ ] Renouvellement auto certificat SSL
- [ ] Script de deploiement automatise (deploy.sh)

## Notes sur l'API AstrologyAPI
- Plan actuel limite a: planets/tropical, western_horoscope, natal_wheel_chart, house_cusps, moon_phase_report, geo_details
- Endpoints bloques: tarot_predictions, yes_no_tarot, daily horoscope, sign reports, numerology, solar return, transits, compatibility reports, chart interpretation
- Upgrade du plan necessaire pour debloquer les endpoints avances
