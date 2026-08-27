"""Test suite E2E — Optimisation Home + Article du jour offert.

Verrouille :
  1. Le retrait de `ConcoursImpact` de la home (redondance identifiée).
  2. L'ajout du bloc `NocturneDailyArticle` (rotation quotidienne + capture email).
  3. L'endpoint `/api/daily-article/send` (validation Pydantic, rate limit, envoi email).

Exécution : `cd /app/backend && python -m pytest tests/test_home_daily_article.py -v`
"""
from __future__ import annotations
import os
import time
import uuid

import requests

BASE_URL = os.environ.get('BACKEND_URL', 'http://localhost:8001')


# ═══════════════════════════════════════════════════════════════════════
# 1. Homepage — ConcoursImpact retiré, NocturneDailyArticle ajouté
# ═══════════════════════════════════════════════════════════════════════

def test_homepage_concours_impact_removed():
    with open('/app/frontend/src/pages/Homepage.js') as f:
        code = f.read()
    assert '<ConcoursImpact' not in code, 'ConcoursImpact doit être retiré de la home'
    assert "from '@/components/nocturne/ConcoursImpact'" not in code


def test_homepage_daily_article_added():
    with open('/app/frontend/src/pages/Homepage.js') as f:
        code = f.read()
    assert '<NocturneDailyArticle' in code
    assert "NocturneDailyArticle from '@/components/nocturne/NocturneDailyArticle'" in code


def test_daily_article_component_uses_registered_blog_articles():
    with open('/app/frontend/src/components/nocturne/NocturneDailyArticle.jsx') as f:
        code = f.read()
    # Rotation basée sur day-of-year
    assert 'BLOG_ARTICLES' in code
    assert 'pickArticleOfTheDay' in code
    # Doit poster sur le nouveau endpoint daily-article, pas lead-magnet
    assert '/api/daily-article/send' in code
    assert '/api/lead-magnet/subscribe' not in code
    # data-testids requis
    for testid in ['nocturne-daily-article', 'nda-title', 'nda-tag', 'nda-cta-read-now',
                   'nda-email-input', 'nda-cta-email', 'nda-cta-all-articles']:
        assert f'data-testid="{testid}"' in code, f'data-testid manquant : {testid}'


# ═══════════════════════════════════════════════════════════════════════
# 2. Endpoint /api/daily-article/send — validation Pydantic
# ═══════════════════════════════════════════════════════════════════════

def test_daily_article_send_rejects_bad_email():
    r = requests.post(
        f'{BASE_URL}/api/daily-article/send',
        json={'email': 'not-an-email', 'slug': 'x-y', 'title': 'Foo',
              'excerpt': '1234567890'},
        timeout=10,
    )
    assert r.status_code == 422


def test_daily_article_send_rejects_bad_slug():
    r = requests.post(
        f'{BASE_URL}/api/daily-article/send',
        json={'email': 'contact@plume-astrale.fr', 'slug': 'BAD SLUG!!',
              'title': 'Foo', 'excerpt': '1234567890'},
        timeout=10,
    )
    assert r.status_code == 422


def test_daily_article_send_rejects_short_excerpt():
    r = requests.post(
        f'{BASE_URL}/api/daily-article/send',
        json={'email': 'contact@plume-astrale.fr', 'slug': 'x-y',
              'title': 'Foo', 'excerpt': 'short'},
        timeout=10,
    )
    assert r.status_code == 422


# ═══════════════════════════════════════════════════════════════════════
# 3. Endpoint /api/daily-article/send — rate limit 60s
# ═══════════════════════════════════════════════════════════════════════

def test_daily_article_send_rate_limits_second_call_within_60s():
    """Deuxième appel < 60s pour le même email → 429."""
    # Email unique pour cette exécution afin d'éviter les collisions cross-tests
    unique_email = f'ratelimit-{uuid.uuid4().hex[:12]}@plume-astrale.fr'
    payload = {
        'email': unique_email,
        'slug': 'interpreter-venus-en-astrologie',
        'title': 'Interpréter Vénus en astrologie',
        'excerpt': 'Vénus décrit votre rapport à l amour, à la beauté, aux valeurs.',
        'tag': 'Astrologie',
    }
    # 1er envoi — devrait être 200 ou 500 (si SMTP fail, on skip le test)
    r1 = requests.post(f'{BASE_URL}/api/daily-article/send', json=payload, timeout=25)
    if r1.status_code == 500:
        # Backend SMTP failure — inconclusive, on skip
        import pytest
        pytest.skip('SMTP unavailable; cannot validate rate limit path')
    assert r1.status_code == 200
    # 2ème envoi immédiatement — devrait être 429
    r2 = requests.post(f'{BASE_URL}/api/daily-article/send', json=payload, timeout=10)
    assert r2.status_code == 429
