"""Promo d'inscription : crédits offerts aux comptes créés pendant la période.

Le solde initial (20 crédits) est posé par le trigger Supabase. Ce module ajoute
le bonus promo une seule fois par compte, au premier accès au solde.

Réglages (variables d'environnement du backend) :
  SIGNUP_PROMO_ENABLED=false   coupe la promo
  SIGNUP_PROMO_CREDITS=100     crédits offerts
  SIGNUP_PROMO_START=...       début (ISO 8601), défaut 2026-10-03 00:00 Paris
  SIGNUP_PROMO_UNTIL=...       fin (ISO 8601), défaut lundi 2026-10-05 23:59 Paris
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

MARKER = 'Promo inscription'
_checked: set[str] = set()


def _parse(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _window() -> tuple[datetime, datetime]:
    start = _parse(os.environ.get('SIGNUP_PROMO_START') or '2026-10-03T00:00:00+02:00')
    until = _parse(os.environ.get('SIGNUP_PROMO_UNTIL') or '2026-10-05T23:59:59+02:00')
    return start, until


def is_active(now: datetime | None = None) -> bool:
    if os.environ.get('SIGNUP_PROMO_ENABLED', 'true').strip().lower() in ('0', 'false', 'no', 'off'):
        return False
    start, until = _window()
    return start <= (now or datetime.now(timezone.utc)) <= until


def credits_amount() -> int:
    try:
        return max(0, int(os.environ.get('SIGNUP_PROMO_CREDITS', '100')))
    except ValueError:
        return 100


def grant_if_eligible(sb, user_id: str, balance: int) -> int:
    """Crédite le bonus si le compte a été créé dans la fenêtre. Renvoie le montant ajouté."""
    if user_id in _checked or not is_active():
        return 0
    amount = credits_amount()
    if amount <= 0:
        return 0
    try:
        prof = sb.table('profiles').select('created_at').eq('id', user_id).maybe_single().execute()
        created = (prof.data or {}).get('created_at') if prof else None
        if not created:
            return 0
        created_dt = _parse(str(created).replace('Z', '+00:00'))
        start, until = _window()
        if not (start <= created_dt <= until):
            _checked.add(user_id)
            return 0
        done = (sb.table('credit_transactions').select('id').eq('user_id', user_id)
                .eq('description', MARKER).limit(1).execute())
        if done and done.data:
            _checked.add(user_id)
            return 0
        _checked.add(user_id)
        sb.table('wallets').update({'credit_balance': balance + amount}).eq('user_id', user_id).execute()
        sb.table('credit_transactions').insert({
            'user_id': user_id, 'tx_type': 'promo', 'amount': amount, 'description': MARKER,
        }).execute()
        return amount
    except Exception as e:
        logger.warning(f'[signup_promo] grant failed for {user_id}: {e}')
        _checked.discard(user_id)
        return 0
