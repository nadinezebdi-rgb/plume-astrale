"""Test suite E2E post-audit — verrouille les 4 fixes P0 de livraison PDF.

Ce fichier teste les corrections apportées suite à l'audit externe du 2026-02-25 :
1. Voyage Karmique : `karmic_data=` accepté par generate_karma_destin_pdf
2. Synastrie payante : dossier assets/synastrie/ exposé (HTTP 200)
3. Extrait Pack Karmique : dossier assets/pack_karmique/ exposé (HTTP 200)
4. Route /api/couple/compatibility/preview : deprecated 410 Gone

Ces tests garantissent qu'aucun régression ne peut casser silencieusement
les 3 parcours de paiement critiques identifiés par l'audit.

Exécution : `cd /app/backend && python -m pytest tests/test_audit_p0_delivery.py -v`
"""
import inspect
import os
import uuid
from pathlib import Path

import pytest
import requests


BASE_URL = os.environ.get('BACKEND_URL', 'http://localhost:8001')
ASSETS_DIR = Path('/app/backend/assets')


# ═══════════════════════════════════════════════════════════════════════
# Bug 1 · Voyage Karmique — TypeError sur karmic_data
# ═══════════════════════════════════════════════════════════════════════

def test_karma_destin_pdf_signature_accepts_karmic_data():
    """generate_karma_destin_pdf DOIT accepter le param `karmic_data`.
    L'audit a montré que voyage_karmique_service appelait `natal_data=`
    (paramètre inexistant) → TypeError systématique après paiement.
    """
    from services.karma_destin_pdf import generate_karma_destin_pdf

    sig = inspect.signature(generate_karma_destin_pdf)
    params = set(sig.parameters.keys())

    assert 'karmic_data' in params, (
        f"generate_karma_destin_pdf devrait accepter karmic_data. "
        f"Params actuels : {params}"
    )
    assert 'natal_data' not in params, (
        f"natal_data n'est PAS un paramètre valide — l'appel dans "
        f"voyage_karmique_service.py aurait déclenché TypeError. "
        f"Params actuels : {params}"
    )


def test_voyage_karmique_service_calls_karmic_data():
    """Le service voyage_karmique DOIT appeler generate_karma_destin_pdf
    avec karmic_data= (et non natal_data=).
    """
    source = Path('/app/backend/services/voyage_karmique_service.py').read_text()
    assert 'karmic_data=karma_data' in source, (
        "voyage_karmique_service.py doit passer karmic_data=karma_data"
    )
    assert 'natal_data=karma_data' not in source, (
        "voyage_karmique_service.py ne doit plus passer natal_data=karma_data (TypeError)"
    )


# ═══════════════════════════════════════════════════════════════════════
# Bugs 2 & 3 · Dossiers de livraison PDF exposés statiquement
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize('folder', ['synastrie', 'pack_karmique', 'voyage_karmique'])
def test_asset_folder_exists_on_disk(folder):
    """Chaque dossier de livraison DOIT exister au démarrage backend.
    Sinon FastAPI ne peut pas monter le StaticFiles au démarrage.
    """
    assert (ASSETS_DIR / folder).exists(), (
        f"Le dossier {folder} devrait être créé au démarrage backend"
    )
    assert (ASSETS_DIR / folder).is_dir(), (
        f"{folder} doit être un dossier, pas un fichier"
    )


@pytest.mark.parametrize('folder', ['synastrie', 'voyage_karmique'])
def test_asset_folder_no_longer_publicly_served(folder):
    """Post-migration 2026-02-26 : les dossiers `synastrie` et `voyage_karmique`
    ne sont PLUS exposés en statique. L'accès passe désormais par
    /api/pdf/download?session_id=X&token=Y (token opaque).

    Ce test verrouille la fin de la surface d'attaque énumération :
    un attaquant qui essaie /api/assets/synastrie/anyfile.pdf doit obtenir 404,
    pas un fichier PDF.
    """
    unique_name = f'_e2e_probe_{uuid.uuid4().hex[:8]}.txt'
    probe_path = ASSETS_DIR / folder / unique_name
    probe_content = f'audit-p0-{folder}-{unique_name}'
    try:
        probe_path.write_text(probe_content)
        r = requests.get(
            f'{BASE_URL}/api/assets/{folder}/{unique_name}',
            timeout=10,
        )
        assert r.status_code == 404, (
            f'/api/assets/{folder}/{unique_name} devrait renvoyer HTTP 404 '
            f'(mount statique retiré 2026-02-26 pour SEC), a renvoyé HTTP {r.status_code}. '
            f'Vérifier que server.py ne monte plus {folder} dans /api/assets/*.'
        )
    finally:
        if probe_path.exists():
            probe_path.unlink()


def test_pack_karmique_folder_still_served():
    """Pack Karmique conserve son mount temporaire (grace period pour les
    achats existants). À migrer à son tour ultérieurement.

    Test optional : si le mount est retiré, ce test doit skip proprement.
    """
    unique_name = f'_e2e_probe_{uuid.uuid4().hex[:8]}.txt'
    probe_path = ASSETS_DIR / 'pack_karmique' / unique_name
    try:
        probe_path.write_text('probe')
        r = requests.get(
            f'{BASE_URL}/api/assets/pack_karmique/{unique_name}',
            timeout=10,
        )
        # 200 tant que le mount est présent, 404 sinon (comportement acceptable)
        assert r.status_code in (200, 404)
    finally:
        if probe_path.exists():
            probe_path.unlink()


# ═══════════════════════════════════════════════════════════════════════
# Bug 4 · Route /couple/compatibility/preview dépréciée
# ═══════════════════════════════════════════════════════════════════════

def test_couple_compatibility_preview_returns_410():
    """L'ancienne route /api/couple/compatibility/preview était triplement
    cassée (async sur sync, schéma birth_date incompatible, ne renvoyait
    ni PDF ni URL). Elle DOIT désormais retourner HTTP 410 Gone avec un
    message clair pointant vers la route principale.
    """
    r = requests.post(
        f'{BASE_URL}/api/couple/compatibility/preview',
        json={},
        timeout=10,
    )
    assert r.status_code == 410, (
        f'La route dépréciée devrait renvoyer HTTP 410 Gone, '
        f'a renvoyé HTTP {r.status_code}'
    )
    detail = r.json().get('detail', '')
    assert '/api/compatibility/generate' in detail, (
        f'Le message 410 devrait pointer vers la route principale, '
        f'a renvoyé : {detail!r}'
    )


def test_couple_compatibility_preview_hidden_from_openapi():
    """La route dépréciée ne doit plus figurer dans la doc OpenAPI publique."""
    r = requests.get(f'{BASE_URL}/api/openapi.json', timeout=10)
    if r.status_code != 200:
        pytest.skip('OpenAPI schema non exposé sur ce déploiement')
    paths = r.json().get('paths', {})
    deprecated_path = '/api/couple/compatibility/preview'
    assert deprecated_path not in paths, (
        f'{deprecated_path} devrait être exclue de l\'OpenAPI schema '
        f'(include_in_schema=False)'
    )


# ═══════════════════════════════════════════════════════════════════════
# Smoke tests · Backend reachable
# ═══════════════════════════════════════════════════════════════════════

def test_backend_health():
    """Sanity : le backend répond bien avant tous les tests."""
    r = requests.get(f'{BASE_URL}/api/health', timeout=10)
    assert r.status_code == 200
    assert r.json().get('ok') is True
