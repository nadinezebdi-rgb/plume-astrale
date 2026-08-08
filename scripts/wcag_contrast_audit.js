/**
 * Audit WCAG AA de contraste sur toutes les pages publiques.
 * Injecte axe-core, filtre les violations "color-contrast" (AA 4.5:1 / 3:1).
 * Sortie : /app/scripts/wcag_contrast_report.json
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE = 'https://consultation-astro.preview.emergentagent.com';

const PAGES = [
  { url: '/',                          label: 'Accueil' },
  { url: '/theme-natal',               label: 'Vente · Thème Natal' },
  { url: '/kabbale',                   label: 'Vente · Kabbale' },
  { url: '/astrocartographie',         label: 'Vente · Astrocartographie' },
  { url: '/karma-destin',              label: 'Vente · Karma & Destin' },
  { url: '/numerologie',               label: 'Vente · Numérologie' },
  { url: '/synastrie',                 label: 'Vente · Synastrie' },
  { url: '/livres',                    label: 'Livres · landing' },
  { url: '/nos-livres',                label: 'Nos livres · catalog' },
  { url: '/blog',                      label: 'Blog' },
  { url: '/temoignages',               label: 'Témoignages' },
  { url: '/contact',                   label: 'Contact' },
  { url: '/credits',                   label: 'Crédits · info' },
  { url: '/mentions-legales',          label: 'Mentions légales' },
  { url: '/cgv',                       label: 'CGV' },
  { url: '/services/tirage-tarot',     label: 'Tirage Tarot (gate)' },
  { url: '/services/chatia',           label: 'ChatIA (gate)' },
  { url: '/services/horoscope',        label: 'Horoscope' },
  { url: '/services/choix',            label: 'Choix (gate)' },
  { url: '/connexion',                 label: 'Connexion' },
  { url: '/inscription',               label: 'Inscription' },
];

const AXE_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js';

async function auditPage(page, url, label) {
  const violations = [];
  try {
    await page.goto(`${BASE}${url}`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(1200);
    // Inject axe-core
    await page.addScriptTag({ url: AXE_CDN });
    await page.waitForFunction(() => window.axe, { timeout: 8000 });
    // Run only the color-contrast check
    const result = await page.evaluate(async () => {
      const r = await window.axe.run(document, {
        runOnly: { type: 'rule', values: ['color-contrast'] },
      });
      return r.violations;
    });
    for (const v of result) {
      for (const n of v.nodes) {
        // Extract text preview + colors
        const html = n.html || '';
        const contrast = n.any?.[0]?.data;
        violations.push({
          selector: n.target?.join(' > ') || '',
          html: html.slice(0, 200),
          fg: contrast?.fgColor || null,
          bg: contrast?.bgColor || null,
          ratio: contrast?.contrastRatio || null,
          expected: contrast?.expectedContrastRatio || null,
          fontSize: contrast?.fontSize || null,
          fontWeight: contrast?.fontWeight || null,
        });
      }
    }
  } catch (e) {
    return { url, label, error: e.message, violations: [] };
  }
  return { url, label, violations };
}

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  const results = [];
  for (const p of PAGES) {
    process.stdout.write(`Auditing ${p.url}... `);
    const r = await auditPage(page, p.url, p.label);
    console.log(r.error ? `ERR (${r.error.slice(0, 60)})` : `${r.violations.length} violations`);
    results.push(r);
  }

  await browser.close();

  const outPath = '/app/scripts/wcag_contrast_report.json';
  fs.writeFileSync(outPath, JSON.stringify(results, null, 2));
  console.log(`\nReport → ${outPath}`);

  // Print concise summary
  console.log('\n══ SUMMARY ══');
  for (const r of results) {
    if (r.error) { console.log(`  ${r.label.padEnd(30)}  ERROR: ${r.error.slice(0, 50)}`); continue; }
    const flag = r.violations.length === 0 ? '✓' : '✗';
    console.log(`  ${flag} ${r.label.padEnd(30)}  ${r.violations.length} violations`);
  }
})();
