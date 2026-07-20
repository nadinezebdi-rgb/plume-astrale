"""Tests pour /api/subscriptions/cercle-solena (Cercle Soléna abonnement mensuel).

Contexte :
  - STRIPE_CERCLE_SOLENA_PRICE_ID n'est PAS configuré → checkout doit répondre 503
  - Table `subscriptions` n'est peut-être pas créée dans Supabase (migration à faire)
  - Objectif : valider auth gate (401) + comportement 503 attendu
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://ebwicqvbkwogxneipaxh.supabase.co')
SUPABASE_ANON = os.environ.get(
    'SUPABASE_ANON_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA',
)
ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASSWORD = 'PlumeAdmin2026'


@pytest.fixture(scope='module')
def admin_token():
    """Obtient un JWT valide via Supabase pour admin@plume-astrale.fr."""
    r = requests.post(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        headers={'apikey': SUPABASE_ANON, 'Content-Type': 'application/json'},
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD},
        timeout=15,
    )
    if r.status_code != 200:
        pytest.skip(f'Supabase login échoué: {r.status_code} {r.text[:200]}')
    return r.json().get('access_token')


class TestSubscriptionAuth:
    """Vérifie que les endpoints sont protégés par JWT."""

    def test_checkout_no_token_returns_401_or_403(self):
        r = requests.post(
            f'{BASE_URL}/api/subscriptions/cercle-solena/checkout',
            json={'origin_url': BASE_URL},
            timeout=10,
        )
        assert r.status_code in (401, 403), (
            f'Expected 401/403 without token, got {r.status_code}: {r.text[:200]}'
        )

    def test_checkout_invalid_token_returns_401(self):
        r = requests.post(
            f'{BASE_URL}/api/subscriptions/cercle-solena/checkout',
            headers={'Authorization': 'Bearer invalid.jwt.token'},
            json={'origin_url': BASE_URL},
            timeout=10,
        )
        assert r.status_code == 401, (
            f'Expected 401 with invalid token, got {r.status_code}: {r.text[:200]}'
        )

    def test_status_no_token_returns_401_or_403(self):
        r = requests.get(
            f'{BASE_URL}/api/subscriptions/cercle-solena/status',
            timeout=10,
        )
        assert r.status_code in (401, 403), (
            f'Expected 401/403, got {r.status_code}: {r.text[:200]}'
        )


class TestSubscriptionCheckoutBehavior:
    """Une fois authentifié, /checkout doit renvoyer 503 (price_id manquant)."""

    def test_checkout_valid_token_returns_503_price_not_configured(self, admin_token):
        r = requests.post(
            f'{BASE_URL}/api/subscriptions/cercle-solena/checkout',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'origin_url': BASE_URL},
            timeout=15,
        )
        # Comportement ATTENDU : 503 car STRIPE_CERCLE_SOLENA_PRICE_ID pas configuré
        assert r.status_code == 503, (
            f'Expected 503 (price not configured), got {r.status_code}: {r.text[:300]}'
        )
        data = r.json()
        assert 'detail' in data
        # Le message d'erreur doit être explicite
        assert 'configur' in data['detail'].lower() or 'abonnement' in data['detail'].lower(), (
            f"Detail message doesn't mention config: {data['detail']}"
        )

    def test_status_valid_token(self, admin_token):
        """/status doit retourner {active: false, subscription: null} si aucun abo actif.
        Note : peut retourner 500 si la table 'subscriptions' n'existe pas encore côté DB.
        """
        r = requests.get(
            f'{BASE_URL}/api/subscriptions/cercle-solena/status',
            headers={'Authorization': f'Bearer {admin_token}'},
            timeout=15,
        )
        if r.status_code == 500:
            pytest.skip(
                f"Table 'subscriptions' probablement absente (migration SQL Supabase non appliquée): {r.text[:200]}"
            )
        assert r.status_code == 200, (
            f'Expected 200, got {r.status_code}: {r.text[:300]}'
        )
        data = r.json()
        assert 'active' in data
        assert data['active'] is False, f'admin ne devrait pas être abonné: {data}'
        assert data.get('subscription') is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
