#!/usr/bin/env python3
"""Audit WCAG AA de contraste (couleur uniquement) sur les pages publiques.

Injecte axe-core via CDN, filtre la règle 'color-contrast' (seuils AA 4.5:1 / 3:1),
et écrit un rapport JSON + résumé texte lisible.
"""
import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = 'https://consultation-astro.preview.emergentagent.com'
AXE_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js'

PAGES = [
    ('/', 'Accueil'),
    ('/theme-natal', 'Vente · Thème Natal'),
    ('/kabbale', 'Vente · Kabbale'),
    ('/astrocartographie', 'Vente · Astrocartographie'),
    ('/karma-destin', 'Vente · Karma & Destin'),
    ('/numerologie', 'Vente · Numérologie'),
    ('/synastrie', 'Vente · Synastrie'),
    ('/livres', 'Livres · landing'),
    ('/nos-livres', 'Nos livres · catalog'),
    ('/blog', 'Blog'),
    ('/temoignages', 'Témoignages'),
    ('/contact', 'Contact'),
    ('/credits', 'Crédits · info'),
    ('/mentions-legales', 'Mentions légales'),
    ('/cgv', 'CGV'),
    ('/services/tirage-tarot', 'Tirage Tarot (gate)'),
    ('/services/chatia', 'ChatIA (gate)'),
    ('/services/horoscope', 'Horoscope'),
    ('/services/choix', 'Choix (gate)'),
    ('/connexion', 'Connexion'),
    ('/inscription', 'Inscription'),
]

def audit_page(page, url, label):
    try:
        page.goto(f'{BASE}{url}', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(1200)
        page.add_script_tag(url=AXE_CDN)
        page.wait_for_function('window.axe !== undefined', timeout=8000)
        result = page.evaluate('''async () => {
            const r = await window.axe.run(document, {
                runOnly: { type: 'rule', values: ['color-contrast'] },
            });
            return r.violations;
        }''')
        violations = []
        for v in result:
            for n in v.get('nodes', []):
                data = (n.get('any') or [{}])[0].get('data', {}) or {}
                violations.append({
                    'selector': ' > '.join(n.get('target') or []),
                    'html': (n.get('html') or '')[:220],
                    'fg': data.get('fgColor'),
                    'bg': data.get('bgColor'),
                    'ratio': data.get('contrastRatio'),
                    'expected': data.get('expectedContrastRatio'),
                    'fontSize': data.get('fontSize'),
                    'fontWeight': data.get('fontWeight'),
                })
        return {'url': url, 'label': label, 'violations': violations, 'error': None}
    except Exception as e:
        return {'url': url, 'label': label, 'violations': [], 'error': str(e)[:200]}


def main():
    out = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/pw-browsers/chromium_headless_shell-1208/chrome-linux/headless_shell')
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        for u, l in PAGES:
            print(f'Auditing {u}... ', end='', flush=True)
            r = audit_page(page, u, l)
            if r['error']:
                print(f'ERR ({r["error"][:60]})')
            else:
                print(f'{len(r["violations"])} violations')
            out.append(r)
        browser.close()

    report_path = Path('/app/scripts/wcag_contrast_report.json')
    report_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f'\nReport → {report_path}')

    # Concise summary
    print('\n══ SUMMARY ══')
    total = 0
    for r in out:
        if r['error']:
            print(f'  ⚠ {r["label"]:<32} ERROR: {r["error"][:50]}')
            continue
        n = len(r['violations'])
        total += n
        flag = '✓' if n == 0 else '✗'
        print(f'  {flag} {r["label"]:<32} {n} violations')
    print(f'\nTotal contrast violations: {total}')


if __name__ == '__main__':
    main()
