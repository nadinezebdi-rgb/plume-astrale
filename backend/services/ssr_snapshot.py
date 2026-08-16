"""
SSR Snapshot Registry — F500 SEO Rebuild (2026-02).

Chaque route "SEO-critique" a un snapshot HTML pré-rendu stocké dans MongoDB
(collection `seo_content`). Le crawler Playwright headless capture le HTML
rendu par React (côté client), puis l'écrit en base avec :
  - path, meta_title, meta_desc, canonical, og_image
  - h1, html_body (contenu visible)
  - jsonld[] (schemas structurés)
  - hreflang[]
  - updated_at, cache_ttl_hours (1h pour horoscopes, 24h pour sales pages)

L'endpoint /api/seo/{path} sert ces snapshots à Googlebot ou à tout
crawler. Le prerender.js au build time les injecte dans les HTML statiques
générés dans /app/frontend/build/.

Approche non-cloaking : les MÊMES données servies à tous. Aucune détection UA.
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SIGNS = ['belier','taureau','gemeaux','cancer','lion','vierge','balance','scorpion','sagittaire','capricorne','verseau','poissons']
BLOG_SLUGS = [
    'calculer-son-chemin-de-vie-avec-precision',
    'interpreter-venus-en-astrologie',
    'comprendre-le-retour-de-saturne',
    'theme-natal-vocation-professionnelle',
    'compatibilite-amoureuse-selon-theme-natal',
    'signification-des-maisons-astrologiques',
    'comment-connaitre-son-ascendant-astrologique',
    'previsions-astrologiques-personnalisees-2026',
    'theme-astral-personnalise-gratuit',
]

# Routes MVP (Étape 1a — Top 20) + Extension Phase 2 (~40 routes)
_STATIC_ROUTES = [
    # Home + tunnel principal
    {'path': '/', 'ttl_hours': 24, 'priority': 1.0},
    {'path': '/decouvrir', 'ttl_hours': 24, 'priority': 0.9},
    {'path': '/manifesto', 'ttl_hours': 168, 'priority': 0.7},
    {'path': '/cercle-solena', 'ttl_hours': 24, 'priority': 0.95},
    {'path': '/nos-livres', 'ttl_hours': 24, 'priority': 0.85},
    {'path': '/blog', 'ttl_hours': 12, 'priority': 0.9},
    {'path': '/temoignage', 'ttl_hours': 24, 'priority': 0.6},
    {'path': '/credits', 'ttl_hours': 24, 'priority': 0.75},
    {'path': '/barometre-2026', 'ttl_hours': 24, 'priority': 0.7},
    # Sales pages
    {'path': '/theme-natal-luxe', 'ttl_hours': 24, 'priority': 0.95},
    {'path': '/theme-natal', 'ttl_hours': 24, 'priority': 0.9},
    {'path': '/kabbale', 'ttl_hours': 24, 'priority': 0.85},
    {'path': '/astrocartographie', 'ttl_hours': 24, 'priority': 0.85},
    {'path': '/synastrie', 'ttl_hours': 24, 'priority': 0.85},
    {'path': '/numerologie-pdf', 'ttl_hours': 24, 'priority': 0.8},
    {'path': '/karma-destin-pdf', 'ttl_hours': 24, 'priority': 0.8},
    {'path': '/pack-karmique', 'ttl_hours': 24, 'priority': 0.8},
    # Horoscope index
    {'path': '/horoscope', 'ttl_hours': 6, 'priority': 0.9},
]

# 12 signes × (jour + semaine + mois) + articles blog
_HOROSCOPE_ROUTES = [
    {'path': f'/horoscope/{s}', 'ttl_hours': 6, 'priority': 0.7} for s in SIGNS
] + [
    {'path': f'/horoscope/{s}/semaine', 'ttl_hours': 24, 'priority': 0.6} for s in SIGNS
] + [
    {'path': f'/horoscope/{s}/mois', 'ttl_hours': 168, 'priority': 0.55} for s in SIGNS
]

_BLOG_ROUTES = [{'path': f'/blog/{slug}', 'ttl_hours': 168, 'priority': 0.65} for slug in BLOG_SLUGS]

SEO_ROUTES = _STATIC_ROUTES + _HOROSCOPE_ROUTES + _BLOG_ROUTES  # ~64 routes total

BASE_URL_INTERNAL = 'http://localhost:3000'  # frontend interne, non-public
CHROMIUM_PATH = '/pw-browsers/chromium_headless_shell-1208/chrome-linux/headless_shell'


async def snapshot_route(path: str, ttl_hours: int) -> dict:
    """Rend une route via Playwright headless et extrait le contenu SEO."""
    from playwright.async_api import async_playwright
    url = f'{BASE_URL_INTERNAL}{path}'
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=CHROMIUM_PATH,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
        )
        try:
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (compatible; PlumeSSRBot/1.0)',
            )
            page = await context.new_page()
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(1500)  # React hydration + async data
            # Extract SEO-critical data
            data = await page.evaluate("""() => {
              const meta = (name) => document.querySelector(`meta[name="${name}"]`)?.content
                || document.querySelector(`meta[property="${name}"]`)?.content || '';
              const jsonld = Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
                .map(s => { try { return JSON.parse(s.textContent); } catch { return null; } })
                .filter(x => x);
              const canonical = document.querySelector('link[rel="canonical"]')?.href || location.href;
              const h1 = document.querySelector('h1')?.innerText?.trim() || '';
              // Contenu visible : on ne prend que le main / role=main / role=article, fallback body
              const main = document.querySelector('main, [role="main"], #root > div');
              return {
                meta_title: document.title,
                meta_desc: meta('description') || meta('og:description'),
                canonical,
                og_image: meta('og:image'),
                og_type: meta('og:type') || 'website',
                h1,
                html_body: main ? main.innerHTML.slice(0, 100000) : '',  // cap 100KB
                jsonld,
                lang: document.documentElement.lang || 'fr',
              };
            }""")
            await context.close()
            return data
        finally:
            await browser.close()


def _get_mongo():
    """Lazy connection to MongoDB (uses backend MONGO_URL)."""
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    if not mongo_url or not db_name:
        raise RuntimeError('MONGO_URL/DB_NAME manquants')
    return AsyncIOMotorClient(mongo_url)[db_name]


async def save_snapshot(route: dict, data: dict) -> None:
    """Enregistre le snapshot en base (upsert par path) + ping IndexNow.

    SEO P1 (2026-02-16) :
      - Force canonical = PUBLIC_DOMAIN + path (jamais localhost)
      - Strip SearchAction du JSON-LD (endpoint /?q= n'existe pas côté site)
    """
    db = _get_mongo()
    now = datetime.now(timezone.utc)

    # Force canonical propre (jamais localhost:3000 même si extrait tôt)
    data['canonical'] = f'{PUBLIC_DOMAIN}{route["path"]}'

    # Strip SearchAction des JSON-LD extraits
    if isinstance(data.get('jsonld'), list):
        cleaned = []
        for schema in data['jsonld']:
            if not isinstance(schema, dict):
                continue
            action = schema.get('potentialAction')
            if isinstance(action, dict) and action.get('@type') == 'SearchAction':
                schema = {k: v for k, v in schema.items() if k != 'potentialAction'}
            cleaned.append(schema)
        data['jsonld'] = cleaned

    doc = {
        **data,
        'path': route['path'],
        'ttl_hours': route['ttl_hours'],
        'priority': route['priority'],
        'updated_at': now.isoformat(),
        'expires_at': (now + timedelta(hours=route['ttl_hours'])).isoformat(),
    }
    await db.seo_content.update_one({'path': route['path']}, {'$set': doc}, upsert=True)
    # Ping IndexNow (Bing/Yandex/Naver) — non-bloquant, best-effort
    try:
        await _ping_indexnow(route['path'])
    except Exception as e:
        logger.debug(f'[ssr] indexnow ping skipped for {route["path"]}: {e}')


PUBLIC_DOMAIN = os.environ.get('SEO_PUBLIC_DOMAIN', 'https://plume-astrale.fr').rstrip('/')
INDEXNOW_KEY = os.environ.get('INDEXNOW_KEY', '').strip()


async def _ping_indexnow(path: str) -> None:
    """Notifie IndexNow (Bing/Yandex) qu'une URL vient d'être mise à jour.

    Nécessite INDEXNOW_KEY dans .env et un fichier /{key}.txt à la racine
    du domaine contenant la clé (validation propriété). No-op si absent.
    """
    if not INDEXNOW_KEY:
        return
    import httpx
    url = f'{PUBLIC_DOMAIN}{path}'
    payload = {
        'host': PUBLIC_DOMAIN.replace('https://', '').replace('http://', ''),
        'key': INDEXNOW_KEY,
        'keyLocation': f'{PUBLIC_DOMAIN}/{INDEXNOW_KEY}.txt',
        'urlList': [url],
    }
    async with httpx.AsyncClient(timeout=5) as client:
        await client.post('https://api.indexnow.org/indexnow', json=payload)


async def get_snapshot(path: str) -> Optional[dict]:
    """Récupère le snapshot d'une route ou None si absent."""
    db = _get_mongo()
    return await db.seo_content.find_one({'path': path}, {'_id': 0})


async def refresh_all(only_expired: bool = True) -> dict:
    """Rafraîchit tous les snapshots. Si only_expired=True, ne refresh que ceux dont TTL est dépassé."""
    stats = {'refreshed': [], 'skipped': [], 'errors': []}
    db = _get_mongo()
    now = datetime.now(timezone.utc)
    for route in SEO_ROUTES:
        try:
            if only_expired:
                existing = await db.seo_content.find_one({'path': route['path']}, {'expires_at': 1})
                if existing and existing.get('expires_at'):
                    exp = datetime.fromisoformat(existing['expires_at'])
                    if exp.tzinfo is None:
                        exp = exp.replace(tzinfo=timezone.utc)
                    if exp > now:
                        stats['skipped'].append(route['path'])
                        continue
            data = await snapshot_route(route['path'], route['ttl_hours'])
            await save_snapshot(route, data)
            stats['refreshed'].append(route['path'])
            logger.info(f'[ssr] ✓ {route["path"]} — H1: {data.get("h1", "")[:60]}')
        except Exception as e:
            logger.warning(f'[ssr] ✗ {route["path"]} — {e}')
            stats['errors'].append({'path': route['path'], 'error': str(e)[:200]})
    return stats


async def ssr_refresh_loop() -> None:
    """Background task — refresh les snapshots expirés toutes les heures."""
    logger.info('[ssr] refresh loop démarrée — cycle 1h')
    # Bootstrap : première passe au démarrage (only_expired=False force le refresh initial)
    try:
        await asyncio.sleep(30)  # laisse le frontend démarrer
        first = await refresh_all(only_expired=False)
        logger.info(f'[ssr] bootstrap : {len(first["refreshed"])} snapshots créés, {len(first["errors"])} erreurs')
    except Exception as e:
        logger.warning(f'[ssr] bootstrap failed : {e}')
    while True:
        try:
            await asyncio.sleep(3600)  # 1h
            stats = await refresh_all(only_expired=True)
            if stats['refreshed']:
                logger.info(f'[ssr] cycle : {len(stats["refreshed"])} refreshed, {len(stats["skipped"])} skipped')
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception(f'[ssr] cycle error : {e}')
