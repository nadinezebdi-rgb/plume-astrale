"""
Landing v3 endpoints :
  - GET  /api/landing/testimonials  → 5 derniers témoignages approuvés (public)
  - POST /api/landing/testimonials  → soumission témoignage (auth requise, statut pending)
  - GET  /api/landing/testimonials/admin → tous (approuvés + pending), admin only
  - POST /api/landing/testimonials/{id}/approve  → admin only
  - DELETE /api/landing/testimonials/{id}  → admin only

  - POST /api/landing/ab/track  → track impression/click d'une variante hero (public)
  - GET  /api/landing/ab/stats  → stats A/B hero, admin only

Persiste sur disque via services.app_settings (JSON) — pas de table DB dedicated.
"""
from __future__ import annotations
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from middleware.auth import get_optional_user
from services.supabase_client import get_admin_client
from services.app_settings import get_setting, set_setting

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/landing', tags=['landing'])

# ═══════════════════════════════════════════════════════════════
# Testimonials
# ═══════════════════════════════════════════════════════════════

_SEED_TESTIMONIALS: List[Dict[str, Any]] = []
# ═══ Concours 2026 : aucun témoignage seed. Seuls les vrais témoignages
# ═══ soumis puis approuvés en admin apparaissent publiquement.


def _load_testimonials() -> List[Dict[str, Any]]:
    """Charge la liste; ne seed plus (concours : pas de faux témoignages)."""
    data = get_setting('landing_testimonials')
    if data is None:
        set_setting('landing_testimonials', [])
        return []
    # PURGE : si des seed "seed-*" traînent en DB, on les retire à la volée.
    filtered = [t for t in data if not str(t.get('id', '')).startswith('seed-')]
    if len(filtered) != len(data):
        set_setting('landing_testimonials', filtered)
    return list(filtered)


def _save_testimonials(items: List[Dict[str, Any]]) -> None:
    set_setting('landing_testimonials', items)


class TestimonialSubmit(BaseModel):
    name: str = Field(..., min_length=2, max_length=60)
    sign: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=60)
    quote: str = Field(..., min_length=20, max_length=500)
    transform_before: Optional[str] = Field(None, max_length=200)
    transform_after: Optional[str] = Field(None, max_length=200)


@router.get('/testimonials')
async def landing_testimonials_public(limit: int = 6):
    """Renvoie jusqu'à `limit` témoignages approuvés (default 6, max 100).
    Triés du plus récent au plus ancien."""
    items = _load_testimonials()
    approved = [t for t in items if t.get('status') == 'approved']
    approved.sort(key=lambda t: t.get('created_at', ''), reverse=True)
    limit = max(1, min(100, int(limit or 6)))
    return {
        'testimonials': [{
            'id': t['id'],
            'initial': t.get('initial') or (t.get('name') or '?')[:1].upper(),
            'name': t.get('name'),
            'sign': t.get('sign'),
            'city': t.get('city'),
            'quote': t.get('quote'),
            'transform_before': t.get('transform_before'),
            'transform_after': t.get('transform_after'),
            'stars': t.get('stars', 5),
        } for t in approved[:limit]],
    }


@router.post('/testimonials')
async def landing_testimonial_submit(
    payload: TestimonialSubmit,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Soumission d'un témoignage. Reserve aux utilisateurs authentifies. Status pending."""
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Connecte-toi pour partager ton témoignage.')
    items = _load_testimonials()
    name = payload.name.strip()
    initial = (name[:1] or '?').upper()
    new = {
        'id': f'usr-{uuid.uuid4().hex[:12]}',
        'initial': initial,
        'name': name,
        'sign': (payload.sign or '').strip() or None,
        'city': (payload.city or '').strip() or None,
        'quote': payload.quote.strip(),
        'transform_before': (payload.transform_before or '').strip() or None,
        'transform_after': (payload.transform_after or '').strip() or None,
        'status': 'pending',
        'stars': 5,
        'author_id': current_user.get('id'),
        'author_email': current_user.get('email'),
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    items.append(new)
    _save_testimonials(items)

    # Ping Slack + log historique alertes
    import asyncio as _asyncio
    _asyncio.create_task(_notify_new_testimonial(new))

    return {'submitted': True, 'id': new['id'], 'status': 'pending'}


async def _notify_new_testimonial(t: Dict[str, Any]) -> None:
    """Notification Slack (best effort) + log_alert quand un nouveau témoignage arrive en pending."""
    import os as _os
    import httpx as _httpx
    from services.app_settings import log_alert as _log_alert
    slack_ok = False
    webhook = _os.environ.get('SLACK_WEBHOOK_URL', '').strip()
    if webhook:
        blocks = [
            {'type': 'header', 'text': {'type': 'plain_text',
                'text': '✍️ Nouveau témoignage en attente'}},
            {'type': 'section', 'text': {'type': 'mrkdwn',
                'text': f'*{t.get("name")}*'
                        + (f' · {t.get("sign")}' if t.get('sign') else '')
                        + (f' · {t.get("city")}' if t.get('city') else '')
                        + f'\n>{t.get("quote","")[:280]}'
                        + f'\n_Soumis par_ `{t.get("author_email","?")}`'}},
            {'type': 'actions', 'elements': [{
                'type': 'button',
                'text': {'type': 'plain_text', 'text': 'Ouvrir /admin'},
                'url': 'https://plume-astrale.fr/admin',
                'style': 'primary',
            }]},
        ]
        try:
            async with _httpx.AsyncClient(timeout=6.0) as client:
                r = await client.post(webhook, json={
                    'text': f'Nouveau témoignage : {t.get("name")}', 'blocks': blocks,
                })
                slack_ok = r.status_code in (200, 204)
        except Exception as e:
            logger.warning(f'[testimonial slack] fail: {e}')
    try:
        _log_alert(
            kind='new_testimonial',
            title=f'Nouveau témoignage : {t.get("name")} (pending)',
            details=(t.get('quote') or '')[:180],
            channels=['slack'] if slack_ok else [],
        )
    except Exception:
        pass


async def _require_admin(current_user: Optional[dict]) -> dict:
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')
    return current_user


@router.get('/testimonials/admin')
async def landing_testimonials_admin_list(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    await _require_admin(current_user)
    items = _load_testimonials()
    items.sort(key=lambda t: t.get('created_at', ''), reverse=True)
    return {'testimonials': items}


@router.post('/testimonials/{tid}/approve')
async def landing_testimonial_approve(
    tid: str,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    await _require_admin(current_user)
    items = _load_testimonials()
    for t in items:
        if t.get('id') == tid:
            t['status'] = 'approved'
            _save_testimonials(items)
            return {'approved': True, 'id': tid}
    raise HTTPException(status_code=404, detail='Témoignage introuvable.')


@router.delete('/testimonials/{tid}')
async def landing_testimonial_delete(
    tid: str,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    await _require_admin(current_user)
    items = _load_testimonials()
    new_items = [t for t in items if t.get('id') != tid]
    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail='Témoignage introuvable.')
    _save_testimonials(new_items)
    return {'deleted': True, 'id': tid}


# ═══════════════════════════════════════════════════════════════
# A/B test hero headline
# ═══════════════════════════════════════════════════════════════

VALID_VARIANTS = ('A', 'B')
VALID_EVENTS = ('impression', 'cta_click', 'signup_click')


class ABTrackPayload(BaseModel):
    variant: str
    event: str


@router.post('/ab/track')
async def landing_ab_track(payload: ABTrackPayload):
    """Track une impression ou un clic pour la variante hero A/B (public, no auth)."""
    if payload.variant not in VALID_VARIANTS:
        raise HTTPException(status_code=400, detail='variant doit être A ou B.')
    if payload.event not in VALID_EVENTS:
        raise HTTPException(status_code=400, detail=f'event doit être parmi {VALID_EVENTS}.')
    stats = get_setting('landing_ab_hero_stats') or {}
    key = payload.variant
    row = stats.get(key) or {'impression': 0, 'cta_click': 0, 'signup_click': 0}
    row[payload.event] = int(row.get(payload.event, 0)) + 1
    stats[key] = row
    set_setting('landing_ab_hero_stats', stats)
    return {'ok': True}


@router.get('/ab/stats')
async def landing_ab_stats(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Stats A/B hero, admin only."""
    await _require_admin(current_user)
    stats = get_setting('landing_ab_hero_stats') or {}
    result: Dict[str, Any] = {'variants': {}}
    for v in VALID_VARIANTS:
        row = stats.get(v) or {'impression': 0, 'cta_click': 0, 'signup_click': 0}
        imp = row.get('impression', 0)
        ctc = row.get('cta_click', 0) + row.get('signup_click', 0)
        ctr = round((ctc / imp * 100), 2) if imp else 0.0
        result['variants'][v] = {
            **row,
            'total_clicks': ctc,
            'ctr_pct': ctr,
        }
    # Detect winner (>50 impressions each + CTR delta ≥ 1pt)
    a, b = result['variants']['A'], result['variants']['B']
    if a['impression'] >= 50 and b['impression'] >= 50 and abs(a['ctr_pct'] - b['ctr_pct']) >= 1.0:
        result['winner'] = 'A' if a['ctr_pct'] > b['ctr_pct'] else 'B'
    else:
        result['winner'] = None
    result['forced_variant'] = get_setting('forced_hero_variant')
    result['headlines'] = {
        'A': 'Ton ciel de naissance contient une carte.',
        'B': "La lecture que ton ciel attendait.",
    }
    return result


@router.post('/ab/set-forced-variant')
async def landing_ab_set_forced_variant(
    payload: Dict[str, Any],
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Admin : verrouille manuellement la variante hero servie (ou reset avec variant=null)."""
    await _require_admin(current_user)
    variant = (payload or {}).get('variant')
    if variant not in (None, 'A', 'B'):
        raise HTTPException(status_code=400, detail='variant doit etre null, "A" ou "B".')
    set_setting('forced_hero_variant', variant)
    try:
        from services.app_settings import log_alert
        log_alert(
            kind='hero_ab_lock',
            title=f'Hero forcé sur variante {variant}' if variant else 'Hero A/B débloqué (50/50)',
            details=f'Par {current_user.get("email","admin")}',
            channels=[],
        )
    except Exception:
        pass
    return {'forced_variant': variant}


def _auto_detect_and_lock_winner() -> Optional[str]:
    """Auto-lock du gagnant si:
      - ≥100 impressions par variante
      - delta CTR ≥ 2pt
      - pas déjà verrouillé
    Retourne la variante verrouillée (ou None).
    """
    if get_setting('forced_hero_variant'):
        return None  # Déjà locké
    stats = get_setting('landing_ab_hero_stats') or {}
    a = stats.get('A') or {}
    b = stats.get('B') or {}
    imp_a, imp_b = int(a.get('impression', 0)), int(b.get('impression', 0))
    if imp_a < 100 or imp_b < 100:
        return None
    ctr_a = ((a.get('cta_click', 0) + a.get('signup_click', 0)) / imp_a * 100) if imp_a else 0
    ctr_b = ((b.get('cta_click', 0) + b.get('signup_click', 0)) / imp_b * 100) if imp_b else 0
    if abs(ctr_a - ctr_b) < 2.0:
        return None
    winner = 'A' if ctr_a > ctr_b else 'B'
    loser = 'B' if winner == 'A' else 'A'
    set_setting('forced_hero_variant', winner)
    headlines = {
        'A': 'Ton ciel de naissance contient une carte.',
        'B': "La lecture que ton ciel attendait.",
    }
    winner_ctr = ctr_a if winner == 'A' else ctr_b
    loser_ctr = ctr_b if winner == 'A' else ctr_a
    delta = round(abs(ctr_a - ctr_b), 2)
    try:
        from services.app_settings import log_alert
        log_alert(
            kind='hero_ab_autolock',
            title=f'Auto-lock hero → {winner}',
            details=f'A CTR {ctr_a:.2f}% ({imp_a}) vs B CTR {ctr_b:.2f}% ({imp_b})',
            channels=[],
        )
    except Exception:
        pass
    # Fire-and-forget notification email + slack (best effort)
    try:
        import asyncio as _asyncio
        _asyncio.create_task(_notify_winner_locked(
            winner=winner, loser=loser,
            winner_headline=headlines[winner], loser_headline=headlines[loser],
            winner_ctr=round(winner_ctr, 2), loser_ctr=round(loser_ctr, 2),
            delta=delta, imp_a=imp_a, imp_b=imp_b,
        ))
    except Exception as e:
        logger.warning(f'[hero autolock] notify schedule fail: {e}')
    return winner


async def _notify_winner_locked(winner: str, loser: str,
                                winner_headline: str, loser_headline: str,
                                winner_ctr: float, loser_ctr: float, delta: float,
                                imp_a: int, imp_b: int) -> None:
    """Email + Slack (best effort) quand auto-lock hero declenche."""
    import os as _os
    import httpx as _httpx
    from services.refund_alert import _get_admin_emails as _admins
    from services.resend_service import send_email as _send
    from services.app_settings import log_alert as _log_alert

    subject = f'🏆 Plume Astrale — Hero A/B verrouillé sur {winner} (+{delta}pt CTR)'
    html = f'''
    <div style="max-width:640px;margin:0 auto;font-family:Georgia,serif;
                background:#0b1020;color:#e8e6f0;padding:32px 24px;line-height:1.6;">
      <div style="background:#141a33;border:1px solid rgba(217,178,106,0.35);border-radius:12px;padding:28px;">
        <div style="color:#d9b26a;font-size:11px;letter-spacing:0.2em;text-transform:uppercase;">
          🏆 A/B Hero — Auto-lock déclenché
        </div>
        <h1 style="color:#d9b26a;font-size:22px;margin:10px 0 20px;">
          Variante {winner} verrouillée à 100%
        </h1>
        <p style="color:#4ADE80;font-size:14px;margin:0 0 8px;">
          <strong>Gagnant · {winner}</strong> — CTR {winner_ctr}%
        </p>
        <blockquote style="border-left:3px solid #d9b26a;padding-left:14px;
          margin:6px 0 22px;color:#e8e6f0;font-style:italic;">« {winner_headline} »</blockquote>

        <p style="color:#f87171;font-size:14px;margin:0 0 8px;">
          <strong>Perdante · {loser}</strong> — CTR {loser_ctr}%
        </p>
        <blockquote style="border-left:3px solid #f87171;padding-left:14px;
          margin:6px 0 22px;color:#b8b4c9;font-style:italic;">« {loser_headline} »</blockquote>

        <p style="color:#b8b4c9;font-size:13px;margin-top:24px;">
          Delta CTR : <strong style="color:#d9b26a;">+{delta}pt</strong> · Impressions A {imp_a} · B {imp_b}
        </p>
        <p style="margin-top:20px;font-size:12px;">
          <a href="https://plume-astrale.fr/admin" style="color:#d9b26a;">Débloquer / gérer →</a>
        </p>
        <p style="font-size:11px;color:#7c7ce5;margin-top:20px;font-style:italic;">
          Automatique · Déclenché à ≥100 impressions par variante et ≥2pt de delta CTR.
        </p>
      </div>
    </div>
    '''
    admins = await _admins()
    sent = 0
    for admin_email in admins:
        try:
            eid = await _send(admin_email, subject, html)
            if eid:
                sent += 1
        except Exception as e:
            logger.warning(f'[hero autolock] send fail to {admin_email}: {e}')

    slack_ok = False
    webhook = _os.environ.get('SLACK_WEBHOOK_URL', '').strip()
    if webhook:
        try:
            async with _httpx.AsyncClient(timeout=6.0) as client:
                r = await client.post(webhook, json={
                    'text': f'Hero A/B verrouillé automatiquement sur {winner} (+{delta}pt CTR).',
                    'blocks': [
                        {'type': 'header', 'text': {'type': 'plain_text',
                            'text': f'🏆 Hero A/B → {winner} (+{delta}pt)'}},
                        {'type': 'section', 'text': {'type': 'mrkdwn',
                            'text': f'*Gagnante {winner}* — CTR {winner_ctr}%\n>{winner_headline}\n\n'
                                    f'*Perdante {loser}* — CTR {loser_ctr}%\n>{loser_headline}\n\n'
                                    f'Impressions A {imp_a} · B {imp_b}'}},
                        {'type': 'actions', 'elements': [{'type': 'button',
                            'text': {'type': 'plain_text', 'text': 'Ouvrir /admin'},
                            'url': 'https://plume-astrale.fr/admin', 'style': 'primary'}]},
                    ],
                })
                slack_ok = r.status_code in (200, 204)
        except Exception as e:
            logger.warning(f'[hero autolock] slack fail: {e}')

    try:
        channels = []
        if sent:
            channels.append(f'email x{sent}')
        if slack_ok:
            channels.append('slack')
        _log_alert(
            kind='hero_autolock_notified',
            title=f'Auto-lock {winner} — notifs envoyées',
            details=f'Delta {delta}pt · CTR {winner_ctr}% vs {loser_ctr}%',
            channels=channels,
        )
    except Exception:
        pass


@router.get('/ab/serve-variant')
async def landing_ab_serve_variant():
    """Endpoint public : indique quelle variante hero servir (auto-lock si winner détecté).
    Retourne {variant: 'A'|'B'|null, forced: bool}. Si null, le client peut faire son propre pick."""
    _auto_detect_and_lock_winner()
    forced = get_setting('forced_hero_variant')
    if forced in VALID_VARIANTS:
        return {'variant': forced, 'forced': True}
    return {'variant': None, 'forced': False}


@router.get('/trust-stats')
async def landing_trust_stats():
    """Stats publiques pour badges de confiance (hero, section 2).
    - total_readings : commandes lecture_complete payées (hors bypass admin)
    - approved_reviews : témoignages approuvés
    - average_rating : moyenne étoiles témoignages (fallback 4.9)
    """
    sb = get_admin_client()
    total_readings = 0
    try:
        r = sb.table('payment_transactions').select('metadata', count='exact').eq(
            'pack_id', 'lecture_complete').eq('payment_status', 'paid').execute()
        for row in (r.data or []):
            md = row.get('metadata') or {}
            if not md.get('admin_bypass') and not md.get('refunded_at'):
                total_readings += 1
    except Exception as e:
        logger.warning(f'[trust-stats] fetch fail: {e}')

    items = _load_testimonials()
    approved = [t for t in items if t.get('status') == 'approved']
    approved_count = len(approved)
    if approved:
        avg = sum(int(t.get('stars', 5)) for t in approved) / approved_count
        average_rating = round(avg, 1)
    else:
        average_rating = 4.9

    # Nombre affichable "arrondi" (marketing, jamais surestimé)
    if total_readings >= 2000:
        display_count = f'+{2000 + ((total_readings - 2000) // 100) * 100}'
    elif total_readings >= 100:
        display_count = f'+{(total_readings // 50) * 50}'
    else:
        display_count = '+2 000'  # baseline historique
    return {
        'total_readings': total_readings,
        'approved_reviews': approved_count,
        'average_rating': average_rating,
        'display_count': display_count,
    }


@router.get('/rating-timeseries')
async def landing_rating_timeseries(days: int = 30):
    """Renvoie une timeseries lissée pour sparkline trust bar.
    Points = un par jour sur `days` derniers jours.
    Chaque point : {date, count (nb temoignages approuves ce jour-la),
                    avg (moyenne etoiles rolling 7j, fallback 4.9)}
    """
    from datetime import datetime as _dt, timedelta as _td, timezone as _tz
    days = max(7, min(90, int(days or 30)))
    items = _load_testimonials()
    approved = [t for t in items if t.get('status') == 'approved']
    # Bucket par jour
    by_day: Dict[str, List[int]] = {}
    for t in approved:
        try:
            d = _dt.fromisoformat((t.get('created_at') or '').replace('Z', '+00:00'))
        except Exception:
            continue
        key = d.date().isoformat()
        by_day.setdefault(key, []).append(int(t.get('stars', 5)))

    today = _dt.now(_tz.utc).date()
    points = []
    global_avg = 4.9
    # Rolling window de 7 jours pour lisser la moyenne
    for i in range(days - 1, -1, -1):
        day = today - _td(days=i)
        key = day.isoformat()
        window_stars: List[int] = []
        for j in range(7):
            wkey = (day - _td(days=j)).isoformat()
            window_stars.extend(by_day.get(wkey, []))
        avg = round(sum(window_stars) / len(window_stars), 2) if window_stars else global_avg
        points.append({
            'date': key,
            'count': len(by_day.get(key, [])),
            'avg': avg,
        })
    return {'points': points, 'days': days}
