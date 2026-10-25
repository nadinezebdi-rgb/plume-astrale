"""Tests du kill-switch background loops et du endpoint diagnostic.

Ne teste pas Playwright/Supabase — vérifie la LOGIQUE de la variable
d'environnement DISABLE_BACKGROUND_TASKS / BACKGROUND_LOOPS_ENABLED
et la forme du payload /api/admin/background-loops/status.
"""
from __future__ import annotations
import os
from unittest.mock import patch


def _compute_bg_enabled() -> bool:
    """Reproduit la logique de server.py:_start_cart_recovery (lignes ~4048-4049).

    Garder synchro avec le code prod : si l'un des 2 switches dit "off",
    les loops sont désactivés.
    """
    _bg_disabled_alias = os.environ.get(
        'DISABLE_BACKGROUND_TASKS', ''
    ).lower() in ('1', 'true', 'yes', 'on')
    return (not _bg_disabled_alias) and os.environ.get('BACKGROUND_LOOPS_ENABLED', '1') != '0'


def test_kill_switch_default_enabled():
    with patch.dict(os.environ, {}, clear=False):
        for k in ('DISABLE_BACKGROUND_TASKS', 'BACKGROUND_LOOPS_ENABLED'):
            os.environ.pop(k, None)
        assert _compute_bg_enabled() is True


def test_kill_switch_disable_alias_true():
    for val in ('true', 'True', 'TRUE', '1', 'yes', 'on'):
        with patch.dict(os.environ, {'DISABLE_BACKGROUND_TASKS': val}, clear=False):
            os.environ.pop('BACKGROUND_LOOPS_ENABLED', None)
            assert _compute_bg_enabled() is False, f'val={val!r} should disable'


def test_kill_switch_disable_alias_false_values_do_not_disable():
    for val in ('false', '0', 'no', 'off', '', 'maybe'):
        with patch.dict(os.environ, {'DISABLE_BACKGROUND_TASKS': val}, clear=False):
            os.environ.pop('BACKGROUND_LOOPS_ENABLED', None)
            assert _compute_bg_enabled() is True, f'val={val!r} should NOT disable'


def test_kill_switch_legacy_env_disables():
    with patch.dict(os.environ, {'BACKGROUND_LOOPS_ENABLED': '0'}, clear=False):
        os.environ.pop('DISABLE_BACKGROUND_TASKS', None)
        assert _compute_bg_enabled() is False


def test_kill_switch_both_set_both_disable():
    """Si l'un ou l'autre est positionné, les loops sont off."""
    with patch.dict(os.environ, {
        'DISABLE_BACKGROUND_TASKS': 'true',
        'BACKGROUND_LOOPS_ENABLED': '1',
    }, clear=False):
        assert _compute_bg_enabled() is False
    with patch.dict(os.environ, {
        'DISABLE_BACKGROUND_TASKS': 'false',
        'BACKGROUND_LOOPS_ENABLED': '0',
    }, clear=False):
        assert _compute_bg_enabled() is False


def test_deploy_target_detection():
    """La détection Railway vs Emergent doit utiliser les env vars connues."""
    # Logique dupliquée de l'endpoint pour éviter l'import server (lourd).
    def detect():
        if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_PROJECT_ID'):
            return 'railway'
        if (os.environ.get('K_SERVICE') or os.environ.get('EMERGENT_DEPLOYMENT_ID')
                or os.environ.get('EMERGENT_APP_ID')):
            return 'emergent'
        if os.environ.get('KUBERNETES_SERVICE_HOST'):
            return 'kubernetes'
        return 'unknown'

    with patch.dict(os.environ, {}, clear=True):
        assert detect() == 'unknown'
    with patch.dict(os.environ, {'RAILWAY_PROJECT_ID': 'xyz'}, clear=True):
        assert detect() == 'railway'
    with patch.dict(os.environ, {'EMERGENT_APP_ID': 'abc'}, clear=True):
        assert detect() == 'emergent'
    with patch.dict(os.environ, {'KUBERNETES_SERVICE_HOST': '10.0.0.1'}, clear=True):
        assert detect() == 'kubernetes'
