# Mail à envoyer à support@emergent.sh

**À :** support@emergent.sh
**Objet :** Demande : commande de build personnalisée (`yarn build:seo`) pour le déploiement — plumeastrale.com

Bonjour,

Je suis utilisatrice d'Emergent pour mon application **Plume Astrale** (job ID : `<à compléter — visible dans l'URL de votre projet Emergent, format `job/xxxxxxxx-xxxx-...`>`), déployée actuellement sur `https://consultation-astro.preview.emergentagent.com` et le domaine custom `plumeastrale.com`.

## Ma demande

Mon dépôt contient dans `frontend/package.json` un script personnalisé :

```json
"build:seo": "react-scripts build && node scripts/prerender-seo.js"
```

Ce script fait deux choses essentielles au référencement :
1. Build CRA standard (`react-scripts build`)
2. Pré-rendu statique des routes clés (`/`, `/theme-natal`, `/composer`, `/blog/*`) + génération du `sitemap.xml` et des métas Open Graph

Actuellement, le pipeline de déploiement Emergent exécute `yarn build` (ou `npm run build`) par défaut. **Je souhaiterais qu'il exécute `yarn build:seo`** afin que mes pages soient livrées pré-rendues en production (sinon mes efforts SEO ne sont pas publiés).

## Ce dont j'ai besoin de votre côté

- **Option A (préférée)** : un fichier de configuration self-serve (ex. `.emergent/deploy.yml`) que je peux committer dans mon dépôt pour surcharger la commande de build.
- **Option B** : que votre équipe configure manuellement `yarn build:seo` comme commande de build pour mon projet.

Si l'Option A existe, pouvez-vous m'envoyer la syntaxe exacte ? Si c'est l'Option B, pouvez-vous l'appliquer et me confirmer le prochain déploiement ?

## Détails techniques

- Stack : React 18 (Create React App), Yarn
- Script : `yarn build:seo` (défini dans `frontend/package.json`)
- Durée : build normal + ~45s de prérendu Node (reste bien sous les timeouts standards)
- Dépendances déjà installées (`puppeteer-core` déjà dans `package.json`)

Merci beaucoup pour votre aide — c'est la dernière brique avant que mon tunnel SEO ne soit pleinement actif.

Bien cordialement,
[Votre nom]
Plume Astrale
plumeastrale.com

---

### 💡 Comment récupérer votre job ID
1. Ouvrez votre projet dans Emergent.
2. Dans l'URL du navigateur, cherchez le segment après `/job/` — c'est votre job ID (format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).
3. Copiez-le à la place de `<à compléter>` dans le mail.

### 📎 Pièce jointe recommandée
Un screenshot de votre `frontend/package.json` ouvert sur la ligne `"build:seo": …` — ça permet au support de confirmer la commande d'un coup d'œil.
