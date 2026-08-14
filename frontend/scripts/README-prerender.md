# Prerender SSG · SEO P3

Le script `scripts/prerender.js` génère une version HTML statique complète
de chaque route publique **après** `yarn build`. Résultat : Googlebot reçoit
tout le contenu SEO (title, meta, canonical, H1, corps de la page, JSON-LD)
dès le premier byte — sans dépendre du rendu JavaScript différé.

## Pourquoi c'est important
Le bilan SEO 2026-02 a identifié 3 blockers :
- ✅ P1 canonical généralisé (fixé — voir `SEO.js`)
- ✅ P2 articles blog en URLs propres `/blog/:slug` (fixé — voir `BlogArticle.js`)
- ⏳ **P3 rendu 100% JavaScript** — ce script est la solution

## Activation en 3 étapes

### 1. Installer les dépendances (une seule fois)
```bash
cd /app/frontend
yarn add -D puppeteer serve
```
> ⚠ `puppeteer` télécharge Chromium (~180 Mo). Ne l'ajoutez que si votre
> pipeline CI/CD peut se le permettre. Alternative : `puppeteer-core` + Chrome
> système (à configurer manuellement dans `prerender.js`).

### 2. Lancer localement pour vérifier
```bash
yarn build && yarn prerender
```
Le script :
1. Lance `serve -s build` sur `localhost:5555`
2. Ouvre Chromium
3. Visite chaque route de la liste `ROUTES` dans `scripts/prerender.js`
4. Attend que `SEO.js` ait posé les meta (canonical, title, JSON-LD)
5. Sauve le HTML complet dans `build/{route}/index.html`

Vérification rapide après exécution :
```bash
grep 'canonical' build/blog/comprendre-le-retour-de-saturne/index.html
grep '<h1' build/blog/comprendre-le-retour-de-saturne/index.html
```
Chaque URL doit avoir son propre canonical et son propre H1.

### 3. L'ajouter au pipeline de déploiement
Insérez `yarn prerender` **entre** `yarn build` et le déploiement :
```yaml
# .github/workflows/deploy.yml — exemple GitHub Actions
- run: yarn install --frozen-lockfile
- run: yarn build
- run: yarn prerender           # ← ajouter cette ligne
- run: aws s3 sync ./build ...
```

## Comportement sans installation
Si `puppeteer` ou `serve` ne sont pas installés, le script affiche un message
et sort en code 0 → **il ne bloque JAMAIS le build**. Vous pouvez donc l'ajouter
au pipeline sans risque : il ne fera rien tant que les deps ne sont pas là.

## Routes prerendered
Voir la constante `ROUTES` dans `scripts/prerender.js`. Elle inclut :
- Homepage `/`
- 9 articles blog `/blog/:slug`
- 12 signes zodiac `/horoscope/:sign`
- 6 pages produit + outils gratuits
- Pages éditoriales (`/manifesto`, `/decouvrir`)

Pour ajouter une nouvelle route SEO, éditez simplement le tableau `ROUTES`.
