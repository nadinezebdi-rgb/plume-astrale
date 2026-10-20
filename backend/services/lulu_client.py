"""lulu_client — Client Lulu Print API (mode mock + réel)
================================================================================

LULU_MOCK=1 → tous les appels retournent des réponses simulées déterministes.
LULU_MOCK=0 (default production) → vraie API OAuth2 Lulu.

Playbook : integration_playbook_expert_v2 (Lulu Print API Getting Started).

ENV requis en mode réel :
  LULU_BASE_URL           — https://api.sandbox.lulu.com ou https://api.lulu.com
  LULU_TOKEN_URL          — endpoint OpenID client_credentials
  LULU_CLIENT_KEY         — API key
  LULU_CLIENT_SECRET      — API secret
  LULU_WEBHOOK_SECRET     — secret HMAC-SHA256 pour vérifier les webhooks
  LULU_POD_PACKAGE_ID     — SKU A5 hardcover (ex: 0583X0827FCPRECW060UW444MXX)

En mode mock, aucune ENV n'est requise.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import logging
import os
import time
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


def is_mock() -> bool:
    return os.environ.get('LULU_MOCK', '0') == '1'


# Prix de référence mock (en EUR TTC, livraison + impression + marge).
# Base utilisée pour le quote si l'API n'est pas branchée.
_MOCK_SHIPPING_EUR = {
    'FR': 8.5, 'BE': 10.0, 'CH': 12.0, 'LU': 10.0, 'MC': 9.0,
    'DE': 12.0, 'IT': 12.0, 'ES': 12.0, 'PT': 13.0, 'NL': 11.0, 'GB': 15.0,
    'US': 22.0, 'CA': 25.0,
}
_MOCK_PRINT_COST_EUR = 18.5   # coût impression Lulu A5 hardcover 42 pages
_DEFAULT_SHIPPING_EUR = 18.0  # pour pays non listés


def mock_quote(address: Dict[str, Any], page_count: int = 42) -> Dict[str, Any]:
    """Retourne un devis mocké déterministe."""
    country = (address.get('country_code') or 'FR').upper()
    shipping = _MOCK_SHIPPING_EUR.get(country, _DEFAULT_SHIPPING_EUR)
    print_cost = _MOCK_PRINT_COST_EUR + (page_count - 42) * 0.08
    total_cost = round(shipping + print_cost, 2)
    return {
        'currency': 'EUR',
        'total_cost_incl_tax': total_cost,
        'print_cost': round(print_cost, 2),
        'shipping_cost': shipping,
        'estimated_shipping_days': 7 if country in ('FR', 'BE', 'MC', 'LU') else 14,
        'mock': True,
    }


# ─── Token management (prod only) ────────────────────────────────────
_token_cache: Dict[str, Any] = {'value': None, 'expires': 0}


async def _get_token() -> str:
    if _token_cache['value'] and time.time() < _token_cache['expires'] - 60:
        return _token_cache['value']
    key = os.environ.get('LULU_CLIENT_KEY', '')
    secret = os.environ.get('LULU_CLIENT_SECRET', '')
    token_url = os.environ.get('LULU_TOKEN_URL', '')
    if not (key and secret and token_url):
        raise RuntimeError('LULU_CLIENT_KEY/SECRET/TOKEN_URL manquants')
    basic = base64.b64encode(f'{key}:{secret}'.encode()).decode()
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            token_url,
            data={'grant_type': 'client_credentials'},
            headers={'Authorization': f'Basic {basic}',
                     'Content-Type': 'application/x-www-form-urlencoded'},
        )
        r.raise_for_status()
        d = r.json()
    _token_cache.update(value=d['access_token'], expires=time.time() + d.get('expires_in', 300))
    return _token_cache['value']


async def quote_print_job(address: Dict[str, Any], page_count: int = 42) -> Dict[str, Any]:
    """Devis d'impression + livraison. Mock ou vrai selon LULU_MOCK."""
    if is_mock():
        logger.info(f'[lulu_mock] quote country={address.get("country_code")} → mocked')
        return mock_quote(address, page_count)

    base = os.environ.get('LULU_BASE_URL', '').rstrip('/')
    pod = os.environ.get('LULU_POD_PACKAGE_ID', '')
    if not (base and pod):
        raise RuntimeError('LULU_BASE_URL ou LULU_POD_PACKAGE_ID manquant')
    token = await _get_token()
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            f'{base}/print-job-cost-calculations/',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json={
                'line_items': [{'page_count': page_count, 'pod_package_id': pod, 'quantity': 1}],
                'shipping_address': address,
                'shipping_option': 'PRIORITY_MAIL',
            },
        )
        r.raise_for_status()
        return r.json()


async def create_print_job(
    *, external_id: str, address: Dict[str, Any],
    interior_url: str, cover_url: str,
    contact_email: str = 'contact@plume-astrale.fr',
) -> Dict[str, Any]:
    """Crée un print job Lulu. Mock retourne un faux ID + status IN_PRODUCTION."""
    if is_mock():
        logger.info(f'[lulu_mock] create_print_job external_id={external_id}')
        return {
            'id': int(time.time()),
            'external_id': external_id,
            'status': {'name': 'IN_PRODUCTION', 'message': 'Mock — simulated job'},
            'line_items': [{
                'external_id': f'{external_id}-item',
                'tracking_urls': [],
            }],
            'mock': True,
        }

    base = os.environ.get('LULU_BASE_URL', '').rstrip('/')
    pod = os.environ.get('LULU_POD_PACKAGE_ID', '')
    token = await _get_token()
    payload = {
        'external_id': external_id,
        'contact_email': contact_email,
        'shipping_level': 'PRIORITY_MAIL',
        'shipping_address': address,
        'line_items': [{
            'quantity': 1,
            'pod_package_id': pod,
            'interior': {'source_url': interior_url},
            'cover': {'source_url': cover_url},
        }],
    }
    async with httpx.AsyncClient(timeout=90) as c:
        r = await c.post(
            f'{base}/print-jobs/',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json=payload,
        )
        r.raise_for_status()
        return r.json()


def verify_webhook_signature(raw_body: bytes, hmac_header: Optional[str]) -> bool:
    """Vérifie la signature HMAC-SHA256 d'un webhook Lulu."""
    if is_mock():
        return True  # les webhooks mock ne sont pas signés
    secret = os.environ.get('LULU_WEBHOOK_SECRET', '')
    if not secret:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    supplied = (hmac_header or '').removeprefix('sha256=').strip()
    return hmac.compare_digest(expected, supplied)


__all__ = ['is_mock', 'mock_quote', 'quote_print_job', 'create_print_job',
            'verify_webhook_signature']


async def cover_dimensions(page_count: int) -> Dict[str, Any]:
    """Use Lulu's selected binding and actual interior count, never an estimated spine."""
    if is_mock():
        raise RuntimeError('Les dimensions de couverture exigent Lulu réel ou son gabarit exact')
    base = os.environ.get('LULU_BASE_URL', '').rstrip('/')
    pod = os.environ.get('LULU_POD_PACKAGE_ID', '')
    if not base or not pod:
        raise RuntimeError('Configuration Lulu manquante')
    token = await _get_token()
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(f'{base}/cover-dimensions/',
            headers={'Authorization': f'Bearer {token}'},
            json={'pod_package_id': pod, 'interior_page_count': page_count, 'unit': 'mm'})
        response.raise_for_status()
        return response.json()


async def validate_print_files(interior_url: str, cover_url: str, page_count: int):
    """Lulu preflight only; this does not place or charge an order."""
    import asyncio
    if is_mock():
        raise RuntimeError('Validation réelle Lulu requise avant impression')
    base = os.environ.get('LULU_BASE_URL', '').rstrip('/')
    pod = os.environ.get('LULU_POD_PACKAGE_ID', '')
    token = await _get_token()
    async with httpx.AsyncClient(timeout=45, headers={'Authorization': f'Bearer {token}'}) as client:
        for kind, url, accepted in [('interior', interior_url, 'VALIDATED'), ('cover', cover_url, 'NORMALIZED')]:
            payload = {'source_url': url, 'pod_package_id': pod}
            if kind == 'cover':
                payload['interior_page_count'] = page_count
            response = await client.post(f'{base}/validate-{kind}/', json=payload)
            response.raise_for_status()
            result = response.json()
            for attempt in range(25):
                if result.get('status') == accepted:
                    break
                if result.get('status') == 'ERROR':
                    raise RuntimeError(f'Lulu {kind}: {result.get("errors")}')
                await asyncio.sleep(2)
                response = await client.get(f'{base}/validate-{kind}/{result["id"]}/')
                response.raise_for_status()
                result = response.json()
            else:
                raise RuntimeError(f'Validation Lulu {kind} toujours en cours; réessayer avant commande')
            if kind == 'interior' and int(result.get('page_count') or page_count) != page_count:
                raise RuntimeError('Nombre de pages Lulu incohérent')
