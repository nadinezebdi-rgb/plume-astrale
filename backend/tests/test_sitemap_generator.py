"""Tests du générateur de sitemap.xml (SEO Audit Feb 2026)."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # /app
sys.path.insert(0, str(ROOT))

from scripts.generate_sitemap import build_sitemap, _extract_js_array, _extract_horoscope_signs


def test_sitemap_builds_without_error():
    xml = build_sitemap()
    assert xml.startswith('<?xml')
    assert '</urlset>' in xml.strip()


def test_sitemap_contains_homepage():
    xml = build_sitemap()
    assert '<loc>https://plume-astrale.fr/</loc>' in xml


def test_sitemap_contains_all_blog_articles():
    """Les 9+ articles de blogArticles.js doivent apparaître."""
    xml = build_sitemap()
    articles = _extract_js_array(ROOT / 'frontend' / 'src' / 'config' / 'blogArticles.js',
                                 'BLOG_ARTICLES')
    assert len(articles) >= 9
    for a in articles:
        assert f'/blog/{a["slug"]}' in xml, f'Article manquant : {a["slug"]}'


def test_sitemap_contains_12_horoscope_signs_no_period():
    """Les 12 /horoscope/<signe> présents, mais pas les 24 week/month."""
    xml = build_sitemap()
    signs = _extract_horoscope_signs(ROOT / 'frontend' / 'src' / 'config' / 'seoRoutes.js')
    assert len(signs) == 12
    for s in signs:
        assert f'/horoscope/{s}</loc>' in xml, f'Signe manquant : {s}'
    # Les semaine/mois NE doivent PAS être dans le sitemap
    assert '/semaine' not in xml
    assert '/mois</loc>' not in xml


def test_sitemap_excludes_private_and_noindex_pages():
    xml = build_sitemap()
    forbidden = [
        '/mentions-legales',
        '/cgv</loc>',
        '/confidentialite</loc>',
        '/panier',
        '/mon-compte',
        '/mon-accueil',
        '/admin',
        '/dashboard',
        '/paiement</loc>',
        '/commande',
        '/desabonnement',
        '/mot-de-passe-oublie',
        '/reinitialiser-mot-de-passe',
    ]
    for u in forbidden:
        assert u not in xml, f'URL interdite présente : {u}'


def test_sitemap_excludes_redirect_sources():
    """Aucune URL qui 301 ne doit figurer dans le sitemap."""
    xml = build_sitemap()
    redirect_sources = [
        '/temoignage</loc>',
        '/home-experience-v3',
        '/compatibilite-amoureuse</loc>',
        '/politique-de-confidentialite',
        '/privacy</loc>',
        '/nos-livres',
        '/kabbale</loc>',
        '/karma-destin',
        '/karma-destin-pdf',
        '/premium</loc>',
        '/theme-natal-luxe',
        '/outils/',
        '/tirage-tarot',
    ]
    for u in redirect_sources:
        assert u not in xml, f'URL de redirection présente : {u}'


def test_sitemap_contains_canonical_services():
    """Les /services/* canoniques doivent être présents."""
    xml = build_sitemap()
    for svc in ['/services/theme-natal', '/services/tarot', '/services/numerologie',
                '/services/compatibilite', '/services/oracle', '/services/rituel']:
        assert svc in xml, f'Service canonique manquant : {svc}'
