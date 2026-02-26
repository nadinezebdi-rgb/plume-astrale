# Plume Astrale - PRD

## Date: 26 Fevrier 2026

## Produit
Plateforme esoterique complete proposant des analyses astrologiques, numerologiques et de tarologie personnalisees.

## Produits & Prix
| Produit | Prix | Description |
|---------|------|-------------|
| Theme Astral Pro | 29,90 EUR | PDF francais avec design Plume Astrale |
| Compatibilite Amoureuse | 29,90 EUR | Rapport de compatibilite via AstrologyAPI |
| Chemin d'Ame | 24,90 EUR | Manuscrit personnalise avec illustrations |
| Tarologie & Mediumnite | 35,00 EUR | Tirage en Croix 5 cartes + interpretations |
| Livre Physique | 49,90 EUR | Edition reliee (Print-on-Demand) |

## Codes Promo
- `PLUME2026` : Acces gratuit a TOUS les produits
- `ASTRO100` : Acces gratuit au Chemin d'Ame uniquement

## Deploiement
- **VPS Hostinger** : KVM 1, Ubuntu 24.04, IP 187.124.9.214
- **Domaine** : plume-astrale.fr (DNS A record → VPS)
- **SSL** : Let's Encrypt, expire le 27 mai 2026
- **Stack** : Docker Compose (MongoDB + Backend + Frontend + Nginx)
- **Github** : https://github.com/nadinezebdi-rgb/plume-astrale

## Completed - 26 Fev 2026
- [x] Tirage en Croix (5 cartes) avec interpretations detaillees
- [x] PDF Theme Astral Pro en FRANCAIS (remplace l'ancien PDF anglais)
- [x] Code promo PLUME2026 sur TOUTES les prestations
- [x] Favicon esoterique (oeil de providence / croissant de lune)
- [x] Badge "Made with Emergent" retire
- [x] Deploiement VPS Hostinger avec Docker Compose
- [x] SSL Let's Encrypt active (HTTPS)
- [x] DNS plume-astrale.fr → 187.124.9.214

## Completed - 25 Fev 2026
- [x] Integration illustrations zodiacales dans PDF
- [x] Generation 22 cartes Tarot de Marseille
- [x] Produit Compatibilite Amoureuse
- [x] Produit Chemin d'Ame (24,90 EUR)
- [x] Code promo universel PLUME2026
- [x] Champ genre dans le formulaire
- [x] Pages: /quotidien, /tarot-oui-non, /tarologie, /compatibilite
- [x] Apercu visuel du PDF avant achat

## Backlog
- [ ] (P1) Abonnement Stripe 14,99 EUR/mois pour contenu quotidien
- [ ] (P1) Tableau de bord admin (suivi ventes)
- [ ] (P2) Print-on-Demand automatise
- [ ] (P2) Emails automatiques J+5
- [ ] (P2) Section d'aide Notion
- [ ] (P3) React Context pour centraliser l'etat frontend
- [ ] (P3) Renouvellement automatique certificat SSL (cron certbot)
