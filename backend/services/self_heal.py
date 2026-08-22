"""
Auto-réparation des produits one-shot : si le webhook Stripe n'atteint pas le
backend (non configuré côté Stripe, ou down au moment du paiement), les pages
succès pollent /status — on en profite pour vérifier le paiement DIRECTEMENT
auprès de Stripe et déclencher la génération/livraison manquante.

Étend aussi aux sessions `admin-natal-*` (bypass promo admin) : elles ne
transitent pas par Stripe mais peuvent hériter d'un statut `pending` bloqué
si le pod backend redémarre pendant la génération PDF (crash, deploy, OOM).
Le poll de /status détectera alors ce pending stale et relancera le handler.
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

_inflight: set = set()

# Après combien de temps un `pdf_status: pending` est considéré comme "stale"
# (server crashé/redémarré au milieu de la génération) et doit être relancé.
# Budget réaliste du pipeline complet :
#   • enrich_natal_ultra (GPT) ≤ 90s
#   • enrich_book_chapters (GPT) ≤ 90s
#   • astrology API v3 ≤ 30s
#   • cairosvg + reportlab (thread) ≤ 60s
#   • Upload Supabase 27 Mo ≤ 30s
#   • Email Resend ≤ 10s
# Worst case = ~310s. On prend 420s (7 min) de marge pour être sûr qu'un
# pending "stale" est vraiment orphelin et pas juste une génération lente.
_STALE_PENDING_S = 420


async def self_heal_if_paid(session_id: str, already_delivered: bool, handler) -> None:
    """Si le paiement est confirmé mais rien n'a été livré, lance le handler produit.

    - Sessions Stripe (`cs_...`) : on interroge Stripe pour valider le payment_status
      avant de déclencher (couvre le cas où le webhook Stripe ne nous atteint pas).
    - Sessions admin bypass (`admin-natal-*`) : pas de Stripe, on relance directement
      si le PDF n'existe pas encore et que la génération semble stale (pending trop
      ancien ou statut absent).
    """
    if already_delivered or not session_id:
        return
    if session_id in _inflight:
        return

    # ─── Cas 1 : admin bypass — pas de Stripe, self-heal direct
    if session_id.startswith('admin-natal-') or session_id.startswith('admin-'):
        _inflight.add(session_id)
        try:
            from services.supabase_client import get_admin_client
            sb = get_admin_client()
            r = sb.table('payment_transactions').select('metadata').eq('session_id', session_id).maybe_single().execute()
            if not r or not r.data:
                return
            md = r.data.get('metadata') or {}
            # Déjà livré ? ne fait rien
            if md.get('pdf_path'):
                return
            # Génération en échec explicite : ne relance PAS (l'admin doit fixer via /admin)
            if md.get('pdf_status') == 'failed':
                return
            # Statut pending stale (crash server au milieu) ou absent → relance
            started_at = md.get('regenerate_started_at') or md.get('pending_started_at')
            stale = True
            if started_at:
                try:
                    dt = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    stale = (datetime.now(timezone.utc) - dt) > timedelta(seconds=_STALE_PENDING_S)
                except Exception:
                    stale = True
            if stale:
                # Compare-and-swap : ne relance que si `pending_started_at` n'a pas
                # changé depuis la lecture (évite les doubles-relances via polls
                # concurrents entre plusieurs pods ou plusieurs onglets clients).
                new_pending = datetime.now(timezone.utc).isoformat()
                try:
                    q = sb.table('payment_transactions').update({'metadata': {**md, 'pdf_status': 'pending', 'pending_started_at': new_pending}}).eq('session_id', session_id)
                    if started_at:
                        # Ne mets à jour que si le pending_started_at en base est
                        # toujours celui qu'on a lu (protection concurrence).
                        q = q.eq('metadata->>pending_started_at', started_at)
                    result = q.execute()
                    updated = bool(result and result.data)
                except Exception as _e:
                    logger.info(f'[self_heal] CAS conditional update failed, falling back: {_e}')
                    updated = False
                if not updated:
                    # Un autre pod a déjà attrapé le lock, on abandonne
                    logger.info(f'[self_heal] admin bypass {session_id} pending claimed by another worker, skip')
                    return
                logger.info(f'[self_heal] admin bypass {session_id} stale/absent → relance handler')
                await handler(session_id)
        except Exception as e:
            logger.warning(f'[self_heal] admin {session_id}: {e}')
        finally:
            _inflight.discard(session_id)
        return

    # ─── Cas 2 : Stripe (`cs_...`) — vérifie paiement puis déclenche
    if not session_id.startswith('cs_'):
        return
    _inflight.add(session_id)
    try:
        from integrations.payments.stripe.checkout import StripeCheckout
        sc = StripeCheckout(api_key=os.environ['STRIPE_API_KEY'], webhook_url='')
        st = await sc.get_checkout_status(session_id)
        if getattr(st, 'payment_status', '') == 'paid':
            # Le webhook Stripe n'est pas arrivé : ce chemin envoie l'event Meta.
            # track_purchase_once est idempotent (verrou capi_sent_at).
            try:
                from services.capi_purchase import track_purchase_once
                await track_purchase_once(session_id, {'payment_status': 'paid'})
            except Exception as e:
                logger.warning(f'[self_heal] capi purchase fail: {e}')
            logger.info(f'[self_heal] paiement confirmé via polling Stripe → livraison déclenchée ({session_id})')
            await handler(session_id)
    except Exception as e:
        logger.warning(f'[self_heal] {session_id}: {e}')
    finally:
        _inflight.discard(session_id)
