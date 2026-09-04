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
const SIGNS = ['belier','taureau','gemeaux','cancer','lion','vierge','balance','scorpion','sagittaire','capricorne','verseau','poissons'];
const HORO_ROUTES = SIGNS.flatMap((s) => [`/horoscope/${s}`, `/horoscope/${s}/semaine`, `/horoscope/${s}/mois`]);
const SERVICES = ['tarot','compatibilite','oracle','rituel','energie','archetype','consultation','revolution-solaire','love-languages','astrosexo'];
const SERVICES_ROUTES = SERVICES.map((s) => `/services/${s}`);
const ROUTES = [
  '/',
  '/manifesto',
  '/decouvrir',
  '/cercle-solena',
  '/barometre-2026',
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
  '/theme-natal', '/theme-natal-luxe', '/theme-natal-pdf',
  '/kabbale', '/astrocartographie',
  '/karma-destin', '/karma-destin-pdf',
  '/numerologie', '/numerologie-pdf',
  '/synastrie', '/voyage-karmique', '/pack-karmique',
  '/edition-reliee',
  '/tarot-oui-non', '/tarologie', '/quotidien',
  '/horoscope',
  ...HORO_ROUTES,
  ...SERVICES_ROUTES,
  '/premium', '/cercle', '/temoignages',
  '/credits', '/charte-de-confiance',
  '/mentions-legales', '/cgv', '/confidentialite', '/contact',
];

const PORT = 5555; // Port temporaire pour serve
const BUILD_DIR = path.resolve(__dirname, '..', 'build');

async function main() {
  if (!fs.existsSync(BUILD_DIR)) {
    console.error("❌ /build introuvable. Lancez `yarn build` d'abord.");
    process.exit(1);
  }

  // Vérification puppeteer-core (SEO prerender Feb 2026 — light 5MB au lieu de 300MB)
  let puppeteer;
  try {
    puppeteer = require('puppeteer-core');
  } catch (e) {
    console.log('\n⚠ puppeteer-core non installé — prerender skippé.');
    console.log('  Pour activer le SSG SEO :');
    console.log('  $ yarn add -D puppeteer-core serve\n');
    process.exit(0); // exit 0 pour ne PAS bloquer le build
  }

  // Détecte le binaire Chromium disponible (image K8s : /usr/bin/google-chrome ou /root/bin/chromium)
  const CHROME_CANDIDATES = [
    process.env.CHROME_BIN,
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/root/bin/chromium',
    '/usr/bin/chromium-browser',
  ].filter(Boolean);
  const chromeBin = CHROME_CANDIDATES.find((p) => { try { return fs.existsSync(p); } catch { return false; } });
  if (!chromeBin) {
    console.log(`\n⚠ Aucun binaire Chrome/Chromium trouvé. Cherché : ${CHROME_CANDIDATES.join(', ')}`);
    process.exit(0);
  }
  console.log(`▸ Chrome trouvé : ${chromeBin}`);

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
    executablePath: chromeBin,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  console.log('▸ Chromium démarré');

  // Backend URL for SSR snapshot injection (F500 2026-02 · Prerender Baker)
  // Le contenu html_body de MongoDB est injecté dans <div id="root"> pour que
  // Googlebot lise le contenu SANS attendre le bundle JS.
  const SSR_API = process.env.REACT_APP_BACKEND_URL || 'https://consultation-astro.preview.emergentagent.com';
  const httpsMod = require('https');
  const httpMod = require('http');

  async function fetchSnapshot(route) {
    return new Promise((resolve) => {
      const url = `${SSR_API}/api/seo/content?path=${encodeURIComponent(route)}`;
      const mod = url.startsWith('https:') ? httpsMod : httpMod;
      const req = mod.get(url, { timeout: 4000 }, (res) => {
        if (res.statusCode !== 200) return resolve(null);
        let body = '';
        res.on('data', (c) => (body += c));
        res.on('end', () => {
          try { resolve(JSON.parse(body)); } catch { resolve(null); }
        });
      });
      req.on('error', () => resolve(null));
      req.on('timeout', () => { req.destroy(); resolve(null); });
    });
  }

  let ok = 0, ko = 0, baked = 0;
  for (const route of ROUTES) {
    const url = `http://localhost:${PORT}${route}`;
    try {
      const page = await browser.newPage();
      await page.setUserAgent('Mozilla/5.0 (compatible; PlumeSSG/1.0)');
      await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });
      await page.waitForFunction(
        () => document.querySelector('link[rel="canonical"]') !== null,
        { timeout: 10000 },
      ).catch(() => null);
      await new Promise((res) => setTimeout(res, 600));

      let html = await page.content();

      // Prerender Baker : injecte le html_body du snapshot MongoDB dans #root
      // → Googlebot voit le contenu sans exécuter le JS (crawl budget préservé).
      try {
        const snap = await fetchSnapshot(route);
        if (snap && snap.html_body && snap.html_body.length > 500) {
          const rootMarker = /<div id="root">.*?<\/div>/is;
          const injection = `<div id="root"><div data-ssr-baked="true">${snap.html_body}</div></div>`;
          if (rootMarker.test(html)) {
            html = html.replace(rootMarker, injection);
            baked++;
          }
        }
      } catch (bakeErr) {
        // silencieux — le HTML brut de Puppeteer reste le fallback
      }

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

  console.log(`\n▸ Prerender terminé — ${ok} OK / ${ko} erreurs · ${baked} snapshots MongoDB injectés.`);
  if (ko > 0) {
    console.log('  (Les routes en erreur restent servies par le SPA fallback — index.html)');
  }
}

main().catch((e) => {
  console.error('Prerender fatal:', e);
  process.exit(1);
});
