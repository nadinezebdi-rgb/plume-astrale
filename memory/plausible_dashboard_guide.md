# 📊 Guide dashboard Plausible — Plume Astrale

**Objectif** : lire tes chiffres en 30 secondes sans te noyer dans l'interface.

Ton cockpit interne live vit à : **`/admin/analytics`** (accessible depuis ton compte admin).

---

## Les 6 KPIs qui décident

| # | KPI                        | Ce que ça veut dire                        | Cible saine       |
|---|----------------------------|--------------------------------------------|-------------------|
| 1 | **Visiteurs uniques**      | Ton audience nette                         | +20% mois/mois    |
| 2 | **signup_completed**       | Inscriptions abouties                      | ≥ 3% des visiteurs |
| 3 | **\*_checkout**            | Tentatives de paiement (tous PDF)          | ≥ 25% des signups |
| 4 | **Revenue PDF**            | Ventes tunnel unique                        | Suivi mensuel     |
| 5 | **cercle_solena_checkout** | Abonnements récurrents                     | ≥ 5% des acheteurs PDF |
| 6 | **bundle_click**           | Intérêt pour l'offre Duo 68€               | ≥ 10% des connectés |

**Règle d'or** : si un chiffre chute deux semaines de suite, tu regardes ce qui a bougé sur la page qui alimente cet event.

---

## Le tunnel qui compte (à lire dans cet ordre)

```
1. Visiteurs uniques        ┐
                            ├─ Combien te découvrent ?
2. signup_completed         ┘
                            ┐
3. *_checkout               ├─ Combien passent à l'action ?
                            ┘
4. Paiement Stripe réussi   ┐
                            ├─ Combien payent vraiment ?
5. cercle_solena_checkout   ┘
```

Chaque étape a un **taux de conversion attendu**. Si un ratio chute, c'est là que tu débogues.

Exemples de lecture :
- **Signup < 2%** → ton hero ou ton formulaire d'inscription est le blocage
- **Checkout < 20% des signups** → tes landings produits ne convertissent pas assez (revois les témoignages, le mockup PDF, l'urgence)
- **Payment < 60% des checkouts** → problème CB (Stripe error, prix trop cher perçu, doute de dernière minute)
- **Cercle Solena < 3%** → le bandeau post-achat manque d'attractivité (peut-être ajouter -50% le 2e mois)

---

## Setup Plausible en 4 étapes

### 1. Créer le compte Plausible
- URL : https://plausible.io/register
- Prix : 9$/mois pour < 10 000 pageviews (largement suffisant au démarrage)
- Alternative gratuite auto-hébergée : https://github.com/plausible/community-edition

### 2. Ajouter ton site
- **Domaine** : `plume-astrale.fr`
- **Timezone** : Europe/Paris
- **Tracker** : le script est déjà branché dans le code (activation via `.env`)

### 3. Configurer les Goals (dans Site Settings → Goals)

Crée exactement ces 8 Goals **Custom Event** :

| Nom du Goal              | Type                    |
|--------------------------|-------------------------|
| `signup_completed`       | Custom event            |
| `login`                  | Custom event            |
| `bundle_click`           | Custom event            |
| `kabbale_checkout`       | Custom event + Revenue  |
| `astrocarto_checkout`    | Custom event + Revenue  |
| `pack_karmique_checkout` | Custom event + Revenue  |
| `cercle_solena_checkout` | Custom event + Revenue  |
| `solena_click`           | Custom event            |

Pour les 4 Goals avec **Revenue** : coche "This is a revenue goal" et laisse la currency EUR.

### 4. Activer dans `.env`
```
# /app/frontend/.env
REACT_APP_PLAUSIBLE_DOMAIN=plume-astrale.fr
```

Rebuild frontend : `cd /app/frontend && yarn build` (ou déclenche un redéploiement).

---

## Alertes email (utile)

Dans Plausible → Site Settings → Email reports :
- **Rapport quotidien** : Off (bruit)
- **Rapport hebdomadaire** : **On** — reçois chaque lundi matin un résumé de la semaine
- **Traffic spike alert** : **On** — sois notifiée si tu passes viral (>100 visiteurs/heure sur une même heure)

---

## Ce que Plausible ne te dit PAS (et qu'il faut compléter côté Stripe)

Plausible track les **intentions** (checkout initié). Pour connaître le **vrai revenue converti**, tu croises avec Stripe :

- **Stripe Dashboard → Revenue** → recettes réelles TTC après remboursements
- **Stripe Dashboard → Subscriptions** → taux de churn Cercle Soléna
- **Stripe Dashboard → Failed payments** → CB refusées à corriger

**Ratio à surveiller** : `Stripe Revenue / *_checkout events` → ton taux de conversion CB réel.
Si < 55%, tu as un problème de UX de paiement (form, latence, doute).

---

## Petit rappel RGPD

Plausible = **pas de cookies**, **pas de PII**, **pas besoin de bandeau de consentement légalement obligatoire**.

Néanmoins, le code Plume Astrale respecte le consent explicite via le bandeau existant (`getConsent() === 'accepted'`) — les events ne sont envoyés que si l'utilisatrice a cliqué "Accepter". C'est plus strict que le minimum légal, c'est très bien pour ton positionnement premium et éthique.
