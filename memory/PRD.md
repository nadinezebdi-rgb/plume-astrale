# Plume Astrale - PRD (Product Requirements Document)

## Projet
Application de génération de thèmes astraux et chemins d'âme - Un outil spirituel qui combine numérologie, astrologie, tarot et lecture d'âme.

## Date de mise à jour
15 Février 2026 (Session 3 - PDF + Livre physique)

## Dernières modifications
- ✅ **Génération PDF** du manuscrit (8 pages, design ésotérique)
- ✅ **Page Livre physique** à 49,90€ avec formulaire d'adresse
- ✅ **Commande livre** via Stripe avec collecte adresse livraison
- ✅ Intégration AstrologyAPI avec données réelles
- ✅ Code de réduction ASTRO100 fonctionnel

## Problème initial
L'utilisateur avait un site fonctionnel (backend Supabase + Stripe + génération PDF) mais le design n'était pas ésotérique et le flux freemium n'était pas logique.

## Architecture technique
- **Frontend**: React 19 + Tailwind CSS + shadcn/ui components
- **Backend**: Supabase (Edge Functions + Astrology API)
- **Paiement**: Stripe (9,90€ Essentiel / 29,90€ Premium)
- **Déploiement initial**: Netlify (plume-astrale.fr)

## Structure Tarifaire Actuelle

### Manuscrit de la Plume - 29,90€ (paiement unique)
- Analyse complète de votre âme
- Chemin de vie détaillé
- Année personnelle 2026
- Identité céleste (Soleil, Lune, Ascendant)
- Guidance personnalisée 2026
- Mission de vie
- PDF téléchargeable à garder pour toujours

**Positionnement** : "Un trésor céleste à conserver précieusement toute votre vie"

## Ce qui a été implémenté

### Session 1 - Design Ésotérique
- Palette violet/or avec étoiles animées
- Formulaire style "rituel" (5 étapes)
- Flux freemium corrigé
- 5 pages de base

### Session 2 - Nouvelles Fonctionnalités
- **Page /choix** : Comparatif Essentiel vs Premium
- **Page /tarot** : Tirage 3 cartes (Passé/Présent/Futur)
- **Page /compatibilite** : Score % avec 12 signes
- **Page /horoscope** : Jour/Semaine/Mois
- **Navbar** : Navigation post-paiement
- **Boutons optimisés** : Textes orientés résultat ("Recevoir mon manuscrit")

## APIs AstrologyAPI à souscrire

### Déjà actives (Forfait Starter)
- planètes/tropical
- cuspides de la maison/tropical
- horoscope occidental
- thème astral
- rapport_phase_lunaire
- géo_détails
- fuseau horaire

### À ajouter
- [ ] **Horoscope du jour** - Pour fidélisation
- [ ] **Horoscope mensuel** - Contenu premium
- [ ] **Prédiction du Tarot** - Remplacer les données locales
- [ ] **Oui Non Tarot** - Tirage rapide
- [ ] **Compatibilité zodiacale** - Score précis
- [ ] **Horoscope de synastrie** - Analyse couple
- [ ] **Nombres numérologiques** - Enrichir calculs

## Prochaines étapes (Backlog)

### P0 - Critique
- [ ] Intégrer Stripe réel avec checkout
- [ ] Connecter AstrologyAPI pour données dynamiques
- [ ] Génération PDF fonctionnelle

### P1 - Important
- [ ] Page abonnement post-achat (15€/mois, 29€/mois)
- [ ] Emails automatiques (confirmation + J+5)
- [ ] Dashboard admin avec KPIs

### P2 - Nice to have
- [ ] Chat IA personnalisé
- [ ] Notifications push horoscope
- [ ] Partage social

## KPIs Cibles (Stratégie 500k€)
- 100 visiteurs/jour
- 40% conversion Aperçu → Choix
- 10% taux d'achat
- 6% vente Premium
- 45% Premium → Abonnement
- 15€ RPV
- 15 000€ MRR

## LocalStorage Keys
- `plume_astrale_data` : Données utilisateur
- `plume_astrale_paid` : Status paiement (true/false)
- `plume_astrale_plan` : Plan choisi (essentiel/premium)
- `plume_astrale_payment_date` : Date du paiement
