"""Meta Conversions API (CAPI) — tracking server-side des conversions.

Complète le pixel client-side : envoie les événements directement depuis
FastAPI vers Meta, ce qui permet de continuer à mesurer les conversions
même quand les navigateurs bloquent le pixel (Safari ITP, bloqueurs ~20% du trafic).

REQUIS (.env backend) :
    META_PIXEL_ID=1801418127692821
    META_CAPI_ACCESS_TOKEN=EAAxxxxxxxxxx...   # System User Token, généré dans
                                              # Meta Business > Paramètres > Utilisateurs Système
    META_CAPI_TEST_CODE=TEST12345            # optionnel — pour Test Events console

Deduplication : les events envoyés depuis le pixel client-side ET la CAPI
doivent partager le même event_id → Meta les dédup automatiquement. Le client
envoie déjà un event_id via `analytics.js` — le serveur doit utiliser le même.

Reference : https://developers.facebook.com/docs/marketing-api/conversions-api
"""
from __future__ import annotations
import hashlib
import logging
import os
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

META_PIXEL_ID = os.environ.get('META_PIXEL_ID', '1801418127692821')
META_CAPI_ACCESS_TOKEN = os.environ.get('META_CAPI_ACCESS_TOKEN')
META_CAPI_TEST_CODE = os.environ.get('META_CAPI_TEST_CODE')  # optionnel


def _sha256(v: Optional[str]) -> Optional[str]:
    """Meta exige les PII hashées en SHA-256 (email, phone, first_name, etc.)."""
    if not v:
        return None
    return hashlib.sha256(v.strip().lower().encode('utf-8')).hexdigest()


def extract_client_signals(request) -> dict:
    """Signaux de matching Meta extraits de la requête FastAPI.

    Derrière Vercel/Railway, `request.client.host` est l'IP du proxy — on
    prend le premier hop de X-Forwarded-For (IP réelle du visiteur).
    """
    ua = request.headers.get('user-agent') or None
    forwarded = request.headers.get('x-forwarded-for', '')
    if forwarded:
        ip = forwarded.split(',')[0].strip() or None
    else:
        ip = request.client.host if request.client else None
    return {'client_ip': ip, 'client_user_agent': ua}


async def send_capi_event(
    event_name: str,
    event_id: str | None = None,
    user_email: str | None = None,
    user_phone: str | None = None,
    user_first_name: str | None = None,
    client_ip: str | None = None,
    client_user_agent: str | None = None,
    fbc: str | None = None,   # cookie _fbc (Facebook Click ID)
    fbp: str | None = None,   # cookie _fbp (Facebook Browser ID)
    event_source_url: str | None = None,
    value: float | None = None,
    currency: str = 'EUR',
    **custom_data,
) -> bool:
    """Envoie un événement à Meta Conversions API. Renvoie True si OK.

    event_name : Meta standard event (Purchase, Lead, InitiateCheckout, Subscribe, ...)
                 OU custom event.
    event_id : IDEMPOTENT — doit matcher l'event_id envoyé par le pixel client
               (via `eventID` dans fbq('track', ...)) pour dédupication.
    """
    if not META_CAPI_ACCESS_TOKEN:
        logger.debug('[meta_capi] META_CAPI_ACCESS_TOKEN absent — event non envoyé')
        return False

    user_data = {}
    if user_email:
        user_data['em'] = [_sha256(user_email)]
    if user_phone:
        user_data['ph'] = [_sha256(user_phone)]
    if user_first_name:
        user_data['fn'] = [_sha256(user_first_name)]
    if client_ip:
        user_data['client_ip_address'] = client_ip
    if client_user_agent:
        user_data['client_user_agent'] = client_user_agent
    if fbc:
        user_data['fbc'] = fbc
    if fbp:
        user_data['fbp'] = fbp

    custom = dict(custom_data)
    if value is not None:
        custom['value'] = float(value)
        custom['currency'] = currency

    event = {
        'event_name': event_name,
        'event_time': int(time.time()),
        'action_source': 'website',
        'user_data': user_data,
        'custom_data': custom,
    }
    if event_id:
        event['event_id'] = event_id
    if event_source_url:
        event['event_source_url'] = event_source_url

    payload = {'data': [event]}
    if META_CAPI_TEST_CODE:
        payload['test_event_code'] = META_CAPI_TEST_CODE

    url = f'https://graph.facebook.com/v20.0/{META_PIXEL_ID}/events'
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                url,
                params={'access_token': META_CAPI_ACCESS_TOKEN},
                json=payload,
            )
            if r.status_code >= 400:
                logger.warning(f'[meta_capi] {event_name} failed {r.status_code}: {r.text[:300]}')
                return False
            data = r.json()
            events_received = data.get('events_received', 0)
            if events_received == 0:
                logger.warning(f'[meta_capi] {event_name} accepté mais 0 event_received : {data}')
                return False
            logger.info(f'[meta_capi] ✓ {event_name} envoyé (events_received={events_received})')
            return True
    except Exception as e:
        logger.error(f'[meta_capi] {event_name} exception: {e}')
        return False
