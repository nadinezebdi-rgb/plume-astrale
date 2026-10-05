"""Experience Funnel — Dashboard A/B custom (Feb 2026)

Objectif business (analyse investisseur) :
  Mesurer en temps réel si /experience convertit mieux que la homepage,
  et quel est le CA / visiteur — pour piloter le budget publicitaire.

Architecture :
  - POST /api/experience/funnel-event   : ingestion publique (front → Mongo)
  - GET  /api/admin/experience/funnel   : agrégation admin (dashboard widget)

Collection Mongo : `experience_funnel_events`
  {
    visitor_id, event_name, variant, session_id, intent_type, card,
    utm_source, utm_campaign, amount_eur, transaction_id, path, created_at
  }

Anti-doublons :
  - purchase : unique index (visitor_id, transaction_id) → 1 entry / achat
  - autres events : pas de dédup natif (le front gère la dédup côté client
    via sessionStorage pour signup_started, feather_completed, etc.)

RGPD :
  - Aucun email / nom / token n'est stocké — seulement des identifiants
    anonymes (visitor_id = crypto.randomUUID() côté client)
  - Le visitor_id peut être purgé par l'utilisateur en vidant localStorage
  - Rétention à définir (recommandé : 90 jours) — pas encore implémenté
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from motor.motor_asyncio import AsyncIOMotorClient
from routes.admin import require_admin

logger = logging.getLogger(__name__)


# ─── MongoDB accessor ─────────────────────────────────────────────────
_client: Optional[AsyncIOMotorClient] = None


def _get_db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return _client[os.environ['DB_NAME']]


async def _ensure_indexes():
    """Idempotent — crée les indexes au démarrage / premier appel."""
    db = _get_db()
    col = db.experience_funnel_events
    try:
        # Dédup native purchase : un même visitor_id ne peut pas insérer
        # 2 fois le même transaction_id (refresh page success → 1 event).
        await col.create_index(
            [('visitor_id', 1), ('transaction_id', 1)],
            unique=True,
            partialFilterExpression={'transaction_id': {'$type': 'string'}},
            name='uniq_visitor_txn',
        )
        # Query patterns : agrégation par période + variant + event
        await col.create_index([('created_at', -1), ('variant', 1)], name='by_time_variant')
        await col.create_index([('created_at', -1), ('event_name', 1)], name='by_time_event')
    except Exception as e:
        logger.warning(f'[funnel] index creation warning: {e}')


# ─── Events acceptés (whitelist) ──────────────────────────────────────
# Seuls ces events sont autorisés en ingestion pour éviter le flood + noise.
ALLOWED_EVENTS = frozenset({
    # Étapes visite/qualification
    'experience_visit',        # arrivée sur / ou /experience (per variant)
    'intent_selected',
    'tarot_card_selected',
    'tarot_continue_clicked',
    'feather_completed',
    # Signup
    'signup_started',
    'signup_completed',
    # Conversion
    'credit_purchase',         # exige amount_eur + transaction_id
})

# Variants autorisés (bloque le noise 'test', 'foo', etc.)
ALLOWED_VARIANTS = frozenset({'homepage', 'experience', 'direct', 'unknown'})


# ─── Ingestion route (public, no auth) ────────────────────────────────
class FunnelEventIn(BaseModel):
    event_name: str = Field(..., min_length=3, max_length=64)
    visitor_id: str = Field(..., min_length=6, max_length=64)
    variant: str = Field(default='unknown', max_length=16)
    session_id: Optional[str] = Field(default=None, max_length=64)
    intent_type: Optional[str] = Field(default=None, max_length=32)
    card: Optional[str] = Field(default=None, max_length=32)
    utm_source: Optional[str] = Field(default=None, max_length=64)
    utm_campaign: Optional[str] = Field(default=None, max_length=64)
    amount_eur: Optional[float] = Field(default=None, ge=0, le=10000)
    transaction_id: Optional[str] = Field(default=None, max_length=128)
    path: Optional[str] = Field(default=None, max_length=256)


funnel_router = APIRouter(prefix='/experience', tags=['experience-funnel'])


@funnel_router.post('/funnel-event', status_code=204)
async def ingest_funnel_event(payload: FunnelEventIn, _req: Request):
    """Ingestion event → MongoDB. Silent 204 (pas de contenu).
    RGPD : aucune PII acceptée dans le payload — enforced via whitelist.
    """
    if payload.event_name not in ALLOWED_EVENTS:
        # Silencieux : on ne veut pas signaler à un potentiel abuseur
        # quels events sont acceptés. Log côté serveur pour debug.
        logger.info(f'[funnel] rejected event_name={payload.event_name}')
        return
    variant = payload.variant if payload.variant in ALLOWED_VARIANTS else 'unknown'

    # Contrainte purchase : exige amount + transaction_id sinon on refuse
    if payload.event_name == 'credit_purchase':
        if not payload.amount_eur or not payload.transaction_id:
            logger.info('[funnel] rejected purchase without amount+transaction_id')
            return

    doc = {
        'visitor_id': payload.visitor_id,
        'event_name': payload.event_name,
        'variant': variant,
        'session_id': payload.session_id,
        'intent_type': payload.intent_type,
        'card': payload.card,
        'utm_source': (payload.utm_source or '')[:64] or None,
        'utm_campaign': (payload.utm_campaign or '')[:64] or None,
        'amount_eur': payload.amount_eur,
        'transaction_id': payload.transaction_id,
        'path': payload.path,
        'created_at': datetime.now(timezone.utc),
    }
    db = _get_db()
    try:
        await db.experience_funnel_events.insert_one(doc)
    except Exception as e:
        # Doublon purchase (unique index) → OK, silent
        if 'duplicate key' in str(e).lower() or 'E11000' in str(e):
            return
        logger.warning(f'[funnel] insert failed: {e}')


# ─── Aggregation route (admin) ────────────────────────────────────────
admin_funnel_router = APIRouter(prefix='/admin/experience', tags=['admin-experience'])


# Ordre des étapes du funnel (pour l'affichage table)
FUNNEL_STEPS: List[str] = [
    'experience_visit',
    'intent_selected',
    'tarot_card_selected',
    'tarot_continue_clicked',
    'feather_completed',
    'signup_started',
    'signup_completed',
    'credit_purchase',
]


@admin_funnel_router.get('/funnel')
async def admin_experience_funnel(
    hours: int = 168,   # default = 7 jours
    _admin: dict = Depends(require_admin),
) -> Dict[str, Any]:
    """Agrège le funnel A/B homepage vs experience sur les N dernières heures.

    Retourne les compteurs uniques par visitor_id à chaque étape, le revenu
    total et le CA / visiteur — les 2 KPI qui pilotent le ROI publicitaire.
    """
    await _ensure_indexes()
    hours = max(1, min(hours, 24 * 90))  # cap 90 jours
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    db = _get_db()
    col = db.experience_funnel_events

    # Une agrégation par (variant, event_name) → nombre de visitors uniques
    pipeline = [
        {'$match': {'created_at': {'$gte': cutoff}}},
        {'$group': {
            '_id': {'variant': '$variant', 'event': '$event_name'},
            'visitors': {'$addToSet': '$visitor_id'},
            'revenue': {'$sum': {'$ifNull': ['$amount_eur', 0]}},
        }},
        {'$project': {
            'variant': '$_id.variant',
            'event': '$_id.event',
            'visitor_count': {'$size': '$visitors'},
            'revenue': 1,
        }},
    ]
    rows = await col.aggregate(pipeline).to_list(length=200)

    # Assemble le résultat par variant
    variants: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        v = row['variant']
        if v not in variants:
            variants[v] = {
                'steps': {step: 0 for step in FUNNEL_STEPS},
                'revenue_eur': 0.0,
            }
        variants[v]['steps'][row['event']] = row['visitor_count']
        variants[v]['revenue_eur'] += float(row.get('revenue') or 0)

    # Calcule CA / visiteur pour chaque variant
    for v, data in variants.items():
        visits = data['steps'].get('experience_visit', 0) or 0
        data['visitors'] = visits
        data['revenue_per_visitor_eur'] = (
            round(data['revenue_eur'] / visits, 4) if visits else 0.0
        )
        # Taux d'inscription et taux d'achat (KPI dérivés)
        signups = data['steps'].get('signup_completed', 0)
        purchases = data['steps'].get('credit_purchase', 0)
        data['signup_rate'] = round(signups / visits, 4) if visits else 0.0
        data['purchase_rate'] = round(purchases / visits, 4) if visits else 0.0

    return {
        'period_hours': hours,
        'from': cutoff.isoformat(),
        'to': datetime.now(timezone.utc).isoformat(),
        'variants': variants,
        'funnel_steps': FUNNEL_STEPS,
    }
