"""Backend tests for Landing v2 — Lecture Complete 97€ bundle."""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
API = f'{BASE_URL}/api'


@pytest.fixture
def client():
    s = requests.Session()
    s.headers.update({'Content-Type': 'application/json'})
    return s


class TestLectureCompleteCheckout:
    def test_checkout_valid_payload(self, client):
        payload = {
            'email': 'test@t.fr',
            'first_name': 'Alice',
            'birth_date': '1990-05-15',
            'birth_time': '12:00',
            'birth_city': 'Paris',
            'birth_country': 'FR',
            'origin_url': BASE_URL,
        }
        r = client.post(f'{API}/lecture-complete/checkout', json=payload, timeout=30)
        assert r.status_code == 200, f'Body: {r.text}'
        data = r.json()
        assert 'url' in data
        assert 'session_id' in data
        assert 'checkout.stripe.com' in data['url'] or 'stripe.com' in data['url']
        assert data['session_id'].startswith('cs_')

    def test_checkout_no_body(self, client):
        r = client.post(f'{API}/lecture-complete/checkout', json=None, timeout=15)
        # FastAPI returns 422 for missing body
        assert r.status_code == 422

    def test_checkout_invalid_email(self, client):
        payload = {'email': 'notanemail', 'origin_url': BASE_URL}
        r = client.post(f'{API}/lecture-complete/checkout', json=payload, timeout=15)
        assert r.status_code == 400
        assert 'Email' in r.text or 'email' in r.text

    def test_checkout_promo_guest_no_bypass(self, client):
        """SEC-004: guest with TOUT2026 should NOT bypass — fallback to Stripe."""
        payload = {
            'email': 'guest@test.fr',
            'origin_url': BASE_URL,
            'promo_code': 'TOUT2026',
        }
        r = client.post(f'{API}/lecture-complete/checkout', json=payload, timeout=30)
        assert r.status_code == 200
        data = r.json()
        # Guest should NOT get admin_bypass; should be regular Stripe URL
        assert not data.get('admin_bypass'), f'SEC-004 VIOLATION: guest got admin bypass! {data}'
        assert data['session_id'].startswith('cs_')


class TestLectureCompleteStatus:
    def test_status_unknown_session(self, client):
        r = client.get(f'{API}/lecture-complete/status', params={'session_id': 'cs_unknown_xxx_notexist'}, timeout=15)
        assert r.status_code == 404

    def test_status_after_checkout_creation(self, client):
        # create session then poll status
        payload = {
            'email': 'poll@test.fr',
            'first_name': 'Poll',
            'birth_date': '1990-01-01',
            'birth_time': '10:00',
            'birth_city': 'Lyon',
            'origin_url': BASE_URL,
        }
        r = client.post(f'{API}/lecture-complete/checkout', json=payload, timeout=30)
        assert r.status_code == 200
        sid = r.json()['session_id']

        rs = client.get(f'{API}/lecture-complete/status', params={'session_id': sid}, timeout=15)
        assert rs.status_code == 200, f'Body: {rs.text}'
        d = rs.json()
        assert 'status' in d
        assert 'payment_status' in d
        assert 'email' in d
        assert 'admin_bypass' in d
        assert d['email'] == 'poll@test.fr'
        assert d['admin_bypass'] is False
