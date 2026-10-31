"""Health-check continu sur la clé astrology-api.io.

- Ping /api/v3/horoscope/sign/daily toutes les 6h avec la clé courante.
- Si le ping tombe en 401/403 (clé révoquée/invalide), envoie une alerte email
  via Resend à ADMIN_ALERT_EMAIL avec le détail et les étapes de correction.
- Rate limiting : max 1 alerte par 12h pour éviter le spam (fichier marker /tmp).
- Exposé aussi via GET /api/health/astrology-io pour vérification manuelle.
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

ASTRO_BASE = 'https://api.astrology-api.io/api/v3'
PING_PATH = '/horoscope/sign/daily'
PING_PAYLOAD = {'sign': 'leo', 'date': datetime.now(timezone.utc).strftime('%Y-%m-%d')}

ADMIN_ALERT_EMAIL = os.environ.get('ADMIN_ALERT_EMAIL', 'contact@plume-astrale.fr')
CHECK_INTERVAL_SECONDS = 6 * 60 * 60  # 6h
ALERT_COOLDOWN_SECONDS = 12 * 60 * 60  # 12h entre 2 alertes
ALERT_MARKER = Path('/tmp/plume_astrology_io_last_alert.txt')

# Compteur de 5xx consécutifs (dégradation progressive). Seuil : 3 → alerte.
_consecutive_5xx = 0
CONSECUTIVE_5XX_THRESHOLD = 3


def _get_key() -> str:
    return os.environ.get('ASTROLOGY_API_IO_KEY', '').strip()


def _key_fingerprint(key: str) -> str:
    if not key:
        return '(empty)'
    return f'{key[:10]}…{key[-4:]} (len={len(key)})'


async def ping_astrology_api(timeout: float = 10.0) -> dict:
    """Retourne un dict {ok, status, latency_ms, error, key_fingerprint}.

    - ok=True si HTTP 200
    - ok=False si 401/403/404/500/timeout/… — error contient le motif actionnable
    """
    key = _get_key()
    if not key:
        return {
            'ok': False,
            'status': None,
            'latency_ms': 0,
            'error': 'ASTROLOGY_API_IO_KEY env var manquante',
            'key_fingerprint': '(empty)',
            'checked_at': datetime.now(timezone.utc).isoformat(),
        }
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
    }
    payload = {'sign': 'leo', 'date': datetime.now(timezone.utc).strftime('%Y-%m-%d')}
    url = f'{ASTRO_BASE}{PING_PATH}'
    started = datetime.now(timezone.utc)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, json=payload, headers=headers)
        latency_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        if r.status_code == 200:
            return {
                'ok': True,
                'status': 200,
                'latency_ms': latency_ms,
                'error': None,
                'key_fingerprint': _key_fingerprint(key),
                'checked_at': datetime.now(timezone.utc).isoformat(),
            }
        body = (r.text or '')[:300]
        reason = 'Clé invalide/revoquée' if r.status_code in (401, 403) else f'HTTP {r.status_code}'
        return {
            'ok': False,
            'status': r.status_code,
            'latency_ms': latency_ms,
            'error': f'{reason} — body: {body}',
            'key_fingerprint': _key_fingerprint(key),
            'checked_at': datetime.now(timezone.utc).isoformat(),
        }
    except httpx.TimeoutException:
        return {
            'ok': False,
            'status': None,
            'latency_ms': int(timeout * 1000),
            'error': f'Timeout après {timeout}s',
            'key_fingerprint': _key_fingerprint(key),
            'checked_at': datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            'ok': False,
            'status': None,
            'latency_ms': 0,
            'error': f'{type(e).__name__}: {str(e)[:200]}',
            'key_fingerprint': _key_fingerprint(key),
            'checked_at': datetime.now(timezone.utc).isoformat(),
        }


def _alert_cooldown_elapsed() -> bool:
    if not ALERT_MARKER.exists():
        return True
    try:
        last = datetime.fromisoformat(ALERT_MARKER.read_text().strip())
        return (datetime.now(timezone.utc) - last).total_seconds() >= ALERT_COOLDOWN_SECONDS
    except Exception:
        return True


def _mark_alert_sent() -> None:
    try:
        ALERT_MARKER.write_text(datetime.now(timezone.utc).isoformat())
    except Exception as e:
        logger.warning(f'[astro_health] mark_alert_sent failed: {e}')


def _build_alert_email(result: dict, reason: str = 'auth') -> tuple[str, str, str]:
    if reason == '5xx_streak':
        title = 'Astrology-API.io renvoie des erreurs 5xx en continu'
        intro = (
            'Le health-check automatique a détecté <strong>3 erreurs 5xx consécutives</strong> '
            "sur astrology-api.io — dégradation progressive ou outage côté fournisseur. "
            'Les services payants (PDF Thème Natal, Synastrie, chat Soléna) peuvent être lents ou en échec intermittent.'
        )
        actions = """
        <ol style="line-height: 1.7; color: #334155; padding-left: 20px;">
          <li>Vérifie le statut du fournisseur : <a href="https://status.astrology-api.io" style="color: #B8935A;">status.astrology-api.io</a> (si existe).</li>
          <li>Teste manuellement : <code>GET /api/health/astrology-io</code> — si le status revient à 200, l'alerte se résoudra toute seule.</li>
          <li>Si l'incident dure plus de 2h, envisage de dégrader gracieusement les pages concernées côté frontend ou de contacter le support astrology-api.io.</li>
        </ol>"""
        subject = '⚠️ Plume Astrale — Astrology-API.io en dégradation 5xx'
    else:
        title = 'Clé astrology-api.io en erreur'
        intro = (
            'Le health-check automatique a détecté que la clé astrology-api.io ne répond plus correctement. '
            'Les services payants (PDF Thème Natal, Synastrie, chat Soléna, Astrocarto, Numérologie) sont probablement en panne.'
        )
        actions = """
        <ol style="line-height: 1.7; color: #334155; padding-left: 20px;">
          <li>Va sur <a href="https://dashboard.astrology-api.io" style="color: #B8935A;">dashboard.astrology-api.io</a> et vérifie l'état du compte + abonnement.</li>
          <li>Révoque l'ancienne clé et génère-en une nouvelle.</li>
          <li>Mets à jour la variable <code>ASTROLOGY_API_IO_KEY</code> sur Railway puis redéploie.</li>
          <li>Teste manuellement : <code>GET /api/health/astrology-io</code> doit renvoyer <code>ok: true</code>.</li>
        </ol>"""
        subject = '🚨 Plume Astrale — Clé astrology-api.io en erreur'

    html = f"""
    <div style="font-family: Inter, Arial, sans-serif; max-width: 560px; margin: 0 auto; padding: 24px; color: #0B1A2E;">
      <h2 style="font-family: Fraunces, Georgia, serif; font-weight: 400; font-size: 22px; margin: 0 0 16px;">
        {title}
      </h2>
      <p style="line-height: 1.6; color: #334155;">{intro}</p>
      <table style="width: 100%; margin: 20px 0; border-collapse: collapse; font-size: 13px;">
        <tr><td style="padding: 6px 0; color: #64748B;">Statut HTTP</td><td style="padding: 6px 0;"><strong>{result.get('status') or 'n/a'}</strong></td></tr>
        <tr><td style="padding: 6px 0; color: #64748B;">Erreur</td><td style="padding: 6px 0;">{result.get('error') or '(inconnue)'}</td></tr>
        <tr><td style="padding: 6px 0; color: #64748B;">Clé testée</td><td style="padding: 6px 0; font-family: monospace;">{result.get('key_fingerprint')}</td></tr>
        <tr><td style="padding: 6px 0; color: #64748B;">Latence</td><td style="padding: 6px 0;">{result.get('latency_ms')} ms</td></tr>
        <tr><td style="padding: 6px 0; color: #64748B;">Vérifié à</td><td style="padding: 6px 0;">{result.get('checked_at')} UTC</td></tr>
      </table>
      <h3 style="font-family: Fraunces, Georgia, serif; font-weight: 400; font-size: 16px; margin: 24px 0 8px;">Actions correctives</h3>
      {actions}
      <p style="font-size: 12px; color: #94A3B8; margin-top: 32px;">
        Cette alerte est envoyée au maximum 1 fois toutes les 12h. Le prochain check aura lieu dans 6h.
      </p>
    </div>
    """
    text = (
        f"Plume Astrale — {title}\n\n"
        f"Statut : {result.get('status')}\n"
        f"Erreur : {result.get('error')}\n"
        f"Clé    : {result.get('key_fingerprint')}\n"
        f"Date   : {result.get('checked_at')} UTC\n"
    )
    return subject, html, text


async def send_astrology_alert(result: dict, reason: str = 'auth') -> bool:
    """Envoie l'alerte Resend si cooldown écoulé. Retourne True si envoyée.

    reason : 'auth' (401/403/clé manquante) | '5xx_streak' (3 erreurs 5xx consécutives)
    """
    if not _alert_cooldown_elapsed():
        logger.info('[astro_health] alerte déjà envoyée récemment, skip (cooldown 12h)')
        return False
    try:
        from services.resend_service import send_email
        subject, html, text = _build_alert_email(result, reason=reason)
        eid = await send_email(ADMIN_ALERT_EMAIL, subject, html, text)
        if eid:
            _mark_alert_sent()
            logger.warning(f'[astro_health] alerte ({reason}) envoyée à {ADMIN_ALERT_EMAIL} (resend_id={eid})')
            # Persist en base pour dashboard admin (non-bloquant si table absente)
            _persist_alert(
                alert_type=f'astrology_io_{reason}',
                severity='high',
                subject=subject,
                reason=reason,
                result=result,
                resend_id=eid,
            )
            return True
        logger.error('[astro_health] envoi alerte Resend échoué (eid=None)')
        return False
    except Exception as e:
        logger.exception(f'[astro_health] send_astrology_alert failed: {e}')
        return False


def _persist_alert(
    alert_type: str,
    severity: str,
    subject: str,
    reason: str,
    result: dict,
    resend_id: Optional[str],
) -> None:
    """Insère l'alerte dans Supabase `admin_alerts`. Log WARNING actionnable si table manquante.

    Ne lève jamais : si la persistance échoue, l'alerte email a déjà été envoyée.
    """
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        sb.table('admin_alerts').insert({
            'alert_type': alert_type,
            'severity': severity,
            'subject': subject,
            'reason': reason,
            'http_status': result.get('status'),
            'error_detail': (result.get('error') or '')[:500],
            'payload': {
                'key_fingerprint': result.get('key_fingerprint'),
                'latency_ms': result.get('latency_ms'),
                'checked_at': result.get('checked_at'),
            },
            'resend_id': resend_id,
            'recipient': ADMIN_ALERT_EMAIL,
        }).execute()
        logger.info(f'[astro_health] alert persisted ({alert_type})')
    except Exception as e:
        msg = str(e)
        if 'admin_alerts' in msg and ('schema cache' in msg or 'does not exist' in msg):
            logger.warning(
                '[astro_health] Table `admin_alerts` absente. Exécuter '
                '/app/backend/migrations/2026_02_admin_alerts.sql dans le SQL Editor Supabase '
                'pour activer le dashboard /admin/alerts.'
            )
        else:
            logger.warning(f'[astro_health] persist alert failed: {msg[:200]}')


async def astrology_io_health_loop() -> None:
    """Boucle infinie : ping toutes les 6h, alerte si échec."""
    global _consecutive_5xx
    logger.info(f'[astro_health] boucle démarrée — ping {PING_PATH} toutes les 6h, alerte → {ADMIN_ALERT_EMAIL}')
    # Grace period au démarrage (évite spam alertes si backend bootstrap met du temps).
    try:
        await asyncio.sleep(120)
    except asyncio.CancelledError:
        raise
    while True:
        try:
            result = await ping_astrology_api()
            if result['ok']:
                if _consecutive_5xx:
                    logger.info(f'[astro_health] 5xx streak reset (était à {_consecutive_5xx})')
                _consecutive_5xx = 0
                logger.info(f"[astro_health] ✓ OK · {result['latency_ms']}ms · {result['key_fingerprint']}")
            else:
                status = result['status']
                err = result['error'] or ''
                logger.error(f"[astro_health] ✗ ÉCHEC · HTTP {status} · {err}")
                if status in (401, 403) or 'env var manquante' in err:
                    # Auth error → alerte immédiate (reset streak 5xx au cas où)
                    _consecutive_5xx = 0
                    await send_astrology_alert(result, reason='auth')
                elif isinstance(status, int) and 500 <= status < 600:
                    _consecutive_5xx += 1
                    logger.warning(f'[astro_health] 5xx streak = {_consecutive_5xx}/{CONSECUTIVE_5XX_THRESHOLD}')
                    if _consecutive_5xx >= CONSECUTIVE_5XX_THRESHOLD:
                        await send_astrology_alert(result, reason='5xx_streak')
                        # reset après alerte pour éviter re-déclenchement au prochain cycle
                        _consecutive_5xx = 0
                else:
                    # timeout/404/autre → ni alerte ni incrément streak 5xx
                    pass
        except Exception as e:
            logger.exception(f'[astro_health] loop iteration failed: {e}')
        try:
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            logger.info('[astro_health] boucle arrêtée (CancelledError)')
            raise
