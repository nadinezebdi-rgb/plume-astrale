"""Regression test — Sitemap ne doit JAMAIS exposer d'URLs dépréciées (Feb 2026)

Contexte : la collection MongoDB `seo_content` peut contenir des snapshots
résiduels d'URLs qui ont depuis été 301-redirigées vers un canonical :
  /nos-livres        → /livres
  /theme-natal-luxe  → /theme-natal

Sans filtre défensif dans l'endpoint `/api/sitemap.xml`, ces URLs se
retrouvent dans le sitemap servi à Google → duplicate content signalé,
la version dépréciée reste indexée, perte de link equity.

Ce test bloque la régression en 2 endroits :
1. Le code source de server.py doit contenir la constante `_DEPRECATED_SEO_PATHS`
2. La constante doit contenir /nos-livres et /theme-natal-luxe
"""
import os
import sys

sys.path.insert(0, '/app/backend')
os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
os.environ.setdefault('DB_NAME', 'test_db')


def test_deprecated_paths_constant_defined_in_server():
    src = open('/app/backend/server.py').read()
    assert '_DEPRECATED_SEO_PATHS' in src, (
        'Constante _DEPRECATED_SEO_PATHS absente de server.py. '
        'Elle protège le sitemap contre les URLs 301-redirigées.'
    )
    # Les 2 paths critiques doivent y figurer
    assert "'/nos-livres'" in src, (
        "'/nos-livres' doit être filtré du sitemap (redirect vers /livres)"
    )
    assert "'/theme-natal-luxe'" in src, (
        "'/theme-natal-luxe' doit être filtré du sitemap (redirect vers /theme-natal)"
    )


def test_sitemap_handler_applies_deprecated_filter():
    """Le handler sitemap_xml doit skiper les paths dépréciés."""
    src = open('/app/backend/server.py').read()
    # Extrait la fonction sitemap_xml
    idx = src.find('async def sitemap_xml')
    assert idx >= 0
    fn_src = src[idx:idx + 2000]
    assert '_DEPRECATED_SEO_PATHS' in fn_src, (
        "sitemap_xml() n'applique pas le filtre _DEPRECATED_SEO_PATHS — "
        "les URLs dépréciées vont réapparaître dans le sitemap."
    )
    assert 'continue' in fn_src, (
        "Attendu 'continue' pour skipper les URLs dépréciées dans la boucle."
    )
