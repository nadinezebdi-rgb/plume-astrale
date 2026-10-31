"""Health-check continu du domaine canonique Plume Astrale.

- Ping https://plume-astrale.fr/ toutes les 6h.
- Inspecte le certificat SSL : alerte si expire dans ≤14 jours ou invalide.
- Alerte si le domaine renvoie du non-2xx 3× consécutivement (DNS pétés /
  reverse proxy down / certificate chain cassée côté Cloudflare).
- Alerte Resend à ADMIN_ALERT_EMAIL avec cooldown 12h partagé avec les autres
  health-checks pour éviter le spam.
"""
from __future__ import annotations
import asyncio
import logging
import os
import socket
import ssl
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

CANONICAL_URL = os.environ.get('CANONICAL_DOMAIN_URL', 'https://plume-astrale.fr').rstrip('/')
ADMIN_ALERT_EMAIL = os.environ.get('ADMIN_ALERT_EMAIL', 'contact@plume-astrale.fr')
CHECK_INTERVAL_SECONDS = 6 * 60 * 60  # 6h
ALERT_COOLDOWN_SECONDS = 12 * 60 * 60  # 12h
SSL_EXPIRY_WARN_DAYS = 14
HTTP_FAIL_STREAK_THRESHOLD = 3
# Même logique côté SSL : on exige N checks consécutifs KO avant d'alerter
# pour éviter les faux positifs (propagation DNS, reissue en cours, flapping edge).
SSL_FAIL_STREAK_THRESHOLD = 3

ALERT_MARKER = Path('/tmp/plume_dns_last_alert.txt')
_http_fail_streak = 0
_ssl_fail_streak = 0


def _hostname(url: str) -> str:
    from urllib.parse import urlparse
    return urlparse(url).hostname or ''


def _check_ssl(hostname: str, port: int = 443, timeout: float = 10.0) -> dict:
    """Retourne {ok, days_remaining, not_after, error}."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
        not_after = cert.get('notAfter')
        if not not_after:
            return {'ok': False, 'days_remaining': None, 'not_after': None, 'error': 'notAfter absent du certificat'}
        # Parse date au format "Oct 20 12:00:00 2026 GMT"
        exp = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z').replace(tzinfo=timezone.utc)
        days = (exp - datetime.now(timezone.utc)).days
        return {'ok': days > 0, 'days_remaining': days, 'not_after': exp.isoformat(), 'error': None}
    except (ssl.SSLError, ssl.CertificateError) as e:
        return {'ok': False, 'days_remaining': None, 'not_after': None, 'error': f'SSL: {type(e).__name__}: {str(e)[:150]}'}
    except (socket.gaierror, socket.timeout, OSError) as e:
        return {'ok': False, 'days_remaining': None, 'not_after': None, 'error': f'DNS/Socket: {type(e).__name__}: {str(e)[:150]}'}
    except Exception as e:
        return {'ok': False, 'days_remaining': None, 'not_after': None, 'error': f'{type(e).__name__}: {str(e)[:150]}'}


async def ping_domain(timeout: float = 10.0) -> dict:
    """Retourne {ok, http_status, ssl: {...}, latency_ms, checked_at}."""
    started = datetime.now(timezone.utc)
    host = _hostname(CANONICAL_URL)
    ssl_result = _check_ssl(host) if host else {'ok': False, 'error': 'hostname missing'}
    http_status: Optional[int] = None
    http_err: Optional[str] = None
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            r = await client.get(CANONICAL_URL)
            http_status = r.status_code
    except httpx.TimeoutException:
        http_err = f'HTTP timeout après {timeout}s'
    except Exception as e:
        http_err = f'{type(e).__name__}: {str(e)[:150]}'
    latency_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
    http_ok = isinstance(http_status, int) and 200 <= http_status < 400
    ssl_days = ssl_result.get('days_remaining')
    ssl_ok = ssl_result.get('ok') and (ssl_days is None or ssl_days > SSL_EXPIRY_WARN_DAYS)
    return {
        'ok': http_ok and ssl_ok,
        'url': CANONICAL_URL,
        'http_status': http_status,
        'http_error': http_err,
        'ssl': ssl_result,
        'latency_ms': latency_ms,
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
        logger.warning(f'[dns_health] mark_alert_sent failed: {e}')


def _build_alert_email(result: dict, reason: str) -> tuple[str, str, str]:
    ssl_info = result.get('ssl') or {}
    if reason == 'ssl_expiring':
        title = f"SSL expire dans {ssl_info.get('days_remaining')} jours"
        intro = (
            f"Le certificat SSL du domaine <strong>{result['url']}</strong> expire "
            f"dans <strong>{ssl_info.get('days_remaining')} jours</strong> "
            f"({ssl_info.get('not_after')}). Renouvelle-le avant expiration pour éviter un blackout."
        )
        subject = f'⚠️ Plume Astrale — SSL {result["url"]} expire bientôt'
    elif reason == 'ssl_broken':
        title = 'SSL/DNS invalide sur le domaine canonique'
        intro = (
            f"Le certificat SSL du domaine <strong>{result['url']}</strong> ne peut pas être validé. "
            f"Cela peut casser l'indexation moteur et le partage social. Détail : {ssl_info.get('error')}"
        )
        subject = f'🚨 Plume Astrale — SSL cassé sur {result["url"]}'
    else:  # http_fail_streak
        title = f'Domaine canonique injoignable (HTTP {result.get("http_status") or "?"})'
        intro = (
            f"Le domaine <strong>{result['url']}</strong> renvoie une erreur HTTP depuis 3 checks consécutifs. "
            f"DNS cassés ou reverse-proxy down. Détail : {result.get('http_error') or 'status=' + str(result.get('http_status'))}"
        )
        subject = f'🚨 Plume Astrale — {result["url"]} injoignable'
    html = f"""
    <div style="font-family: Inter, Arial, sans-serif; max-width: 560px; margin: 0 auto; padding: 24px; color: #0B1A2E;">
      <h2 style="font-family: Fraunces, Georgia, serif; font-weight: 400; font-size: 22px; margin: 0 0 16px;">{title}</h2>
      <p style="line-height: 1.6; color: #334155;">{intro}</p>
      <table style="width: 100%; margin: 20px 0; border-collapse: collapse; font-size: 13px;">
        <tr><td style="padding: 6px 0; color: #64748B;">URL</td><td style="padding: 6px 0; font-family: monospace;">{result['url']}</td></tr>
        <tr><td style="padding: 6px 0; color: #64748B;">HTTP</td><td style="padding: 6px 0;">{result.get('http_status') or 'n/a'}</td></tr>
        <tr><td style="padding: 6px 0; color: #64748B;">SSL expire</td><td style="padding: 6px 0;">{ssl_info.get('not_after') or 'n/a'} ({ssl_info.get('days_remaining')} jours)</td></tr>
        <tr><td style="padding: 6px 0; color: #64748B;">Latence</td><td style="padding: 6px 0;">{result.get('latency_ms')} ms</td></tr>
      </table>
      <p style="font-size: 12px; color: #94A3B8; margin-top: 32px;">Alertes limitées à 1 toutes les 12h.</p>
    </div>
    """
    text = f'Plume Astrale — {title}\nURL: {result["url"]}\nHTTP: {result.get("http_status")}\nSSL: {ssl_info.get("not_after")}\n'
    return subject, html, text


async def send_dns_alert(result: dict, reason: str) -> bool:
    if not _alert_cooldown_elapsed():
        logger.info('[dns_health] alerte déjà envoyée récemment, skip (cooldown 12h)')
        return False
    try:
        from services.resend_service import send_email
        subject, html, text = _build_alert_email(result, reason)
        eid = await send_email(ADMIN_ALERT_EMAIL, subject, html, text)
        if eid:
            _mark_alert_sent()
            logger.warning(f'[dns_health] alerte ({reason}) envoyée → {ADMIN_ALERT_EMAIL} (resend_id={eid})')
            # Persist pour dashboard admin
            _persist_alert(reason, subject, result, eid)
            return True
        return False
    except Exception as e:
        logger.exception(f'[dns_health] send alert failed: {e}')
        return False


def _persist_alert(reason: str, subject: str, result: dict, resend_id: Optional[str]) -> None:
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        ssl_info = result.get('ssl') or {}
        sb.table('admin_alerts').insert({
            'alert_type': f'dns_domain_{reason}',
            'severity': 'high' if reason == 'ssl_broken' or reason == 'http_fail_streak' else 'medium',
            'subject': subject,
            'reason': reason,
            'http_status': result.get('http_status'),
            'error_detail': (result.get('http_error') or ssl_info.get('error') or '')[:500],
            'payload': {
                'url': result.get('url'),
                'latency_ms': result.get('latency_ms'),
                'ssl_days_remaining': ssl_info.get('days_remaining'),
                'ssl_not_after': ssl_info.get('not_after'),
                'checked_at': result.get('checked_at'),
            },
            'resend_id': resend_id,
            'recipient': ADMIN_ALERT_EMAIL,
        }).execute()
    except Exception as e:
        msg = str(e)
        if 'admin_alerts' in msg and ('schema cache' in msg or 'does not exist' in msg):
            logger.warning('[dns_health] Table admin_alerts absente — exécuter la migration consolidée Supabase.')
        else:
            logger.warning(f'[dns_health] persist failed: {msg[:200]}')


async def dns_domain_health_loop() -> None:
    """Boucle 6h : ping + alerte SSL/HTTP."""
    global _http_fail_streak, _ssl_fail_streak
    logger.info(f'[dns_health] boucle démarrée — ping {CANONICAL_URL} toutes les 6h (seuil SSL {SSL_FAIL_STREAK_THRESHOLD}× / HTTP {HTTP_FAIL_STREAK_THRESHOLD}×)')
    try:
        await asyncio.sleep(240)  # grace 4 min pour laisser l'app booter avant pings externes
    except asyncio.CancelledError:
        raise
    while True:
        try:
            result = await ping_domain()
            ssl_info = result.get('ssl') or {}
            if not result['ok']:
                http_err = result.get('http_error')
                http_status = result.get('http_status')
                ssl_ok = ssl_info.get('ok')
                days = ssl_info.get('days_remaining')
                # 1. SSL cassé = incrémente streak, alerte après N consécutifs
                if not ssl_ok and ssl_info.get('error'):
                    _ssl_fail_streak += 1
                    logger.warning(f'[dns_health] SSL streak = {_ssl_fail_streak}/{SSL_FAIL_STREAK_THRESHOLD} · {ssl_info.get("error")[:120]}')
                    _http_fail_streak = 0
                    if _ssl_fail_streak >= SSL_FAIL_STREAK_THRESHOLD:
                        await send_dns_alert(result, 'ssl_broken')
                        _ssl_fail_streak = 0
                # 2. SSL expire bientôt (pas de streak — expiration est stable, pas flappy)
                elif days is not None and days <= SSL_EXPIRY_WARN_DAYS:
                    _ssl_fail_streak = 0
                    _http_fail_streak = 0
                    await send_dns_alert(result, 'ssl_expiring')
                # 3. HTTP KO = incrémente streak
                elif http_err or (isinstance(http_status, int) and http_status >= 400):
                    _ssl_fail_streak = 0
                    _http_fail_streak += 1
                    logger.warning(f'[dns_health] HTTP streak = {_http_fail_streak}/{HTTP_FAIL_STREAK_THRESHOLD}')
                    if _http_fail_streak >= HTTP_FAIL_STREAK_THRESHOLD:
                        await send_dns_alert(result, 'http_fail_streak')
                        _http_fail_streak = 0
            else:
                if _http_fail_streak or _ssl_fail_streak:
                    logger.info(f'[dns_health] streaks reset (HTTP={_http_fail_streak}, SSL={_ssl_fail_streak})')
                _http_fail_streak = 0
                _ssl_fail_streak = 0
                logger.info(f'[dns_health] ✓ OK · HTTP {result["http_status"]} · SSL expire dans {ssl_info.get("days_remaining")}j')
        except Exception as e:
            logger.exception(f'[dns_health] loop failed: {e}')
        try:
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            logger.info('[dns_health] boucle arrêtée')
            raise
