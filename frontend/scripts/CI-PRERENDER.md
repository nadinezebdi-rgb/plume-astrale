# CI Prerender — Wiring `yarn build:seo` en Production

Guide opérationnel pour intégrer le prerender SSR SEO dans votre pipeline
de déploiement, quel qu'il soit.

## Vue d'ensemble

Le prerender transforme le SPA React en pages HTML statiques que Googlebot
peut indexer sans exécuter JavaScript. Sans cette étape, Google reçoit
un `index.html` vide et n'indexe rien correctement.

**Résultat attendu** :
- Avant : `curl plume-astrale.fr/theme-natal` → 3KB, aucun contenu
- Après : `curl plume-astrale.fr/theme-natal` → 30-80KB, HTML complet
  avec H1, meta, canonical, JSON-LD, contenu principal

## Pré-requis serveur de build

- Node ≥ 20.x
- Un binaire Chromium/Chrome accessible (`chromium-browser` sur Debian,
  `google-chrome` sur Ubuntu, ou Chrome standalone)
- 512 Mo RAM minimum (Puppeteer + serve + build React simultanément)

Le package `puppeteer-core` (5 Mo) est déjà installé dans `package.json` —
**pas besoin de télécharger Chromium à l'installation**.

## Recette Emergent (contact support)

Emergent ne propose actuellement **aucune personnalisation self-service** du pipeline de build. Il faut passer par le support pour ajouter `yarn build:seo`.

**Comment procéder** :

1. Récupérer votre **Job ID** : bouton info (i) en haut à droite de l'interface Emergent chat
2. Envoyer un email à **support@emergent.sh** avec le template ci-dessous
3. Le support intervient manuellement sur votre pipeline (délai standard)

**Template email à copier-coller** :

```
À : support@emergent.sh
Sujet : Ajout de yarn build:seo au pipeline de production (SEO prerender)

Bonjour,

Job ID : <RÉCUPÉRER via le bouton (i) dans l'interface Emergent>

Merci d'ajouter à mon pipeline de build de production le remplacement
de la commande actuelle par :

    CHROME_BIN=/usr/bin/google-chrome yarn build:seo

au lieu de `yarn build`.

- Le script `frontend/scripts/prerender.js` est déjà prêt (puppeteer-core, léger)
- Il utilise Chrome système (déjà présent dans l'image Docker pour le PDF engine v2)
- Durée additionnelle estimée : +90 à 120 secondes par déploiement
- Objectif : permettre l'indexation Google en générant les HTML statiques
  avec contenu SEO complet dans build/{route}/index.html

Merci pour votre aide.
```

Alternative si le support prend trop de temps : demander à l'agent Emergent de modifier
`package.json` pour que `"build": "craco build && yarn prerender"` (attention : risque
de casser si Chrome n'est pas dispo dans l'env de build).

## Recette GitHub Actions

`.github/workflows/deploy.yml` :
```yaml
name: Deploy Plume Astrale
on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'yarn'
      - name: Install Chromium (Ubuntu)
        run: sudo apt-get update && sudo apt-get install -y chromium-browser
      - name: Install dependencies
        run: yarn install --frozen-lockfile
      - name: Build + Prerender SEO
        env:
          CHROME_BIN: /usr/bin/chromium-browser
          REACT_APP_BACKEND_URL: ${{ secrets.REACT_APP_BACKEND_URL }}
        run: yarn build:seo
      - name: Deploy to production
        run: <votre commande deploy>
```

## Recette Vercel

Dans Project Settings → General → Build & Development Settings :
- **Build Command** : `yarn build:seo`
- **Install Command** : `yarn install --frozen-lockfile`
- **Output Directory** : `build`

Dans Environment Variables :
- `CHROME_BIN` = `/usr/bin/google-chrome-stable` (Vercel ships Chrome)
- `REACT_APP_BACKEND_URL` = votre URL backend prod

## Recette Netlify

Dans `netlify.toml` :
```toml
[build]
  command = "yarn build:seo"
  publish = "build"

[build.environment]
  NODE_VERSION = "20"
  CHROME_BIN = "/usr/bin/google-chrome-stable"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

Note : Netlify inclut Chrome dans l'image par défaut.

## Vérification post-déploiement

Après le premier deploy avec prerender, vérifiez avec `curl` :

```bash
# 1. Le HTML statique doit contenir le H1 réel
curl -s https://plume-astrale.fr/theme-natal | grep -oP '<h1[^>]*>[^<]+'
# Attendu : <h1 class="ne-display ...">Le seul livre de thème natal…

# 2. La canonical doit être présente
curl -s https://plume-astrale.fr/services/compatibilite | grep 'rel="canonical"'
# Attendu : <link rel="canonical" href="https://plume-astrale.fr/services/compatibilite">

# 3. La taille du HTML doit être > 30KB
curl -s https://plume-astrale.fr/theme-natal | wc -c
# Attendu : > 30000

# 4. Google Search Console → Inspection d'URL → Rendu en direct
# Le HTML rendu doit contenir tout le contenu SEO immédiatement.
```

## Rollback / Désactivation

Si le prerender pose problème (temps de build trop long, erreurs sur une
route), désactivez-le en remplaçant `yarn build:seo` par `yarn build` dans
votre pipeline. Aucune modification de code n'est requise — le SPA continuera
à fonctionner (SEO dégradé mais fonctionnel).

## Ajout de nouvelles routes SEO

Éditez `frontend/scripts/prerender.js` → tableau `ROUTES`, puis mettez
à jour `frontend/public/sitemap.xml` pour cohérence. Deux fichiers à
modifier ensemble.

## FAQ CI

**Q : Le build est-il plus lent ?**
R : Oui, +90-120s pour ~80 routes. C'est le prix d'un SEO efficace.
Envisagez de ne prerender que les 20 routes prioritaires si le temps
de build est critique.

**Q : Que faire si Chrome n'est pas dans l'image de build ?**
R : Le script détecte automatiquement 4 chemins possibles. S'il ne trouve
rien, il sort en code 0 (ne bloque pas le build) et loggue un warning.
Le SPA reste servi normalement.

**Q : Les snapshots MongoDB doivent-ils exister avant le prerender ?**
R : Non — le script les récupère si disponibles pour enrichir le HTML,
mais fonctionne même sans (fallback : le HTML rendu par Puppeteer suffit).

**Q : Le prerender expose-t-il des secrets ?**
R : Non — seul le HTML public rendu par le navigateur est capturé. Aucun
token, aucune donnée privée ne se retrouve dans les fichiers `build/*.html`.
