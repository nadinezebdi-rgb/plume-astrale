# Prerender SSG · SEO P0 (audit Feb 2026)

Le script `scripts/prerender.js` génère une version HTML statique complète
de chaque route publique **après** `yarn build`. Résultat : Googlebot reçoit
tout le contenu SEO (title, meta, canonical, H1, corps de la page, JSON-LD)
dès le premier byte — sans dépendre du rendu JavaScript différé.

## Pourquoi c'est important

L'audit SEO Feb 2026 a démontré que Googlebot recevait le HTML brut du SPA
(vide, sans title/canonical/H1/contenu). Le prerender au build résout ce
blocker critique.

## Activation

Les dépendances (`puppeteer-core` et `serve`) sont **déjà installées** dans
`package.json` (Feb 2026). Le script utilise `puppeteer-core` (léger ~5 Mo)
et pointe vers le binaire Chromium/Chrome système déjà présent dans l'image
Docker — pas de téléchargement de 180 Mo.

### Recette 1-commande
```bash
cd /app/frontend
yarn build:seo    # équivaut à : yarn build && yarn prerender
```

Le script :
1. Vérifie qu'un binaire Chrome existe : `$CHROME_BIN`, `/usr/bin/google-chrome`,
   `/usr/bin/chromium`, `/root/bin/chromium`.
2. Lance `serve -s build` sur `localhost:5555`.
3. Pour chaque route de la liste `ROUTES` :
   - Visite `http://localhost:5555{route}`.
   - Attend que `SEO.js` ait posé la balise canonical.
   - **Injecte** le `html_body` du snapshot MongoDB (`/api/seo/content?path=…`)
     dans `<div id="root">` → Googlebot voit le contenu sans exécuter JS.
   - Écrit `build/{route}/index.html`.

### Variables d'env optionnelles
- `CHROME_BIN` — chemin explicite vers Chromium (sinon auto-détection).
- `REACT_APP_BACKEND_URL` — URL du backend pour fetch les snapshots SEO
  (defaults to preview URL).

### Pipeline CI/CD

**GitHub Actions** — `.github/workflows/deploy.yml`
```yaml
name: Deploy Plume Astrale
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'yarn' }
      - name: Install Chrome
        run: sudo apt-get update && sudo apt-get install -y chromium-browser
      - run: yarn install --frozen-lockfile
      - run: CHROME_BIN=/usr/bin/chromium-browser yarn build:seo
      - name: Deploy
        run: <votre commande deploy>
```

**Vercel / Netlify** — dans les settings du projet :
- Build command : `yarn build:seo`
- Publish directory : `build`
- Environment : `CHROME_BIN=/usr/bin/chromium-browser` (à installer)

**Emergent** — pipeline actuel :
Contacter le support pour ajouter `yarn build:seo` à l'étape de build,
avec Chromium disponible dans l'image (déjà présent via le PDF engine v2).

## Vérification post-run
```bash
# Chaque URL doit avoir son propre canonical
grep 'rel="canonical"' build/theme-natal/index.html

# Chaque URL doit avoir son propre H1
grep '<h1' build/blog/comprendre-le-retour-de-saturne/index.html

# Le body doit contenir du contenu réel (pas juste "Activez JavaScript")
wc -c build/theme-natal/index.html   # > 30 000 bytes attendu
```

## Comportement sans binaire Chrome
Si aucun binaire n'est trouvé, le script affiche un message et sort en code 0
→ **il ne bloque JAMAIS le build**. Le SPA reste servi normalement (SEO dégradé).

## Routes prerendered (Feb 2026 update)
Voir la constante `ROUTES` dans `scripts/prerender.js` :
- Homepage + éditoriaux (`/manifesto`, `/decouvrir`, `/cercle-solena`, `/barometre-2026`)
- 9 articles blog `/blog/:slug`
- **Hub horoscope + 36 pages signes** (12 × 3 périodes jour/semaine/mois)
- 12 pages produit (Thème natal, Synastrie, Voyage karmique, Astrocarto, etc.)
- **10 pages `/services/*`** (fix silo orphelin)
- Pages légales (mentions, CGV, confidentialité, contact)

Total : **~80 routes prerendered** (aligné sur sitemap.xml).

Pour ajouter une route SEO, éditez `ROUTES` dans `scripts/prerender.js`
**ET** `sitemap.xml` pour cohérence.
