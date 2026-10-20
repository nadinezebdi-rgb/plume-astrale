"""Auto-lock des variantes gagnantes d'expériences A/B.

Logique :
- Requête `ab_events` pour l'expérience `home_hero_h1`.
- Pour chaque variante, calcule `shown` et `cta_click` → CTR = cta_click / shown.
- Si le leader a `shown >= MIN_SHOWN` ET un lift >= `MIN_LIFT_PCT` vs la 2e variante,
  on verrouille le gagnant dans la table `experiment_locks`.
- Si le lock existe déjà, ne rien faire (one-way lock, pour éviter yo-yo).
- Dégrade gracieusement si tables absentes.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

MIN_SHOWN_PER_VARIANT = 500
MIN_LIFT_PCT = 10.0  # écart relatif min vs 2e variante pour verrouiller


async def check_and_lock_experiment(experiment: str = 'home_hero_h1') -> Optional[dict]:
    """Scan + verrouille si conditions remplies. Retourne un résumé.

    Returns:
        {status: 'locked'|'already_locked'|'insufficient_data'|'unclear_winner'|'error',
         winner: str|None, variants: [...], reason: str}
    """
    from services.supabase_client import get_admin_client
    sb = get_admin_client()

    # 1) Si déjà verrouillé → noop
    try:
        existing = sb.table('experiment_locks').select('variant, locked_at').eq('experiment', experiment).maybe_single().execute()
        if existing and existing.data:
            return {
                'status': 'already_locked',
                'winner': existing.data.get('variant'),
                'reason': f"déjà verrouillé le {existing.data.get('locked_at')}",
            }
    except Exception as e:
        msg = str(e)
        if 'experiment_locks' in msg and ('schema cache' in msg or 'does not exist' in msg):
            logger.warning('[exp_lock] Table experiment_locks absente — exécuter la migration consolidée.')
            # Continue : si la table n'existe pas, on ne peut pas lock → on retourne juste les stats
        else:
            logger.warning(f'[exp_lock] lookup lock failed: {msg[:200]}')

    # 2) Agréger les events
    try:
        r = sb.table('ab_events').select('variant, event_name').eq('experiment', experiment).limit(100000).execute()
        rows = r.data or []
    except Exception as e:
        return {'status': 'error', 'reason': f'ab_events query failed: {str(e)[:200]}'}

    agg: dict[str, dict[str, int]] = {}
    for row in rows:
        v = row.get('variant')
        e = row.get('event_name')
        if not v or not e:
            continue
        agg.setdefault(v, {}).setdefault(e, 0)
        agg[v][e] += 1

    variants_stats = []
    for v, counts in agg.items():
        shown = counts.get('shown', 0)
        cta = counts.get('cta_click', 0)
        ctr = (100.0 * cta / shown) if shown else 0.0
        variants_stats.append({'variant': v, 'shown': shown, 'cta_click': cta, 'ctr': round(ctr, 2)})

    if not variants_stats:
        return {'status': 'insufficient_data', 'variants': [], 'reason': 'aucun event'}

    # 3) Les variantes doivent toutes avoir >= MIN_SHOWN pour statistiquement comparer
    insufficient = [v for v in variants_stats if v['shown'] < MIN_SHOWN_PER_VARIANT]
    if insufficient:
        return {
            'status': 'insufficient_data',
            'variants': variants_stats,
            'reason': f'variantes avec <{MIN_SHOWN_PER_VARIANT} shown : {[v["variant"] for v in insufficient]}',
        }

    # 4) Trouver le gagnant
    variants_stats.sort(key=lambda x: x['ctr'], reverse=True)
    leader = variants_stats[0]
    runner_up = variants_stats[1] if len(variants_stats) > 1 else {'ctr': 0.0}
    if runner_up['ctr'] == 0:
        lift_pct = 100.0 if leader['ctr'] > 0 else 0.0
    else:
        lift_pct = 100.0 * (leader['ctr'] - runner_up['ctr']) / runner_up['ctr']

    if lift_pct < MIN_LIFT_PCT:
        return {
            'status': 'unclear_winner',
            'variants': variants_stats,
            'reason': f'lift leader={leader["variant"]} vs 2e seulement {lift_pct:.1f}% (<{MIN_LIFT_PCT}%)',
        }

    # 5) Verrouillage
    try:
        sb.table('experiment_locks').upsert({
            'experiment': experiment,
            'variant': leader['variant'],
            'locked_at': datetime.now(timezone.utc).isoformat(),
            'reason': f'auto · {leader["ctr"]}% CTR vs {runner_up["ctr"]}% ({lift_pct:+.1f}%)',
        }, on_conflict='experiment').execute()
        logger.warning(f'[exp_lock] 🔒 {experiment} → variante {leader["variant"]} verrouillée ({leader["ctr"]}% CTR)')
        return {
            'status': 'locked',
            'winner': leader['variant'],
            'variants': variants_stats,
            'lift_pct': round(lift_pct, 2),
            'reason': f'lift {lift_pct:+.1f}% vs 2e variante',
        }
    except Exception as e:
        msg = str(e)
        if 'experiment_locks' in msg and ('schema cache' in msg or 'does not exist' in msg):
            logger.warning('[exp_lock] Table experiment_locks absente — ne peut pas verrouiller.')
            return {
                'status': 'error',
                'variants': variants_stats,
                'reason': 'Table experiment_locks absente (exécuter migration).',
            }
        logger.warning(f'[exp_lock] lock insert failed: {msg[:200]}')
        return {'status': 'error', 'variants': variants_stats, 'reason': msg[:200]}


async def get_locked_variant(experiment: str) -> Optional[str]:
    """Retourne la variante verrouillée pour cette expérience, ou None."""
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        r = sb.table('experiment_locks').select('variant').eq('experiment', experiment).maybe_single().execute()
        if r and r.data:
            return r.data.get('variant')
    except Exception as e:
        msg = str(e)
        if 'experiment_locks' in msg and ('schema cache' in msg or 'does not exist' in msg):
            return None
        logger.warning(f'[exp_lock] get_locked_variant failed: {msg[:200]}')
    return None
