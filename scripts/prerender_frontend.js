#!/usr/bin/env node
/*
 * prerender_frontend.js — Pré-rendu statique des routes publiques via Puppeteer.
 *
 * Fait suite à l'audit qualité du 30/10/2026 (Nao) : le HTML source actuel ne
 * contient que `<div id="root"></div>` → Google reçoit une page vide, indexation
 * lente, aperçus sociaux par URL inexistants.
 *
 * Ce script :
 *   1. Démarre un serveur statique local sur `frontend/build/`
 *   2. Visite chaque route listée dans `frontend/src/config/seoRoutes.js`
 *      (VALID_ROUTES, filtrée) avec un Chromium headless
 *   3. Attend que le DOM soit stable (networkidle0 + 2s)
 *   4. Écrit le HTML rendu dans `build/<route>/index.html`
 *
 * Côté client, `src/index.js` détecte un DOM pré-rempli et bascule
 * sur `ReactDOM.hydrateRoot` → aucun flash, SPA normal après hydratation.
 *
 * Usage :
 *   node scripts/prerender_frontend.js
 *   SKIP_PRERENDER=1 node scripts/prerender_frontend.js    # no-op
 *
 * Branché via `postbuild` dans package.json. Tolère un échec (|| true dans
 * le script yarn) pour ne pas casser un deploy si Chromium n'est pas disponible.
 */
const fs = require('fs');
const path = require('path');
const http = require('http');

if (process.env.SKIP_PRERENDER === '1') {
  console.log('[prerender] SKIP_PRERENDER=1, skipping.');
  process.exit(0);
}

const FRONTEND = path.resolve(__dirname, '..', 'frontend');
const BUILD = path.join(FRONTEND, 'build');
const ROUTES_FILE = path.join(FRONTEND, 'src', 'config', 'seoRoutes.js');
const PORT = parseInt(process.env.PRERENDER_PORT || '45678', 10);

if (!fs.existsSync(BUILD)) {
  console.log('[prerender] build/ absent, skip.');
  process.exit(0);
}
if (!fs.existsSync(ROUTES_FILE)) {
  console.log('[prerender] seoRoutes.js absent, skip.');
  process.exit(0);
}

// ─────────── 1) Charger VALID_ROUTES depuis seoRoutes.js ───────────
function parseRoutes() {
  const src = fs.readFileSync(ROUTES_FILE, 'utf8');
  const m = src.match(/export\s+const\s+VALID_ROUTES\s*=\s*\[([\s\S]*?)\n\];/);
  if (!m) throw new Error('VALID_ROUTES introuvable');
  const body = m[1];
  const paths = new Set();
  const re = /path:\s*['"`]([^'"`]+)['"`]/g;
  let match;
  while ((match = re.exec(body)) !== null) paths.add(match[1]);
  // On n'intercepte pas les routes dynamiques `${s}` : parser leur map explicite.
  const horoscopeMatch = src.match(/export\s+const\s+HOROSCOPE_SIGNS\s*=\s*\[([^\]]+)\]/);
  if (horoscopeMatch) {
    const signs = horoscopeMatch[1].match(/['"`]([^'"`]+)['"`]/g) || [];
    signs.forEach(s => {
      const clean = s.replace(/['"`]/g, '');
      paths.add(`/horoscope/${clean}`);
    });
  }
  return Array.from(paths).filter(p => !p.includes('${'));
}

// ─────────── 2) Mini-serveur statique ───────────
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'application/javascript',
  '.css':  'text/css',
  '.json': 'application/json',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg':  'image/svg+xml',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ico':  'image/x-icon',
  '.map':  'application/json',
};
function serve(req, res) {
  let urlPath = decodeURIComponent(req.url.split('?')[0]);
  if (urlPath.endsWith('/')) urlPath = urlPath.slice(0, -1);
  let file = path.join(BUILD, urlPath);
  if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    file = path.join(BUILD, 'index.html'); // SPA fallback
  }
  const ext = path.extname(file).toLowerCase();
  res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
}

async function main() {
  const routes = parseRoutes();
  console.log(`[prerender] ${routes.length} routes à pré-rendre`);

  // Lazy require puppeteer-core (dans frontend/node_modules).
  let puppeteer;
  try {
    puppeteer = require(path.join(FRONTEND, 'node_modules', 'puppeteer-core'));
  } catch (e) {
    console.log('[prerender] puppeteer-core introuvable, skip.', e.message);
    process.exit(0);
  }

  const execPath = process.env.PUPPETEER_EXECUTABLE_PATH
    || (fs.existsSync('/usr/bin/google-chrome') ? '/usr/bin/google-chrome'
    : fs.existsSync('/usr/bin/chromium') ? '/usr/bin/chromium'
    : fs.existsSync('/usr/bin/chromium-browser') ? '/usr/bin/chromium-browser'
    : null);
  if (!execPath) {
    console.log('[prerender] Aucun binaire Chrome/Chromium trouvé, skip (prod servira du SPA classique).');
    process.exit(0);
  }

  const server = http.createServer(serve);
  await new Promise(resolve => server.listen(PORT, '127.0.0.1', resolve));
  console.log(`[prerender] serveur local http://127.0.0.1:${PORT}`);

  let browser;
  const stats = { ok: 0, fail: 0 };
  try {
    browser = await puppeteer.launch({
      executablePath: execPath,
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    });
    for (const route of routes) {
      const page = await browser.newPage();
      try {
        await page.setViewport({ width: 1280, height: 1024 });
        const url = `http://127.0.0.1:${PORT}${route}`;
        await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });
        // Attendre un peu que les meta/SEO dynamiques soient posées par le composant SEO
        await new Promise(r => setTimeout(r, 1500));
        const html = await page.content();
        // Chemin de sortie : /index.html pour "/", sinon <route>/index.html
        const outDir = route === '/' ? BUILD : path.join(BUILD, route);
        fs.mkdirSync(outDir, { recursive: true });
        fs.writeFileSync(path.join(outDir, 'index.html'), html, 'utf8');
        stats.ok++;
        process.stdout.write(`  ✓ ${route}\n`);
      } catch (err) {
        stats.fail++;
        process.stdout.write(`  ✗ ${route} — ${err.message.split('\n')[0]}\n`);
      } finally {
        await page.close().catch(() => {});
      }
    }
  } finally {
    if (browser) await browser.close().catch(() => {});
    server.close();
  }
  console.log(`[prerender] terminé : ${stats.ok} OK, ${stats.fail} échecs`);
  if (stats.ok === 0) process.exit(0); // tolérant pour ne pas casser le deploy
}

main().catch(err => {
  console.error('[prerender] erreur fatale :', err.message);
  process.exit(0); // tolérant
});
