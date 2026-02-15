# Plume Astrale - PRD (Product Requirements Document)

## Projet
Application de génération de thèmes astraux et chemins d'âme - Un outil spirituel qui combine numérologie, astrologie et lecture d'âme.

## Date de mise à jour
15 Février 2026

## Problème initial
L'utilisateur avait un site fonctionnel (backend Supabase + Stripe + génération PDF) mais le design n'était pas ésotérique et le flux freemium n'était pas logique - les utilisateurs ne voyaient pas le contenu gratuit avant de payer.

## Architecture technique
- **Frontend**: React 19 + Tailwind CSS + shadcn/ui components
- **Backend**: Supabase (Edge Functions + Astrology API)
- **Paiement**: Stripe (19,90€)
- **Déploiement initial**: Netlify (plume-astrale.fr)

## User Personas
1. **Chercheur spirituel** - Intéressé par la numérologie et l'astrologie pour sa croissance personnelle
2. **Curieux** - Veut découvrir son chemin de vie gratuitement avant d'acheter
3. **Amateur d'ésotérisme** - Recherche une expérience mystique et visuellement impactante

## Ce qui a été implémenté

### Design System Ésotérique
- Palette: Violet profond (#0F0518, #1A0B2E) + Or (#C5A059, #FFD700)
- Typographie: Cinzel (titres) + Quicksand (corps)
- Effets: Étoiles animées (canvas), glassmorphism, glow doré
- Sans symbole de l'infini (comme demandé)

### Pages Refaites (5)
1. **Index (Landing)** - Hero immersif avec nébuleuse, features, témoignages, CTA
2. **Formulaire** - Style "rituel" (une question à la fois sur 5 étapes)
3. **Aperçu** - Contenu GRATUIT (chemin de vie + année personnelle) + sections verrouillées
4. **Paiement** - Récapitulatif élégant + Stripe (simulé)
5. **Résultats** - 5 onglets complets (Identité Céleste, Mission de Vie, Cœur & Relations, Défis & Talents, Conseil de la Plume)

### Flux Freemium Corrigé
```
Landing → Formulaire (5 étapes) → Aperçu GRATUIT → Paiement (19,90€) → Résultats complets
```

## Ce qui reste à faire (Backlog)

### P0 - Critique
- [ ] Intégrer Stripe réel (actuellement simulé avec localStorage)
- [ ] Connecter le backend Supabase pour les calculs astrologiques réels
- [ ] Implémenter la génération PDF premium

### P1 - Important
- [ ] Envoi email automatique après paiement
- [ ] Bouton "Télécharger PDF" fonctionnel
- [ ] Bouton "Partager" avec liens sociaux

### P2 - Nice to have
- [ ] Ajout d'éléments chakra dans le design
- [ ] Animations de transition entre les pages
- [ ] Mode sombre/clair toggle

## Tests réussis
- ✅ 100% des tests frontend passés
- ✅ Navigation complète fonctionnelle
- ✅ Calculs numérologie (chemin de vie, année personnelle)
- ✅ Design responsive

## Notes techniques
- LocalStorage keys: `plume_astrale_data`, `plume_astrale_paid`
- Données stockées: prénom, email, dateNaissance, heureNaissance, ville, pays
