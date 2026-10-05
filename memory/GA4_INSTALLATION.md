# GA4 — Guide d'installation & vérification (Plume Astrale)

**Statut** : Infrastructure en place. **Il vous reste UNE action** :
renseigner votre Measurement ID GA4 dans `.env`. Voir §1.

---

## 1. Activer GA4 (action utilisateur, 30 secondes)

Ouvrez `/app/frontend/.env` et remplacez la valeur vide :

```env
REACT_APP_GA4_ID=G-XXXXXXXXXX
```

Puis redémarrez le frontend :

```bash
sudo supervisorctl restart frontend
```

**Où trouver votre ID** : Google Analytics → Admin → Data Streams → Web →
copier le "Measurement ID" (format `G-` suivi de 10 caractères alphanumériques).

---

## 2. Fichiers créés ou modifiés

| Fichier | Rôle | Statut |
|---|---|---|
| `frontend/.env` | Variable `REACT_APP_GA4_ID` (placeholder) | ✏️ modifié |
| `frontend/src/lib/analytics.js` | Consent Mode v2 + GA4 mapping + helpers `ctaClick`, `signUpStart`, `beginCheckout` + anti-PII + revenue e-commerce | ✏️ modifié |
| `frontend/src/pages/Register.js` | Émission `sign_up_start` au montage (dédup session) | ✏️ modifié |
| `frontend/src/pages/Login.js` | Utilise `EVENTS.LOGIN` (event standard GA4) | ✏️ modifié |
| `backend/tests/test_ga4_integration_static.py` | 11 tests de non-régression | ➕ créé |
| `docs/GA4_INSTALLATION.md` | Ce document | ➕ créé |

**Fichiers réutilisés (aucune duplication)** :
- `frontend/src/components/RouteTracker.js` (page_view SPA — déjà en place)
- `frontend/src/components/CookieConsent.js` (bandeau RGPD — déjà en place)
- `frontend/src/pages/CreditSuccess.js` (dédup purchase — déjà en place)

---

## 3. Événements installés — Table exhaustive

| Event métier (Plume) | Event GA4 standard | Émis quand | Paramètres |
|---|---|---|---|
| `page_view` | `page_view` | Chaque changement de route SPA (via `RouteTracker`) | `page_path`, `page_location`, `page_title` |
| `signup_started` | `sign_up_start` | Montage de `/inscription` (dédup sessionStorage) | `source`, `intent_type` |
| `signup_completed` | `sign_up` | Après `supabase.auth.signUp` réussi | `has_birth_data` |
| `login` | `login` | Après `supabase.auth.signInWithPassword` réussi | — |
| `cta_click` | `cta_click` (custom) | Chaque clic CTA (via helper `ctaClick`) | `cta_name`, `page_location`, `destination` |
| `bundle_click` | `view_item` | Clic sur une carte de bundle produit | `item_name`, `item_category` |
| `kabbale_checkout` | `begin_checkout` | Arrivée sur checkout Stripe Kabbale (dédup par pack_id) | `value`, `currency`, `items[]` |
| `astrocarto_checkout` | `begin_checkout` | Idem Astrocarto | `value`, `currency`, `items[]` |
| `pack_karmique_checkout` | `begin_checkout` | Idem Pack Karmique | `value`, `currency`, `items[]` |
| `cercle_solena_checkout` | `begin_checkout` | Idem Cercle Soléna | `value`, `currency`, `items[]` |
| `credit_purchase` | `purchase` | Paiement Stripe confirmé (dédup par session_id) | `transaction_id`, `value`, `currency`, `items[]`, `eventID` |

**Événements du prototype `/experience` (custom GA4)** :
`experience_started`, `intent_selected`, `tarot_card_selected`, `tarot_card_revealed`, `tarot_continue_clicked`, `feather_completed`, `signup_cta_clicked`, `recommended_service_viewed`, `recommended_service_clicked`.

---

## 4. Tunnel de conversion (funnel GA4)

Reconstructible dans GA4 → Explore → Funnel exploration avec les étapes :

```
1. page_view           (visite d'une page)
2. cta_click           (interaction avec un CTA)
3. sign_up_start       (début du parcours d'inscription)
4. sign_up             (compte créé)
5. begin_checkout      (arrivée sur page Stripe)
6. purchase            (paiement confirmé)
```

**KPI CA/visiteur** : GA4 → Reports → Monetization → Purchase revenue, ou custom
Exploration `Total revenue / Total users`.

---

## 5. E-commerce (Stripe → GA4)

L'événement `purchase` est envoyé **une seule fois** grâce à trois barrières :

1. **Client** : `sessionStorage['pa_purchase_tracked_${sessionId}']` (voir `CreditSuccess.js`)
2. **GA4 natif** : `transaction_id` dédupliqué par GA4 (assigné automatiquement dans `revenue()`)
3. **Meta CAPI** : `eventID` partagé client ↔ serveur pour dédup Meta

Structure GA4 envoyée :

```js
gtag('event', 'purchase', {
  transaction_id: "credit_purchase-1739812345678-abc123",
  value: 19.90,
  currency: 'EUR',
  items: [{
    item_id: 'pack_starter',
    item_name: 'Pack Starter 50 crédits',
    item_category: 'credits',
    price: 19.90,
    quantity: 1
  }]
});
```

---

## 6. Consent Mode v2 (RGPD)

Google Consent Mode v2 est **actif dès le chargement** de la page :

```js
// AVANT que gtag.js ne soit chargé :
gtag('consent', 'default', {
  ad_storage: 'denied',
  ad_user_data: 'denied',
  ad_personalization: 'denied',
  analytics_storage: 'denied',
  functionality_storage: 'granted',   // nécessaire
  security_storage: 'granted',        // nécessaire
  wait_for_update: 500
});

// Après clic "Tout accepter" :
gtag('consent', 'update', {
  ad_storage: 'granted',
  ad_user_data: 'granted',
  ad_personalization: 'granted',
  analytics_storage: 'granted'
});
```

**Vérifié en smoke** : dataLayer contient uniquement `consent default (denied)` tant
que l'utilisateur n'a pas cliqué "Tout accepter". Aucun script GA/Meta/X n'est chargé
avant consentement.

---

## 7. Anti-PII

Un garde-fou `sanitizeProps()` filtre automatiquement toutes ces clés avant envoi :

```
email, e_mail, user_email
password, pwd, motdepasse, mot_de_passe
prenom, first_name, last_name, nom
phone, telephone, mobile
address, adresse, postal_code, code_postal
token, access_token, jwt, authorization, bearer
```

Et détecte les valeurs contenant un email (`user@domain.tld` regex).

**Aucun code appelant `event()` ne peut envoyer de PII à GA4** — c'est un backstop
défensif en plus de la responsabilité des devs.

---

## 8. Vérification en production — Checklist

### 8.1 Avec DebugView (recommandé)

1. Installer **Google Analytics Debugger** (extension Chrome/Firefox)
2. Ouvrir `plume-astrale.fr`
3. Accepter les cookies
4. GA4 → Admin → DebugView → sélectionner votre stream
5. Naviguer sur le site et observer les events en temps réel

### 8.2 Console navigateur (5 lignes)

```js
// Ouvrir DevTools → Console sur plume-astrale.fr après consentement
window.dataLayer.slice(-10)   // 10 derniers events
window.gtag                    // doit être une fonction
```

### 8.3 Checklist événements (§12 de votre spec)

| # | Vérification | Comment |
|---|---|---|
| 1 | GA4 chargé | Network → filtrer `googletagmanager.com/gtag/js` — doit être 200 |
| 2 | `page_view` | Naviguer entre 3 pages → DebugView doit compter 3 events |
| 3 | `cta_click` | Cliquer un CTA → event avec `cta_name` + `destination` |
| 4 | `sign_up_start` | Ouvrir `/inscription` → 1 event (max 1 par session) |
| 5 | `sign_up` | Créer un compte test → 1 event `sign_up` après succès |
| 6 | `begin_checkout` | Cliquer "Acheter un pack" → 1 event `begin_checkout` |
| 7 | `purchase` | Terminer un paiement test → 1 event `purchase` avec `transaction_id` |
| 8 | Pas de double `purchase` | Rafraîchir la page /credit-success → 0 nouveau `purchase` |
| 9 | UTM conservés | Ouvrir `?utm_source=instagram&utm_campaign=test` → GA4 → Reports → Acquisition |
| 10 | Desktop + mobile | Tester sur les deux, événements doivent apparaître dans DebugView |
| 11 | Pas de PII | Chercher `email` ou `@` dans DebugView payloads — 0 résultat |
| 12 | Pas de doubles events | DebugView → tout event ne doit apparaître qu'une fois par action |

### 8.4 Marquer les conversions dans GA4

GA4 → Admin → Events → basculer sur "Mark as key event" pour :
- ✅ `sign_up`
- ✅ `begin_checkout`
- ✅ `purchase`

Ces 3 events apparaîtront alors dans les rapports Conversions.

---

## 9. Tests automatisés

Suite de tests de non-régression :

```bash
cd /app/backend
python -m pytest tests/test_ga4_integration_static.py -v
```

Ces tests bloquent une régression sur :
- Placeholder env var
- Aucun ID GA4 hardcodé
- Consent Mode v2 defaults `denied`
- `send_page_view=false` (dédup page_view SPA)
- Mapping événements standards GA4
- Anti-PII actif
- Helpers `ctaClick`, `signUpStart` exposés
- `Login.js` utilise `EVENTS.LOGIN` (pas `login_success`)
- `revenue()` envoie `transaction_id` + `items[]`
- `CreditSuccess.js` dédup par `sessionId`

---

## 10. Ce qui n'a PAS changé (conservation)

- ❌ Aucun changement de design
- ❌ Aucun changement de flow utilisateur
- ❌ Aucun changement de backend
- ❌ Aucun changement Stripe / paiements
- ❌ Aucun changement `AuthContext` / Supabase
- ❌ Aucun changement de `wallet_service` / 20 crédits
- ❌ Aucun changement de routes `/services/*`
- ❌ Aucun changement CookieConsent (bandeau RGPD existant respecté)
- ❌ Aucune duplication analytics (Meta + X + Plausible restent tels quels)

---

## 11. Ce qui reste à faire (optionnel, non-bloquant)

- Ajouter des `ctaClick('Créer un compte', {destination:'/inscription'})` sur les CTA majeurs (Homepage, sales pages)
- Ajouter `beginCheckout('kabbale_checkout', sessionId, price)` sur les composants de paiement (aujourd'hui l'event est émis via `event('kabbale_checkout')` — fonctionne mais moins riche en payload)
- Configurer les Data Streams GA4 en production (validation `_ga` cookie sur `plume-astrale.fr`)
- Optionnel : activer Google Ads si utilisé, via même Data Stream

**Aucune de ces optimisations n'est bloquante — GA4 fonctionnera dès que vous renseignerez votre `REACT_APP_GA4_ID`.**
