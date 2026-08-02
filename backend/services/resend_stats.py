"""
Resend API helper : recupere les stats email (opens, clicks) pour l'A/B test.

Utilise l'endpoint GET https://api.resend.com/emails/{id}.
"""
from __future__ import annotations
import logging
import os
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
RESEND_BASE = 'https://api.resend.com'


async def fetch_email_stats(email_id: str, client: Optional[httpx.AsyncClient] = None) -> Optional[Dict[str, Any]]:
    """Retourne {opened_at?, clicked_at?, last_event, delivered_at?} pour un email_id Resend.

    Renvoie None si le fetch echoue.
    """
    if not email_id or not RESEND_API_KEY:
        return None
    headers = {'Authorization': f'Bearer {RESEND_API_KEY}'}
    close_after = False
    if client is None:
        client = httpx.AsyncClient(timeout=8.0)
        close_after = True
    try:
        r = await client.get(f'{RESEND_BASE}/emails/{email_id}', headers=headers)
        if r.status_code != 200:
            return None
        data = r.json()
        return {
            'id': data.get('id'),
            'delivered_at': data.get('delivered_at') or data.get('last_event_at'),
            'opened_at': data.get('opened_at'),
            'clicked_at': data.get('clicked_at'),
            'last_event': data.get('last_event'),
        }
    except Exception as e:
        logger.warning(f'[resend_stats] fetch fail for {email_id}: {e}')
        return None
    finally:
        if close_after:
            await client.aclose()


async def aggregate_ab_ctr(variant_email_ids: Dict[str, List[str]]) -> Dict[str, Any]:
    """Aggrege opens/clicks par variant.

    variant_email_ids : {'question': [eid1, eid2, ...], 'invitation': [...]}
    Retourne : {'question': {sent, opened, clicked, open_rate, ctr}, 'invitation': {...}, 'winner': 'question'|'invitation'|None}
    """
    import asyncio as _asyncio
    result: Dict[str, Any] = {}
    async with httpx.AsyncClient(timeout=8.0) as client:
        for variant, eids in variant_email_ids.items():
            eids = [e for e in (eids or []) if e]
            if not eids:
                result[variant] = {'sent': 0, 'opened': 0, 'clicked': 0, 'open_rate': 0.0, 'ctr': 0.0}
                continue
            # Fetch en parallele (cap a 50 pour ne pas saturer)
            eids_capped = eids[:50]
            stats_list = await _asyncio.gather(
                *[fetch_email_stats(eid, client=client) for eid in eids_capped],
                return_exceptions=True,
            )
            opened = sum(1 for s in stats_list if isinstance(s, dict) and s.get('opened_at'))
            clicked = sum(1 for s in stats_list if isinstance(s, dict) and s.get('clicked_at'))
            n = len(eids_capped)
            result[variant] = {
                'sent': n,
                'opened': opened,
                'clicked': clicked,
                'open_rate': round(opened / n * 100, 1) if n else 0.0,
                'ctr': round(clicked / n * 100, 1) if n else 0.0,
                'sample_note': f'Basé sur les {n} premiers emails' if len(eids) > 50 else None,
            }

    # Detecte le gagnant : CTR le plus haut avec au moins 30 envois par variant
    winner = None
    q = result.get('question', {})
    inv = result.get('invitation', {})
    if q.get('sent', 0) >= 30 and inv.get('sent', 0) >= 30:
        if q.get('ctr', 0) > inv.get('ctr', 0) + 0.5:
            winner = 'question'
        elif inv.get('ctr', 0) > q.get('ctr', 0) + 0.5:
            winner = 'invitation'
    result['winner'] = winner
    result['significant'] = winner is not None
    return result


# ═══════════════════════════════════════════════════════════════
# Cache 24h + boucle de refresh
# ═══════════════════════════════════════════════════════════════

import time as _time
_CTR_CACHE: Dict[str, Any] = {'ts': 0.0, 'data': None}
_CTR_CACHE_TTL_S = 24 * 3600  # 24h


def get_cached_ab_ctr() -> Optional[Dict[str, Any]]:
    """Retourne le CTR cache si < 24h, sinon None (cote appelant : afficher stale + trigger refresh)."""
    cached = _CTR_CACHE.get('data')
    if cached and (_time.monotonic() - _CTR_CACHE['ts']) < _CTR_CACHE_TTL_S:
        return {**cached, 'cached': True, 'cache_age_s': int(_time.monotonic() - _CTR_CACHE['ts'])}
    return None


async def _send_winner_notification(winner: str, ctr_data: Dict[str, Any]) -> None:
    """Notifie l'admin (email + Slack) que le gagnant A/B est confirme."""
    try:
        from services.supabase_client import get_admin_client
        from services.resend_service import send_email
        sb = get_admin_client()
        r = sb.table('profiles').select('email').eq('is_admin', True).execute()
        admins = [(row.get('email') or '').strip() for row in (r.data or []) if row.get('email')]
        w = ctr_data.get(winner, {})
        l = ctr_data.get('question' if winner == 'invitation' else 'invitation', {})
        subject = f'🏆 A/B J+30 : {winner} gagne (+{round(w.get("ctr",0) - l.get("ctr",0), 2)}pts CTR)'
        html = f"""
        <div style="font-family:Georgia,serif;max-width:560px;margin:0 auto;background:#0b1020;color:#e8e6f0;padding:32px 24px;">
          <div style="background:#141a33;border:1px solid #4ADE80;border-radius:12px;padding:26px;">
            <h1 style="color:#4ADE80;font-size:22px;font-weight:400;margin:0 0 12px;">
              🏆 Gagnant A/B J+30 confirme
            </h1>
            <p><strong>{winner.upper()}</strong> gagne avec un CTR de <strong>{w.get('ctr',0)}%</strong>
              contre <strong>{l.get('ctr',0)}%</strong> pour l'autre variante.</p>
            <p>Envoyes : {w.get('sent',0)} vs {l.get('sent',0)}</p>
            <p style="color:#d9b26a;">Recommandation : bascule 100% sur cette variante pour le prochain cycle.</p>
            <p style="margin-top:20px;">
              <a href="https://plume-astrale.fr/admin" style="color:#d9b26a;">Ouvrir le tableau de bord →</a>
            </p>
          </div>
        </div>
        """
        for admin in admins:
            try:
                await send_email(admin, subject, html)
            except Exception as e:
                logger.warning(f'[ctr_cache] winner email fail {admin}: {e}')
        # Slack ping si configure
        try:
            from services.refund_alert import SLACK_WEBHOOK_URL
            if SLACK_WEBHOOK_URL:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    await client.post(SLACK_WEBHOOK_URL, json={
                        'text': f'🏆 A/B J+30 : *{winner}* gagne ({w.get("ctr",0)}% CTR vs {l.get("ctr",0)}%).'
                                f' Bascule recommandee.\nhttps://plume-astrale.fr/admin',
                    })
        except Exception as e:
            logger.warning(f'[ctr_cache] winner Slack fail: {e}')
    except Exception as e:
        logger.warning(f'[ctr_cache] winner notification build fail: {e}')


async def refresh_ab_ctr_cache() -> Optional[Dict[str, Any]]:
    """Fetch toutes les tx J+30 -> aggrege CTR -> stocke dans cache.

    Envoie une notification si un nouveau gagnant est confirme (transition
    winner=None -> winner=X ou changement de gagnant).
    """
    from services.supabase_client import get_admin_client
    sb = get_admin_client()
    try:
        r = sb.table('payment_transactions').select('metadata').eq('pack_id', 'lecture_complete').execute()
    except Exception as e:
        logger.warning(f'[ctr_cache] fetch fail: {e}')
        return None
    rows = (r.data or []) if r else []
    variant_ids: Dict[str, List[str]] = {'question': [], 'invitation': []}
    total_sent = 0
    for row in rows:
        md = row.get('metadata') or {}
        if not md.get('sequence_j30_sent_at'):
            continue
        variant = md.get('sequence_j30_variant') or 'question'
        eid = md.get('sequence_j30_email_id')
        if eid:
            variant_ids[variant].append(eid)
        total_sent += 1
    if total_sent == 0:
        empty = {
            'question': {'sent': 0, 'opened': 0, 'clicked': 0, 'open_rate': 0.0, 'ctr': 0.0},
            'invitation': {'sent': 0, 'opened': 0, 'clicked': 0, 'open_rate': 0.0, 'ctr': 0.0},
            'winner': None, 'significant': False,
        }
        _CTR_CACHE['data'] = empty
        _CTR_CACHE['ts'] = _time.monotonic()
        return empty

    previous_winner = (_CTR_CACHE.get('data') or {}).get('winner')
    result = await aggregate_ab_ctr(variant_ids)
    new_winner = result.get('winner')

    _CTR_CACHE['data'] = result
    _CTR_CACHE['ts'] = _time.monotonic()
    logger.info(f'[ctr_cache] refreshed: q_ctr={result.get("question",{}).get("ctr")}%, inv_ctr={result.get("invitation",{}).get("ctr")}%, winner={new_winner}')

    # Notification si nouveau gagnant confirme (transition ou changement)
    if new_winner and new_winner != previous_winner:
        # Verifie l'idempotence via cache_notified pour eviter re-envoi lors de refresh multiples
        already = _CTR_CACHE.get('winner_notified') == new_winner
        if not already:
            await _send_winner_notification(new_winner, result)
            _CTR_CACHE['winner_notified'] = new_winner
    return result


async def ab_ctr_refresh_loop() -> None:
    """Boucle background : refresh le CTR cache 1x/jour (au demarrage puis toutes les 24h)."""
    import asyncio as _asyncio
    logger.info('[ctr_cache] boucle demarree (refresh 1x/jour)')
    # Premier refresh 60s apres startup pour laisser les autres services demarrer
    await _asyncio.sleep(60)
    while True:
        try:
            await refresh_ab_ctr_cache()
        except Exception as e:
            logger.warning(f'[ctr_cache] refresh error: {e}')
        await _asyncio.sleep(_CTR_CACHE_TTL_S)
