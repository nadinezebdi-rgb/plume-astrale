#!/usr/bin/env node
/**
 * scripts/prerender.js — SSG maison pour CRA React 19 (SEO P3).
 *
 * Rend chaque route publique en HTML statique complet (incluant les meta
 * dynamiques posés par SEO.js) et écrit le résultat dans build/{route}/index.html.
 * Résultat : Googlebot obtient tout le HTML SEO dès le premier byte.
 *
 * Pré-requis (à installer une seule fois avant le premier `yarn prerender`) :
 *   yarn add -D puppeteer serve
 *
 * Usage local :
 *   yarn build && yarn prerender
 *
 * Usage CI/CD (à ajouter dans le pipeline de déploiement) :
 *   1. yarn install --frozen-lockfile
 *   2. yarn build
 *   3. yarn prerender    ← insère ce hook avant la publication
 *   4. déployer /build sur le CDN / hébergeur
 *
 * Le script est TOLÉRANT : si puppeteer n'est pas installé, il affiche une
 * commande d'installation et sort en code 0 → ne bloque pas le build.
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Routes à prerendrer (alignées sur sitemap.xml — pages publiques uniquement)
const ROUTES = [
  '/',
  '/manifesto',
  '/decouvrir',
  '/blog',
  '/blog/calculer-son-chemin-de-vie-avec-precision',
  '/blog/interpreter-venus-en-astrologie',
  '/blog/comprendre-le-retour-de-saturne',
  '/blog/theme-natal-vocation-professionnelle',
  '/blog/compatibilite-amoureuse-selon-theme-natal',
  '/blog/signification-des-maisons-astrologiques',
  '/blog/comment-connaitre-son-ascendant-astrologique',
  '/blog/previsions-astrologiques-personnalisees-2026',
  '/blog/theme-astral-personnalise-gratuit',
  '/nos-livres', '/livres',
  '/theme-natal', '/theme-natal-luxe',
  '/kabbale', '/astrocartographie',
  '/karma-destin', '/karma-destin-pdf',
  '/numerologie', '/numerologie-pdf',
  '/synastrie',
  '/tarot-oui-non', '/tarologie', '/quotidien',
  '/horoscope',
  '/horoscope/belier', '/horoscope/taureau', '/horoscope/gemeaux',
  '/horoscope/cancer', '/horoscope/lion', '/horoscope/vierge',
  '/horoscope/balance', '/horoscope/scorpion', '/horoscope/sagittaire',
  '/horoscope/capricorne', '/horoscope/verseau', '/horoscope/poissons',
  '/compatibilite-amoureuse', '/astrosexo', '/archetype',
  '/premium', '/cercle', '/temoignage',
  '/credits', '/charte-de-confiance',
  '/mentions-legales', '/cgv',
];

const PORT = 5555; // Port temporaire pour serve
const BUILD_DIR = path.resolve(__dirname, '..', 'build');

async function main() {
  if (!fs.existsSync(BUILD_DIR)) {
    console.error("❌ /build introuvable. Lancez `yarn build` d'abord.");
    process.exit(1);
  }

  // Vérification puppeteer (optionnel)
  let puppeteer;
  try {
    puppeteer = require('puppeteer');
  } catch (e) {
    console.log('\n⚠ puppeteer non installé — prerender skippé.');
    console.log('  Pour activer le SSG SEO :');
    console.log('  $ yarn add -D puppeteer serve\n');
    process.exit(0); // exit 0 pour ne PAS bloquer le build
  }

  // Vérification serve
  let serveBin;
  try {
    serveBin = require.resolve('serve/build/main.js');
  } catch (e) {
    console.log('\n⚠ serve non installé — prerender skippé.');
    console.log('  $ yarn add -D serve\n');
    process.exit(0);
  }

  // Lance serve -s build -l PORT en arrière-plan
  console.log(`▸ Lance serve -s build sur http://localhost:${PORT}`);
  const serveProc = spawn('node', [serveBin, '-s', BUILD_DIR, '-l', String(PORT), '--no-clipboard'], {
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  // Attente que le serveur soit up
  await new Promise((res) => setTimeout(res, 2000));

  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  console.log('▸ Chromium démarré');

  let ok = 0, ko = 0;
  for (const route of ROUTES) {
    const url = `http://localhost:${PORT}${route}`;
    try {
      const page = await browser.newPage();
      await page.setUserAgent('Mozilla/5.0 (compatible; PlumeSSG/1.0)');
      await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });
      // Attend que React ait fini son travail (SEO.js pose les meta dans useEffect)
      await page.waitForFunction(
        () => document.querySelector('link[rel="canonical"]') !== null,
        { timeout: 10000 },
      ).catch(() => null);
      // Petite marge additionnelle pour les IntersectionObserver / lazy sections
      await new Promise((res) => setTimeout(res, 600));

      const html = await page.content();
      const outPath = route === '/' ? path.join(BUILD_DIR, 'index.html') : path.join(BUILD_DIR, route, 'index.html');
      fs.mkdirSync(path.dirname(outPath), { recursive: true });
      fs.writeFileSync(outPath, html, 'utf8');
      console.log(`  ✓ ${route}  →  ${path.relative(BUILD_DIR, outPath)}`);
      ok++;
      await page.close();
    } catch (e) {
      console.warn(`  ✗ ${route}  →  ${e.message}`);
      ko++;
    }
  }

  await browser.close();
  serveProc.kill('SIGTERM');

  console.log(`\n▸ Prerender terminé — ${ok} OK / ${ko} erreurs sur ${ROUTES.length} routes.`);
  if (ko > 0) {
    console.log('  (Les routes en erreur restent servies par le SPA fallback — index.html)');
  }
}

main().catch((e) => {
  console.error('Prerender fatal:', e);
  process.exit(1);
});
