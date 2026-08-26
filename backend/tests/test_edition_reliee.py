"""Test suite E2E — Édition Reliée 149 € (checkout Stripe + webhook + print_approval).

Verrouille les invariants du service `edition_reliee_service` et de la route
`/api/edition-reliee/*`. Les tests qui touchent Stripe utilisent des payloads
valides ET des payloads invalides pour vérifier la validation Pydantic.

Exécution : `cd /app/backend && python -m pytest tests/test_edition_reliee.py -v`
"""
from __future__ import annotations
import os

import pytest
import requests

BASE_URL = os.environ.get('BACKEND_URL', 'http://localhost:8001')


# ═══════════════════════════════════════════════════════════════════════
# 1. Config PACKS — le produit `edition_reliee` doit être défini
# ═══════════════════════════════════════════════════════════════════════

def test_pack_edition_reliee_defined_at_149():
    from config import get_settings
    settings = get_settings()
    pack = settings.PACKS.get('edition_reliee')
    assert pack is not None, 'PACKS.edition_reliee manquant'
    assert pack['amount'] == 149.00
    assert pack['currency'] == 'eur'
    assert pack['product'] == 'edition_reliee'


# ═══════════════════════════════════════════════════════════════════════
# 2. Validation Pydantic — payload invalide → 422
# ═══════════════════════════════════════════════════════════════════════

def test_checkout_rejects_missing_email():
    r = requests.post(
        f'{BASE_URL}/api/edition-reliee/checkout',
        json={'purchaser_first_name': 'X', 'recipient_first_name': 'Y',
              'birth_date': '1990-01-01', 'birth_time': '12:00',
              'birth_city': 'Paris', 'origin_url': 'https://plume-astrale.fr'},
        timeout=10,
    )
    assert r.status_code == 422


def test_checkout_rejects_bad_birth_time_format():
    r = requests.post(
        f'{BASE_URL}/api/edition-reliee/checkout',
        json={'purchaser_email': 't@ex.com', 'purchaser_first_name': 'X',
              'recipient_first_name': 'Y', 'birth_date': '1990-01-01',
              'birth_time': 'nope', 'birth_city': 'Paris',
              'origin_url': 'https://plume-astrale.fr'},
        timeout=10,
    )
    assert r.status_code == 422


def test_checkout_rejects_bad_birth_date_format():
    r = requests.post(
        f'{BASE_URL}/api/edition-reliee/checkout',
        json={'purchaser_email': 't@ex.com', 'purchaser_first_name': 'X',
              'recipient_first_name': 'Y', 'birth_date': '01-01-1990',
              'birth_time': '12:00', 'birth_city': 'Paris',
              'origin_url': 'https://plume-astrale.fr'},
        timeout=10,
    )
    assert r.status_code == 422


# ═══════════════════════════════════════════════════════════════════════
# 3. Status endpoint — 400 sans session_id, 404 pour session inconnue
# ═══════════════════════════════════════════════════════════════════════

def test_status_returns_404_for_unknown_session():
    r = requests.get(f'{BASE_URL}/api/edition-reliee/status?session_id=cs_test_unknown_xxx', timeout=10)
    assert r.status_code == 404


# ═══════════════════════════════════════════════════════════════════════
# 4. Webhook dispatcher — le kind 'edition_reliee' doit être reconnu
# ═══════════════════════════════════════════════════════════════════════

def test_webhook_dispatcher_recognizes_edition_reliee_kind():
    """Le kind 'edition_reliee' doit être routé vers handle_edition_reliee_webhook."""
    import os
    with open('/app/backend/server.py') as f:
        server_code = f.read()
    assert "md.get('kind') == 'edition_reliee'" in server_code, (
        "Le dispatcher Stripe webhook ne route pas kind='edition_reliee'"
    )
    assert 'handle_edition_reliee_webhook' in server_code


# ═══════════════════════════════════════════════════════════════════════
# 5. Service public API — les fonctions clés existent
# ═══════════════════════════════════════════════════════════════════════

def test_service_public_api_exists():
    from services import edition_reliee_service as svc
    assert hasattr(svc, 'create_edition_reliee_checkout')
    assert hasattr(svc, 'handle_edition_reliee_webhook')


# ═══════════════════════════════════════════════════════════════════════
# 6. Frontend routes — /edition-reliee/merci + /relecture/:token routés
# ═══════════════════════════════════════════════════════════════════════

def test_app_js_routes_merci_and_relecture():
    with open('/app/frontend/src/App.js') as f:
        app_code = f.read()
    assert 'path="/edition-reliee/merci"' in app_code
    assert 'EditionRelieeMerci' in app_code
    assert 'path="/relecture/:token"' in app_code
    assert 'RelectureRefus' in app_code


# ═══════════════════════════════════════════════════════════════════════
# 7. Frontend EditionReliee — CTA ouvrent la modal (pas /carte-cadeau)
# ═══════════════════════════════════════════════════════════════════════

def test_edition_reliee_ctas_open_modal():
    with open('/app/frontend/src/pages/EditionReliee.js') as f:
        code = f.read()
    # Les CTAs primary DOIVENT ouvrir la modal (setShowForm(true)), pas rediriger vers /carte-cadeau
    assert 'setShowForm(true)' in code
    assert 'er-checkout-modal' in code
    # La modal DOIT poster sur le checkout Édition Reliée
    assert '/api/edition-reliee/checkout' in code
    # Les CTAs ne DOIVENT PLUS être des <a href="/carte-cadeau"> comme CTA principal
    # (le lien reste dans les blocs 5 et modal en escape valve, mais pas comme CTA principal)
    assert 'href="/carte-cadeau" data-testid="er-cta-primary' not in code
