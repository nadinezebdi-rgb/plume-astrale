#!/usr/bin/env python3
"""
generate_sitemap.py — Régénérateur automatique du sitemap.xml (SEO Audit Feb 2026).

Source unique de vérité : /app/frontend/src/config/seoRoutes.js (VALID_ROUTES)
et /app/frontend/src/config/blogArticles.js (BLOG_ARTICLES).

Garanties :
  • Seulement des URLs canoniques (listées dans VALID_ROUTES, sans paramètres).
  • Tous les articles du registre blogArticles.js sont inclus.
  • <lastmod> = date de modification du fichier source correspondant.
  • Aucune URL exclue (noindex, succès, admin, auth) n'est présente.

Usage :
    python scripts/generate_sitemap.py          # écrit /app/frontend/public/sitemap.xml
    python scripts/generate_sitemap.py --dry    # ne touche à aucun fichier, print à stdout

Peut être branché à `yarn build` via package.json (prebuild hook) pour que le
sitemap soit régénéré à chaque déploiement.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
FRONTEND_SRC = ROOT / 'frontend' / 'src'
PUBLIC_DIR = ROOT / 'frontend' / 'public'
DOMAIN = 'https://plume-astrale.fr'


def _extract_js_array(js_path: Path, var_name: str) -> list[dict]:
    """Extrait un export `const <var_name> = [ ... ]` d'un fichier JS en liste de dicts."""
    content = js_path.read_text(encoding='utf-8')
    m = re.search(rf"export\s+const\s+{re.escape(var_name)}\s*=\s*\[", content)
    if not m:
        raise ValueError(f'{var_name} introuvable dans {js_path}')
    start = m.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '[':
            depth += 1
        elif content[i] == ']':
            depth -= 1
        i += 1
    body = content[start:i - 1]
    # Parse chaque entrée `{ ... }`
    entries = []
    for match in re.finditer(r'\{[^{}]*\}', body):
        raw = match.group(0)
        entry: dict = {}
        for key_match in re.finditer(
            r"([a-zA-Z_]\w*)\s*:\s*('((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"|([-0-9.]+)|\[[^\]]*\])",
            raw,
        ):
            key = key_match.group(1)
            val = key_match.group(2)
            if val.startswith("'") or val.startswith('"'):
                val = val[1:-1]
            try:
                val = float(val) if '.' in val else int(val)
            except Exception:
                pass
            entry[key] = val
        entries.append(entry)
    return entries


def _extract_horoscope_signs(js_path: Path) -> list[str]:
    content = js_path.read_text(encoding='utf-8')
    m = re.search(r"export\s+const\s+HOROSCOPE_SIGNS\s*=\s*\[([^\]]*)\]", content)
    if not m:
        return []
    return [s.strip().strip("'\"") for s in m.group(1).split(',') if s.strip()]


def _file_mtime_iso(file_path: Path) -> str:
    """Renvoie la date de modification au format YYYY-MM-DD (UTC)."""
    try:
        ts = file_path.stat().st_mtime
        return dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).strftime('%Y-%m-%d')
    except Exception:
        return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')


def _route_mtime(path: str) -> str:
    """Trouve le fichier React associé à une route et renvoie son mtime."""
    pages_dir = FRONTEND_SRC / 'pages'
    # Heuristique naïve : /theme-natal → ThemeNatal*.{js,jsx}, /blog/foo → BlogArticle.js
    if path == '/':
        candidates = list(pages_dir.glob('HomeExperienceV3.*')) or list(pages_dir.glob('Home*.js*'))
    elif path.startswith('/blog/'):
        candidates = [pages_dir / 'BlogArticle.js']
    elif path == '/blog':
        candidates = [pages_dir / 'Blog.js']
    elif path.startswith('/horoscope/'):
        candidates = [pages_dir / 'HoroscopeSign.js']
    elif path == '/horoscope':
        candidates = [pages_dir / 'Horoscope.js']
    elif path.startswith('/services/'):
        slug = path.split('/')[-1]
        candidates = list(pages_dir.glob(f'{slug.capitalize()}*.*'))
    else:
        slug = path.strip('/').replace('/', '_').replace('-', '_')
        candidates = list(pages_dir.glob(f'{slug}*.*'))
    for c in candidates:
        if c.is_file():
            return _file_mtime_iso(c)
    # Fallback : date du jour
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')


def build_sitemap() -> str:
    seo_routes_path = FRONTEND_SRC / 'config' / 'seoRoutes.js'
    blog_articles_path = FRONTEND_SRC / 'config' / 'blogArticles.js'

    if not seo_routes_path.exists():
        raise FileNotFoundError(f'Source introuvable : {seo_routes_path}')
    if not blog_articles_path.exists():
        raise FileNotFoundError(f'Source introuvable : {blog_articles_path}')

    # Parse routes et exclusions
    valid_routes = _extract_js_array(seo_routes_path, 'VALID_ROUTES')
    signs = _extract_horoscope_signs(seo_routes_path)

    # Les 12 /horoscope/<signe> ne sont pas littéralement dans VALID_ROUTES
    # (ils sont générés par .map()). Ajoute-les manuellement.
    existing_paths = {r['path'] for r in valid_routes if 'path' in r}
    for s in signs:
        if f'/horoscope/{s}' not in existing_paths:
            valid_routes.append({'path': f'/horoscope/{s}', 'priority': 0.75, 'changefreq': 'weekly'})

    # Parse les articles de blog
    blog_articles = _extract_js_array(blog_articles_path, 'BLOG_ARTICLES')

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append(f'<!-- Plume Astrale — sitemap.xml, régénéré automatiquement le '
                 f'{dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")} par scripts/generate_sitemap.py -->')
    lines.append('<!-- Source : /app/frontend/src/config/{seoRoutes.js, blogArticles.js} -->')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    seen = set()

    def _append(path: str, prio: float, changefreq: str, lastmod: str) -> None:
        if path in seen:
            return
        seen.add(path)
        loc = f'{DOMAIN}{path}' if path != '/' else f'{DOMAIN}/'
        lines.append('  <url>')
        lines.append(f'    <loc>{escape(loc)}</loc>')
        lines.append(f'    <lastmod>{lastmod}</lastmod>')
        lines.append(f'    <changefreq>{changefreq}</changefreq>')
        lines.append(f'    <priority>{prio}</priority>')
        lines.append('  </url>')

    # Routes canoniques
    for r in valid_routes:
        if 'path' not in r:
            continue
        path = r['path']
        prio = r.get('priority', 0.5)
        cf = r.get('changefreq', 'monthly')
        _append(path, float(prio), str(cf), _route_mtime(path))

    # Articles de blog (lastmod = date de publication dans le registre)
    for a in blog_articles:
        if 'slug' not in a:
            continue
        slug = a['slug']
        pub_date = a.get('date', _file_mtime_iso(blog_articles_path))
        _append(f'/blog/{slug}', 0.7, 'monthly', str(pub_date))

    lines.append('</urlset>')
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry', action='store_true', help='Affiche le résultat sans écrire')
    parser.add_argument('--out', type=Path, default=PUBLIC_DIR / 'sitemap.xml',
                        help='Fichier de sortie (défaut : frontend/public/sitemap.xml)')
    parser.add_argument('--nginx-slugs-out', type=Path,
                        default=ROOT / 'deploy' / 'nginx-blog-slugs.conf',
                        help='Fichier nginx fragment avec les slugs blog connus')
    args = parser.parse_args()

    xml = build_sitemap()
    if args.dry:
        print(xml)
    else:
        args.out.write_text(xml, encoding='utf-8')
        n = xml.count('<url>')
        print(f'OK · {n} URLs écrites → {args.out}')

        # Fragment nginx : liste explicite des slugs blog connus.
        articles = _extract_js_array(FRONTEND_SRC / 'config' / 'blogArticles.js', 'BLOG_ARTICLES')
        slugs = sorted({a['slug'] for a in articles if 'slug' in a})
        regex = '|'.join(re.escape(s) for s in slugs)
        nginx_fragment = (
            '# Auto-généré par scripts/generate_sitemap.py — ne pas éditer manuellement.\n'
            '# Slugs d\'articles de blog connus (BLOG_ARTICLES). Toute autre URL /blog/<slug>\n'
            '# renverra 404 côté serveur.\n'
            f'location ~ ^/blog/({regex})/?$ {{\n'
            '    try_files /index.html =404;\n'
            '}\n'
        )
        args.nginx_slugs_out.write_text(nginx_fragment, encoding='utf-8')
        print(f'OK · {len(slugs)} slugs → {args.nginx_slugs_out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
