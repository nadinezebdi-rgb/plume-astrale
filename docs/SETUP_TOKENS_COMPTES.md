# Setup tokens & comptes — Actions manuelles à faire cette semaine

Ces 4 setups nécessitent des actions humaines (créer un token, créer une page,
envoyer un email). Voici le pas-à-pas de chacun, dans l'ordre où c'est le plus
rentable de les faire.

---

## 1. ⏱ 5 min · Créer la page Facebook @plumeastrale

**Pourquoi le faire en premier ?** Sans page FB, le token Meta CAPI n'est
utile qu'à moitié (le pixel envoie déjà les données, mais tu ne peux pas
gérer les ads sans page business associée).

1. Va sur https://www.facebook.com/pages/create/
2. Nom : `Plume Astrale`
3. Catégorie : `Site Web personnel` OU `Média et service d'actualités` OU `Marque`
4. Bio courte : `Comprendre les périodes de votre vie — plume-astrale.fr`
5. Ajouter :
   - Logo (utiliser `/app/frontend/public/logo512.png`)
   - Cover : capture d'écran du hero de plume-astrale.fr
   - URL Instagram : @plumeastrale.fr (Meta le liera automatiquement)
6. Publier

⚠ **Nom d'utilisateur** : après création, va dans Paramètres > Nom
d'utilisateur, et réserve `@plumeastrale` (5-10 min de délai possible).

---

## 2. ⏱ 10 min · Créer le bucket Supabase Storage `public`

Nécessaire pour l'auto-post Instagram hebdo.

1. Va sur https://app.supabase.com > ton projet Plume Astrale
2. Menu **Storage** (icône dossier à gauche)
3. Bouton **"New bucket"**
4. Nom : `public` (exactement, en minuscules)
5. ✅ Cocher **"Public bucket"** (lecture anonyme HTTPS activée)
6. **File size limit** : 10 MB (largement suffisant pour un PNG 1080x1350)
7. Créer

Vérification : après création, upload un fichier test manuellement puis colle
son URL publique dans un onglet incognito — doit s'afficher directement.

---

## 3. ⏱ 15 min · Générer les 2 tokens Meta

### 3.1 System User Token (pour META_CAPI_ACCESS_TOKEN)

1. https://business.facebook.com/settings/system-users
2. Bouton **"Ajouter"** > créer un nouvel utilisateur système
   - Nom : `Plume Astrale · CAPI Bot`
   - Rôle : **Administrateur système**
3. Cliquer sur l'utilisateur système créé > bouton **"Ajouter des actifs"**
   - Sélectionner : le Pixel Plume Astrale (`1801418127692821`)
   - Permission : `Contrôle total`
4. Toujours sur l'utilisateur système > bouton **"Générer un nouveau jeton"**
   - App : sélectionner ton app FB (créer une app "Plume Astrale" si besoin
     via https://developers.facebook.com/apps/create)
   - Permissions à cocher :
     - `ads_management`
     - `business_management`
   - **⚠ Ne pas cocher d'expiration** → le token System User est permanent

5. **Copier le token** immédiatement (il ne sera plus jamais affiché)
6. Coller dans `/app/backend/.env` :
   ```
   META_CAPI_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   META_CAPI_TEST_CODE=TEST12345
   ```
   (le TEST_CODE est optionnel — utile pour valider en console Test Events,
   à retirer une fois en prod)

### 3.2 Instagram Long-Lived Access Token (pour INSTAGRAM_ACCESS_TOKEN)

1. https://developers.facebook.com/tools/explorer/
2. Choisir ton app FB (celle créée à l'étape 3.1)
3. **Permissions** à cocher :
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `business_management`
4. Bouton **"Générer le token d'accès"** → autoriser
5. Le token affiché est **short-lived** (1-2h). Le convertir en long-lived :

   ```bash
   curl -X GET "https://graph.facebook.com/v20.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"
   ```

   La réponse contient un `access_token` valable **60 jours**.

6. Coller dans `/app/backend/.env` :
   ```
   INSTAGRAM_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   INSTAGRAM_BUSINESS_ID=17841440273868005
   ```

⚠ **Renouvellement** : programmer un rappel calendrier tous les 50 jours
pour re-générer le token. On peut automatiser ce refresh via une petite
routine backend si tu veux (dis-le moi).

---

## 4. ⏱ 20 min · Envoyer le 1er guest post à Psychologies

Le pitch complet est dans `/app/docs/GUEST_POSTS_PITCHES.md` (section 1).

**Recette rapide** :

1. **Trouver le/la destinataire nominatif** :
   - LinkedIn > rechercher "Psychologies rédacteur en chef" ou
     "Psychologies journaliste développement personnel"
   - Ou aller sur psychologies.com/L-equipe et repérer 1-2 personnes qui
     couvrent les thèmes de fond (pas les news pratiques)

2. **Personnaliser la 1ère ligne** avec la mention d'un de leurs articles
   récents que tu as vraiment lu. Exemple :
   > "Je viens de lire votre papier sur les rendez-vous manqués avec soi-même
   > — et c'est exactement le type d'article qui m'a fait vous écrire."

3. **Envoyer entre mardi et jeudi 9h-11h** (meilleur taux d'ouverture)

4. **Objet exact** : `Article invité — Les cycles de vie : ce que l'astrologie moderne éclaire`

5. **Ne PAS** :
   - Envoyer en copie carbone à d'autres médias
   - Attacher une pièce jointe > 2 Mo
   - Mettre un lien vers plume-astrale.fr dans le corps (Google déteste)

6. **Relance** : une seule fois, à J+8, avec juste :
   > "Bonjour, je me permets une relance douce — pas de souci si vous n'avez
   > pas le temps. Je reste dispo si l'angle vous parle."

**Tableau de suivi** — copie-colle dans un Google Sheet :

| Cible          | Envoyé le  | Réponse | Publié le | URL |
|----------------|------------|---------|-----------|-----|
| Psychologies   |            |         |           |     |
| Marie Claire   |            |         |           |     |
| Slate          |            |         |           |     |

---

## Ordre d'exécution recommandé

**Cette semaine** (~50 min total) :
- Lundi : #1 Facebook (5 min) + #2 Supabase bucket (10 min)
- Mardi : #3.1 System User Token Meta CAPI (15 min)
- Mercredi : #4 Envoyer pitch Psychologies (20 min)

**Semaine prochaine** :
- #3.2 Instagram Long-Lived Token (peut attendre — l'auto-post
  démarre au 1er lundi après ajout du token de toute façon)
- #4 bis : pitch Marie Claire jeudi
- #4 ter : pitch Slate mardi suivant

Une fois les tokens dans `.env`, il faut **redémarrer le backend** :
```
sudo supervisorctl restart backend
```
