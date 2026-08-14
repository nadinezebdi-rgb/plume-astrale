# X (Twitter) Ads · Créer l'audience "Panier abandonné 30j"

Ce guide t'accompagne pas à pas pour créer ta première audience custom sur X
Ads Manager, une fois que le pixel X a collecté suffisamment d'événements
(minimum 100 en 30 jours pour être utilisable — patience nécessaire les
premières semaines).

## Prérequis

- X Ads Manager actif : https://ads.x.com/manager/18ce55wyjwl/campaigns
- Pixel X installé (fait ✓, ID `18ce55wyjwl`, voir `analytics.js`)
- **Consentement cookies validé** par les visiteurs (le pixel ne se charge
  qu'après acceptation RGPD).
- Trafic accumulé pendant au moins **7-14 jours** pour dépasser le seuil de 100
  événements — sinon audience "En cours" et inutilisable.

## Étape 1 · Vérifier que les événements arrivent

1. Ouvrir https://ads.x.com/manager/18ce55wyjwl/events
2. Cliquer sur ton Website Tag
3. Onglet **"Événements récents"** — tu dois voir :
   - `PageView` (à chaque visite, si consentement)
   - `signup_completed`, `kabbale_checkout`, `cercle_solena_checkout`, etc.
     (custom events, tirés du code `analytics.js`)
   - `Purchase` avec `value` et `currency=EUR` (via `revenue()`)

Si tu vois `0 events last 7 days` → le pixel n'est pas actif ou les gens
refusent les cookies. Vérifier en mode incognito + accepter les cookies +
faire un parcours test.

## Étape 2 · Créer l'audience "Panier abandonné 30j"

1. Menu **Outils** > **Audiences**
2. Bouton **"Créer une audience"**
3. Choix : **"Audience personnalisée > Activité du site Web"**
4. **Source** : ton Website Tag (Plume Astrale)
5. **Nom** : `Panier abandonné 30j`
6. **Conditions** :
   - Include : Users who triggered `kabbale_checkout` OR `astrocarto_checkout`
              OR `pack_karmique_checkout` OR `cercle_solena_checkout`
   - Exclude : Users who triggered `Purchase`
7. **Fenêtre** : 30 jours
8. Enregistrer.

L'audience va se peupler pendant 24-48h. Une fois > 500 personnes, elle
devient utilisable dans les campagnes.

## Étape 3 · Créer la campagne de retargeting

**Objectif recommandé** : Conversions du site web (pas Trafic — les visiteurs
qualifiés méritent une optimisation vers l'achat).

1. Nouvelle campagne > **Conversions**
2. Événement optimisation : `Purchase` (le pixel doit être configuré comme
   "Standard Purchase Event" côté X — voir onglet Events > Configuration)
3. **Audience** : ajouter uniquement "Panier abandonné 30j"
4. Budget de test : **10€/jour**, durée **7 jours** = 70€ de test suffisent
   pour voir si l'audience convertit
5. Placements : `Home Timeline` uniquement pour un premier test (moins de
   dispersion budgétaire)

## Étape 4 · Créatifs recommandés

Pour ces panier-abandonné, ton meilleur asset est :
- **Un tweet organique existant** qui performe bien (screenshot d'un
  témoignage utilisatrice, ou une belle image de tes rapports mensuels)
- **Copy** : « Ta lecture t'attend. Reprends là où tu l'as laissée. »
- **CTA button** : "Consulter"
- **URL** : `https://plume-astrale.fr/mon-compte` avec params UTM
  `?utm_source=x&utm_medium=cpc&utm_campaign=cart_abandon_30j`

## Métriques cibles semaine 1

| Métrique     | Bon    | Alerte |
|--------------|--------|--------|
| CTR          | > 1.2% | < 0.5% |
| CPC          | < 1€   | > 3€   |
| Conversions  | > 3    | 0      |
| ROAS         | > 3x   | < 1x   |

Si ROAS < 1x au bout de 70€ dépensés → couper l'audience et recréer plus
tard avec plus de trafic accumulé. Si ROAS > 3x → scaler à 30€/jour et
étendre à d'autres audiences (Lookalike Acheteuses, Engagement blog).

## Audiences #2 et #3 à créer plus tard

Une fois 500+ Purchase collectés :

### Audience #2 · Lookalike Acheteuses FR 1%
- Source : Custom audience `Purchase 90j`
- Country : France
- Size : 1% (le plus proche)
- Idéal pour l'acquisition prospection

### Audience #3 · Engagement Blog Fort
- Source : PageView URL contains `/blog/` (durée > 60s idéalement,
  mais pas dispo sur X, on filtre par nombre de pages)
- Fenêtre : 60 jours
- Idéal pour campagne "Découverte de Plume Astrale"

## ⚠ Points importants

- **Ne pas lancer plus de 3 campagnes en même temps** au démarrage — chaque
  campagne se cannibalise si l'audience se recoupe. Une seule audience active
  par thème (rétargeting / lookalike / engagement).
- **Ne pas juger avant 3-5 jours** — X Ads a besoin d'un cycle
  d'apprentissage complet. Les 24 premières heures ne veulent RIEN dire.
- **Suivre le CAC (Coût d'Acquisition Client)** plutôt que le ROAS pur —
  tes lectures ont une valeur à vie (LTV) que le ROAS 1er achat ne capture pas.
