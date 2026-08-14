# Meta Pixel — Guide de vérification & Test Events

Le Meta Pixel `1801418127692821` est installé sur plume-astrale.fr et couvre
automatiquement Facebook + Instagram + Threads (une seule installation, toutes
les propriétés Meta la partagent).

## Vérification rapide (30 secondes)

### Option A · Meta Pixel Helper (extension Chrome)
1. Installer [Meta Pixel Helper](https://chrome.google.com/webstore/detail/meta-pixel-helper/fdgfkebogiimcoedlicjlajpkdmockpc) sur Chrome.
2. Ouvrir plume-astrale.fr sur ton navigateur.
3. **Important : accepter les cookies** (le pixel ne se charge qu'après consentement RGPD).
4. Cliquer l'icône bleue "Meta Pixel Helper" en haut à droite.
5. Tu dois voir : `Plume Astrale (1801418127692821)` avec un ✓ vert et l'événement `PageView`.

### Option B · Test Events dans Meta Business Manager
1. Aller sur https://business.facebook.com/
2. Menu Événements > **Gestionnaire d'événements**
3. Cliquer sur ton pixel `Plume Astrale — 1801418127692821`
4. Onglet **"Événements de test"** (Test Events)
5. Coller l'URL : `https://plume-astrale.fr`
6. Cliquer **"Ouvrir le site Web"**
7. **Accepter les cookies** sur plume-astrale.fr
8. Faire un parcours : visiter /decouvrir, cliquer "Recevoir ma lecture", etc.
9. Observer la colonne "Événements" de la Meta interface — tu dois voir :
   - `PageView` (à chaque page)
   - `InitiateCheckout` (au clic sur les CTAs paiement)
   - `Purchase` (après paiement Stripe validé)
   - `Lead` (à l'inscription)
   - `CompleteRegistration` (après confirmation email)

## Mapping des événements Plume Astrale → Meta Standards

| Event métier (analytics.js)        | Meta standard event   | Usage ads                          |
|-----------------------------------|-----------------------|------------------------------------|
| `signup_started`                  | `Lead`               | Audience de personnes intéressées  |
| `signup_completed`                | `CompleteRegistration`| Optimisation "acquisition qualifiée"|
| `kabbale_checkout`                | `InitiateCheckout`   | Retargeting checkout abandonné     |
| `astrocarto_checkout`             | `InitiateCheckout`   | Idem                               |
| `pack_karmique_checkout`          | `InitiateCheckout`   | Idem                               |
| `cercle_solena_checkout`          | `InitiateCheckout`   | Idem                               |
| `cercle_solena_active`            | `Subscribe`          | Optimisation abonnements           |
| `credit_purchase`                 | `Purchase`           | Optimisation ROAS (revenue)        |
| `bundle_click` / `solena_click`   | `ViewContent`        | Audience "engagement fort"         |
| `solena_question`                 | `Contact`            | Audience "prospect chaud"          |

Chaque event est aussi envoyé en `trackCustom(nom_original)` pour permettre
des audiences fines sur les noms métier exacts.

## Créer tes premières audiences

Une fois le pixel actif depuis 48h et 100+ événements collectés :

### Audience #1 · Retargeting "InitiateCheckout non abouti"
- Meta Business > Audiences > Créer une audience personnalisée > Site Web
- Source : Meta Pixel Plume Astrale
- Condition : `Personnes qui ont déclenché InitiateCheckout` ET `PAS Purchase`
- Fenêtre : 30 jours
- Nom : "Panier abandonné 30j"

Idéal pour campagne "Reprends ta lecture où tu l'as laissée"
— très haut ROAS car intention déjà démontrée.

### Audience #2 · Lookalike "Acheteuses ROAS+"
- Source : Custom audience "Purchase 90j"
- Country : France
- Similarité : 1% (le plus proche)
- Nom : "Lookalike Purchase FR 1%"

Idéal pour campagnes d'acquisition — prospection avec prospects
qui ressemblent aux clientes existantes.

### Audience #3 · Retargeting "Engagement fort blog"
- Source : Pageview URL contient `/blog/`
- ET Pageview URL contient `/manifesto`
- Fenêtre : 60 jours
- Nom : "Lectrices engagées 60j"

Idéal pour campagne "Découvre ce que Plume Astrale propose"
— les lecteurs qualifiés du blog sont beaucoup plus enclins à convertir.

## ⚠ Points de vigilance RGPD

1. **Le pixel ne se charge JAMAIS avant le consentement utilisateur** (localStorage `pa_consent_v1 === 'accepted'`). Ceci est vérifié dans `src/lib/analytics.js`.
2. Meta reçoit les événements avec l'IP anonymisée par défaut côté navigateur (Meta le fait automatiquement pour les visiteurs EU).
3. En cas de refus de cookies, aucune donnée n'est transmise à Meta. La fonction `event()` devient un no-op.
4. Le `noscript` fallback dans `index.html` reste bloqué chez les utilisateurs qui refusent cookies **si** les navigateurs modernes respectent Do-Not-Track — Firefox et Safari filtrent ces images de tracking.
