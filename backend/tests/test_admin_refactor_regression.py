"""Regression tests for the admin.py refactor (2026-02).

Vérifie que les routes extraites dans :
  - admin_users.py       (/users, /users/{id}/credits, /users/{id}/premium, /users/{id}/grant-credits, DELETE /users/{id})
  - admin_promo.py       (/promo-codes CRUD)
  - admin_pdfs.py        (/payments, /transactions, /leads, /pdfs-sent, /theme-natal/*, /cron/*, /regenerate-horoscopes)
  - admin_monitoring.py  (/alerts, /ab-stats, /cache/svg/stats, /pdf-failures/last-24h)
  - admin_viralite.py    (/tarot-share/top)
  - admin_illustrations.py (/natal-illustrations*)

restent bien accessibles sur `/api/admin/*` ET sont protégées par `require_admin`.

Pré-requis : `python tests/_admin_token_helper.py admin@plume-astrale.fr`
"""
import json
import os
import sys

import pytest
import requests
from dotenv import load_dotenv

sys.path.insert(0, '/app/backend')
load_dotenv('/app/backend/.env')


def _base_url():
    for line in open('/app/frontend/.env'):
        if line.startswith('REACT_APP_BACKEND_URL='):
            return line.split('=', 1)[1].strip().rstrip('/')
    raise RuntimeError('REACT_APP_BACKEND_URL missing')


BASE_URL = _base_url()


def _admin_headers():
    p = '/tmp/admin_session.json'
    if not os.path.exists(p):
        pytest.skip('no admin session (run tests/_admin_token_helper.py admin@plume-astrale.fr)')
    return {'Authorization': f"Bearer {json.load(open(p))['access_token']}"}


def _non_admin_token():
    sb = anon = None
    for line in open('/app/frontend/.env'):
        if line.startswith('REACT_APP_SUPABASE_URL='):
            sb = line.split('=', 1)[1].strip()
        if line.startswith('REACT_APP_SUPABASE_ANON_KEY='):
            anon = line.split('=', 1)[1].strip()
    r = requests.post(
        f'{sb}/auth/v1/token?grant_type=password',
        headers={'apikey': anon},
        json={'email': 'concours@plume-astrale.fr', 'password': 'ConcoursPlume2026!'},
        timeout=30,
    )
    if r.status_code != 200:
        pytest.skip('demo login failed')
    return r.json()['access_token']


# ─────────────────────────────────────────────────────────────────
# 1. Auth guards : toutes les routes GET refusent les anonymes (401)
#    et refusent les non-admins (403).
# ─────────────────────────────────────────────────────────────────
GET_ROUTES = [
    # admin.py (core)
    '/api/admin/stats',
    '/api/admin/chat-sessions',
    # admin_users.py
    '/api/admin/users',
    # admin_promo.py
    '/api/admin/promo-codes',
    # admin_pdfs.py
    '/api/admin/payments',
    '/api/admin/transactions',
    '/api/admin/leads',
    '/api/admin/pdfs-sent',
    # admin_monitoring.py
    '/api/admin/cache/svg/stats',
    '/api/admin/pdf-failures/last-24h',
    '/api/admin/alerts',
    '/api/admin/ab-stats?experiment=smoke',
    # admin_viralite.py
    '/api/admin/tarot-share/top',
    # admin_illustrations.py
    '/api/admin/natal-illustrations',
]


class TestAuthGuards:
    @pytest.mark.parametrize('path', GET_ROUTES)
    def test_no_token_401(self, path):
        r = requests.get(f'{BASE_URL}{path}', timeout=30)
        assert r.status_code in (401, 403), (path, r.status_code, r.text[:200])

    @pytest.mark.parametrize('path', GET_ROUTES)
    def test_non_admin_403(self, path):
        tok = _non_admin_token()
        r = requests.get(f'{BASE_URL}{path}', headers={'Authorization': f'Bearer {tok}'}, timeout=30)
        assert r.status_code == 403, (path, r.status_code, r.text[:200])


# ─────────────────────────────────────────────────────────────────
# 2. Admin OK : chaque sous-router renvoie 200 + payload bien formé
# ─────────────────────────────────────────────────────────────────
class TestAdminOK:
    def test_stats(self):
        r = requests.get(f'{BASE_URL}/api/admin/stats', headers=_admin_headers(), timeout=30)
        assert r.status_code == 200, r.text[:200]
        body = r.json()
        for key in ('users', 'revenue', 'engagement', 'updated_at'):
            assert key in body
        assert 'total' in body['users']
        assert 'total_eur' in body['revenue']

    def test_chat_sessions(self):
        r = requests.get(f'{BASE_URL}/api/admin/chat-sessions', headers=_admin_headers(), timeout=30)
        assert r.status_code == 200
        assert 'sessions' in r.json()

    def test_users_pagination_shape(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/users?page=1&page_size=5',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 200
        body = r.json()
        for key in ('users', 'total', 'page', 'page_size'):
            assert key in body
        assert body['page'] == 1
        assert body['page_size'] == 5

    def test_promo_codes_list(self):
        r = requests.get(f'{BASE_URL}/api/admin/promo-codes', headers=_admin_headers(), timeout=30)
        assert r.status_code == 200
        assert isinstance(r.json().get('codes'), list)

    def test_payments(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/payments?page=1&page_size=5',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 200
        body = r.json()
        assert 'payments' in body and 'total' in body

    def test_transactions(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/transactions?page=1&page_size=5',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 200
        body = r.json()
        assert 'transactions' in body and 'total' in body

    def test_leads(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/leads?page=1&page_size=5',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 200
        assert 'leads' in r.json()

    def test_pdfs_sent(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/pdfs-sent?page=1&page_size=5',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 200
        body = r.json()
        assert 'items' in body and 'total_completed' in body

    def test_theme_natal_search_too_short(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/theme-natal/search?q=a',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 200
        assert r.json().get('items') == []

    def test_cache_svg_stats_shape(self):
        r = requests.get(f'{BASE_URL}/api/admin/cache/svg/stats', headers=_admin_headers(), timeout=30)
        assert r.status_code == 200
        body = r.json()
        for key in ('total_files', 'total_size_bytes', 'total_size_human', 'by_chart_type'):
            assert key in body

    def test_pdf_failures(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/pdf-failures/last-24h?hours=24',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 200
        body = r.json()
        assert 'items' in body and 'window_hours' in body

    def test_alerts_filters(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/alerts?period=7d&status=open&limit=10',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 200
        body = r.json()
        # tolerant : si la table n'existe pas, flag migration_needed
        assert ('items' in body) and ('migration_needed' in body)

    def test_ab_stats_shape(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/ab-stats?experiment=refactor_smoke&period=7d',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 200
        body = r.json()
        for key in ('experiment', 'period', 'variants', 'total_events'):
            assert key in body

    def test_tarot_share_top(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/tarot-share/top?limit=5',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 200
        body = r.json()
        for key in ('items', 'total_shares', 'total_views'):
            assert key in body

    def test_natal_illustrations_list(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/natal-illustrations?limit=5',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 200
        body = r.json()
        for key in ('items', 'total', 'skip', 'limit'):
            assert key in body


# ─────────────────────────────────────────────────────────────────
# 3. Validation : query params invalides renvoient 422
# ─────────────────────────────────────────────────────────────────
class TestValidation:
    def test_users_page_size_too_big(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/users?page_size=9999',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 422

    def test_ab_stats_missing_experiment(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/ab-stats',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 422

    def test_alerts_bad_period(self):
        r = requests.get(
            f'{BASE_URL}/api/admin/alerts?period=bogus',
            headers=_admin_headers(), timeout=30,
        )
        assert r.status_code == 422


# ─────────────────────────────────────────────────────────────────
# 4. Métriques structurelles : admin.py < 300 lignes + pas de duplication
# ─────────────────────────────────────────────────────────────────
class TestRefactorHealth:
    def test_admin_py_under_300_lines(self):
        with open('/app/backend/routes/admin.py') as f:
            lines = f.readlines()
        assert len(lines) < 300, f'admin.py = {len(lines)} lignes (objectif < 300)'

    def test_no_duplicate_route_decorator(self):
        """Chaque route path n'apparaît qu'une seule fois à travers tous les admin_*.py."""
        import re
        route_re = re.compile(r"@router\.(get|post|patch|delete|put)\(['\"]([^'\"]+)['\"]")
        found = {}
        files = [
            '/app/backend/routes/admin.py',
            '/app/backend/routes/admin_users.py',
            '/app/backend/routes/admin_promo.py',
            '/app/backend/routes/admin_pdfs.py',
            '/app/backend/routes/admin_monitoring.py',
            '/app/backend/routes/admin_viralite.py',
            '/app/backend/routes/admin_illustrations.py',
        ]
        for fp in files:
            with open(fp) as f:
                for m in route_re.finditer(f.read()):
                    key = f'{m.group(1).upper()} {m.group(2)}'
                    found.setdefault(key, []).append(fp)
        dups = {k: v for k, v in found.items() if len(v) > 1}
        assert not dups, f'Routes dupliquées : {dups}'

    def test_mongo_singleton_used_in_viralite(self):
        """admin_viralite.py doit importer get_db du singleton db.py."""
        with open('/app/backend/routes/admin_viralite.py') as f:
            src = f.read()
        assert 'from db import get_db' in src
        assert 'AsyncIOMotorClient' not in src
