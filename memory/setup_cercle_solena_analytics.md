# 🔮 Setup Cercle Soléna & Analytics — Instructions pour Nathalie

## 1. Configurer le prix Stripe (obligatoire pour activer l'abonnement)

1. Va sur https://dashboard.stripe.com/products
2. Clique **"+ Ajouter un produit"**
3. Renseigne :
   - **Nom** : `Cercle Soléna`
   - **Description** : `Abonnement mensuel — 3 crédits, communauté, réductions permanentes`
   - **Modèle de tarification** : `Récurrent`
   - **Prix** : `19.00 EUR`
   - **Fréquence de facturation** : `Mensuel`
4. Enregistre le produit → Stripe génère un **Price ID** de la forme `price_1XxxYyyZzzz`
5. Copie ce Price ID
6. Ajoute-le dans `/app/backend/.env` :
   ```
   STRIPE_CERCLE_SOLENA_PRICE_ID=price_1XxxYyyZzzz
   ```
7. Redémarre le backend (`sudo supervisorctl restart backend`)

Tant que ce Price ID n'est pas configuré, le CTA "Rejoindre le Cercle" renverra une erreur claire "L'abonnement n'est pas encore configuré" (503).

## 2. Migration SQL Supabase (à faire une fois)

Ouvre https://supabase.com/dashboard/project/YOUR-PROJECT/sql/new et colle le contenu de :

```
/app/supabase/cercle_solena_migration.sql
```

Cela crée :
- La table `subscriptions` (une ligne par abonnement Stripe actif)
- La table `credit_grants` (audit des crédits offerts, idempotent)
- Les colonnes `stripe_customer_id` + `is_cercle_member` sur `profiles`
- Les policies RLS (chaque user ne voit que ses propres subs/grants)

## 3. Configurer le webhook Stripe (pour crédit auto mensuel)

1. Va sur https://dashboard.stripe.com/webhooks
2. Ton webhook existant `https://plume-astrale.fr/api/webhook/stripe` doit maintenant écouter aussi ces événements :
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
3. Ces 4 events sont probablement déjà activés (car il y a un ancien flow Premium). Sinon coche-les.
4. Le secret `STRIPE_WEBHOOK_SECRET` est déjà en place.

## 4. Configurer Plausible (Analytics RGPD)

1. Va sur https://plausible.io/register (essai gratuit 30j puis 9$/mois pour < 10k pv)
2. Ajoute ton site : `plume-astrale.fr`
3. Récupère le script d'installation (déjà géré par le code — il suffit d'activer)
4. Ajoute dans `/app/frontend/.env` :
   ```
   REACT_APP_PLAUSIBLE_DOMAIN=plume-astrale.fr
   ```
5. Configure ces **Goals** dans Plausible → Site Settings → Goals :
   - `signup_completed` (custom event)
   - `bundle_click` (custom event)
   - `kabbale_checkout` (custom event)
   - `astrocarto_checkout` (custom event)
   - `cercle_solena_checkout` (custom event)
   - `pack_karmique_checkout` (custom event)

Le tracking ne se déclenche QUE si l'utilisateur a cliqué "Accepter" dans le bandeau cookies (100% RGPD-safe).

## 5. Alternative GA4 (optionnel — additionnel à Plausible)

Si tu veux aussi GA4 :

1. Crée une propriété GA4 sur https://analytics.google.com
2. Récupère l'ID de mesure (format `G-XXXXXXXXXX`)
3. Ajoute dans `/app/frontend/.env` :
   ```
   REACT_APP_GA4_ID=G-XXXXXXXXXX
   ```
4. Rebuild le frontend : `cd /app/frontend && yarn build`

Le même code envoie les événements vers les deux plateformes en parallèle.

---

## ✅ Résumé rapide

| Chose à faire       | Où                                             | Temps  |
|---------------------|------------------------------------------------|--------|
| Créer Price Stripe  | dashboard.stripe.com/products                  | 3 min  |
| SQL migration       | Supabase Studio SQL Editor                     | 30 sec |
| Webhook events      | dashboard.stripe.com/webhooks                  | 1 min  |
| Plausible signup    | plausible.io/register                          | 5 min  |
| .env additions      | `/app/backend/.env` + `/app/frontend/.env`     | 30 sec |

**Total : ~10 minutes de setup pour libérer les 4 features.**
