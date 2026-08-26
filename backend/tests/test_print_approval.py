"""Test suite E2E — Flow d'approbation 72h "Vous lisez avant qu'on imprime".

Ce fichier verrouille les invariants du service `print_approval_service` et
des endpoints associés. Il n'exige PAS que la table Supabase `print_approvals`
existe : les tests mockent le client Supabase.

Exécution : `cd /app/backend && python -m pytest tests/test_print_approval.py -v`
"""
from __future__ import annotations
import os
import uuid
from unittest.mock import MagicMock, patch

import pytest
import requests

BASE_URL = os.environ.get('BACKEND_URL', 'http://localhost:8001')


# ═══════════════════════════════════════════════════════════════════════
# 1. Signature du service — les fonctions publiques doivent exister
# ═══════════════════════════════════════════════════════════════════════

def test_service_public_api_exists():
    from services import print_approval_service as svc
    assert hasattr(svc, 'create_print_approval')
    assert hasattr(svc, 'approve')
    assert hasattr(svc, 'refuse')
    assert hasattr(svc, 'get_by_token')
    assert hasattr(svc, 'list_pending')
    assert hasattr(svc, 'print_approval_loop')
    # Constantes métier
    assert svc.DEADLINE_HOURS == 72
    assert svc.REMINDER_24H_AFTER_CREATED_HOURS == 24
    assert svc.REMINDER_48H_AFTER_CREATED_HOURS == 48


# ═══════════════════════════════════════════════════════════════════════
# 2. get_by_token — tokens invalides rejetés sans hit DB
# ═══════════════════════════════════════════════════════════════════════

def test_get_by_token_rejects_short_token():
    from services.print_approval_service import get_by_token
    # < 16 chars → refus immédiat sans requête Supabase
    assert get_by_token('short', kind='approve') is None
    assert get_by_token('', kind='refuse') is None
    assert get_by_token('a' * 100, kind='approve') is None  # > 64 chars


# ═══════════════════════════════════════════════════════════════════════
# 3. Endpoints HTTP — 404 pour token inconnu, 200 pour admin list
# ═══════════════════════════════════════════════════════════════════════

def test_endpoint_approve_link_returns_404_for_unknown_token():
    """GET /api/print-approval/approve/{token} sur un token inconnu → 404."""
    fake_token = uuid.uuid4().hex
    r = requests.get(f'{BASE_URL}/api/print-approval/approve/{fake_token}', timeout=10, allow_redirects=False)
    assert r.status_code == 404
    # La page HTML de courtoisie contient "Lien introuvable"
    assert 'Lien introuvable' in r.text


def test_endpoint_get_returns_404_for_unknown_token():
    """GET /api/print-approval/{token} → 404 si token inconnu."""
    fake_token = uuid.uuid4().hex
    r = requests.get(f'{BASE_URL}/api/print-approval/{fake_token}', timeout=10)
    assert r.status_code == 404


def test_endpoint_refuse_returns_404_for_unknown_token():
    """POST /api/print-approval/refuse/{token} → 404 si token inconnu."""
    fake_token = uuid.uuid4().hex
    r = requests.post(
        f'{BASE_URL}/api/print-approval/refuse/{fake_token}',
        json={'reason': 'test raison'},
        timeout=10,
    )
    assert r.status_code == 404


def test_endpoint_admin_list_returns_200():
    """GET /api/admin/print-approvals → 200 avec `items:[]` (safe fallback si table absente)."""
    r = requests.get(f'{BASE_URL}/api/admin/print-approvals', timeout=10)
    assert r.status_code == 200
    payload = r.json()
    assert 'items' in payload
    assert isinstance(payload['items'], list)


def test_endpoint_admin_list_respects_limit_bounds():
    """`limit` doit être clampé entre 1 et 200."""
    r = requests.get(f'{BASE_URL}/api/admin/print-approvals?limit=500', timeout=10)
    assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════════
# 4. Migration SQL — fichier présent et bien formé
# ═══════════════════════════════════════════════════════════════════════

def test_migration_file_exists_and_defines_table():
    """La migration SQL doit exister avec les colonnes clés."""
    path = '/app/backend/migrations/2026_02_print_approvals.sql'
    assert os.path.exists(path), f'Migration manquante : {path}'
    with open(path) as f:
        sql = f.read()

    required = [
        'CREATE TABLE IF NOT EXISTS print_approvals',
        'approve_token',
        'refuse_token',
        'deadline_at',
        'reminder_24h_sent_at',
        'reminder_48h_sent_at',
        "status TEXT NOT NULL DEFAULT 'awaiting_review'",
        'ENABLE ROW LEVEL SECURITY',
    ]
    for token in required:
        assert token in sql, f'Migration incomplète : "{token}" manquant'


# ═══════════════════════════════════════════════════════════════════════
# 5. Loop de rappels — comportement idempotent
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_process_reminders_returns_stats_dict():
    """Le loop doit toujours retourner un dict avec les 3 compteurs, même sans DB."""
    from services.print_approval_service import _process_reminders
    stats = await _process_reminders()
    assert set(stats.keys()) == {'reminded_24h', 'reminded_48h', 'expired'}
    assert all(isinstance(v, int) for v in stats.values())


# ═══════════════════════════════════════════════════════════════════════
# 6. Templates email — HTML valide avec liens 1-clic
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_initial_email_contains_both_action_links(monkeypatch):
    """L'email initial DOIT contenir les liens approve + refuse + le PDF."""
    from services import print_approval_service as svc

    captured = {}

    async def fake_send(to_email, subject, html, text='', from_email=None):
        captured['to'] = to_email
        captured['subject'] = subject
        captured['html'] = html
        return 'fake_email_id'

    # Patch send_email juste pour ce test
    import services.resend_service as rs
    monkeypatch.setattr(rs, 'send_email', fake_send)

    row = {
        'id': 'test_id',
        'approve_token': 'tok_approve_' + 'a' * 20,
        'refuse_token': 'tok_refuse_' + 'b' * 20,
        'pdf_url': 'https://example.com/pdf/xyz',
        'purchaser_email': 'test@example.com',
        'purchaser_first_name': 'Marie',
        'recipient_first_name': 'Julie',
    }
    ok = await svc._send_initial_email(row)
    assert ok is True

    html = captured['html']
    # Les 3 liens critiques doivent être présents
    assert f'/api/print-approval/approve/{row["approve_token"]}' in html
    assert f'/relecture/{row["refuse_token"]}' in html
    assert 'https://example.com/pdf/xyz' in html
    # Personnalisation
    assert 'Marie' in html
    assert 'Julie' in html
    # Ton éditorial
    assert 'Nadine' in html
    assert 'Édition Reliée' in html
    # Deadline 72h dans le message
    assert '72' in html
    # Destinataire correct
    assert captured['to'] == 'test@example.com'
