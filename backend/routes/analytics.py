"""
Analytics — dashboard d'attribution des campagnes UTM.

Endpoint admin qui agrege les ventes et leads par source/campagne UTM.
Interroge Supabase directement (payment_transactions + oracle_leads).
"""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/analytics", tags=["analytics"])


async def require_admin(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization.split(None, 1)[1].strip()
    sb = get_admin_client()
    try:
        u = sb.auth.get_user(token)
        user = u.user if hasattr(u, "user") else u
        if not user:
            raise HTTPException(401, "Invalid token")
        prof = sb.table("profiles").select("is_admin").eq("id", user.id).limit(1).execute()
        if not prof.data or not prof.data[0].get("is_admin"):
            raise HTTPException(403, "Admin only")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(401, f"Auth failed: {e}")


def _tx_utm(tx: dict) -> dict:
    """Extrait le dict UTM d'une ligne payment_transactions."""
    meta = tx.get("metadata") or {}
    if isinstance(meta, dict):
        utm = meta.get("utm") or {}
        if isinstance(utm, dict) and utm:
            return utm
    return {}


def _lead_utm(lead: dict) -> dict:
    meta = lead.get("metadata") or {}
    if not isinstance(meta, dict):
        return {}
    return {
        "utm_source": lead.get("source"),
        "utm_medium": meta.get("medium"),
        "utm_campaign": meta.get("campaign"),
        "utm_content": meta.get("content"),
        "referrer": meta.get("referrer"),
    }


@router.get("/attribution", dependencies=[Depends(require_admin)])
async def attribution(days: int = Query(30, ge=1, le=365)):
    """Renvoie les KPI d'attribution sur `days` jours.

    Structure :
      - range: {from, to, days}
      - totals: {leads, purchases, revenue_cents}
      - by_campaign: [{campaign, source, leads, purchases, revenue_cents, cvr}]
      - by_source:   [{source, leads, purchases, revenue_cents}]
      - by_content:  [{content, campaign, purchases, revenue_cents}]  (A/B tests)
      - funnel: {captures, purchases, purchase_rate}
      - recent_purchases: [{email, amount, utm_source, utm_campaign, utm_content, created_at}]
    """
    sb = get_admin_client()
    since_dt = datetime.now(timezone.utc) - timedelta(days=days)
    since_iso = since_dt.isoformat()

    # ── Purchases (payment_transactions status paid) ─────────────────
    purchases = []
    try:
        r = (sb.table("payment_transactions")
             .select("session_id,user_email,pack_id,amount,currency,payment_status,credits_granted,metadata,created_at")
             .gte("created_at", since_iso)
             .order("created_at", desc=True)
             .limit(500)
             .execute())
        purchases = [row for row in (r.data or []) if row.get("payment_status") == "paid"]
    except Exception as e:
        logger.warning(f"[analytics] payment_transactions query failed: {e}")

    # ── Leads (oracle_leads) ─────────────────────────────────────────
    leads = []
    try:
        r = (sb.table("oracle_leads")
             .select("email,first_name,source,consent_marketing,metadata,created_at")
             .gte("created_at", since_iso)
             .order("created_at", desc=True)
             .limit(2000)
             .execute())
        leads = r.data or []
    except Exception as e:
        logger.warning(f"[analytics] oracle_leads query failed (table may not exist): {e}")

    # ── Agregations ──────────────────────────────────────────────────
    by_source_leads = defaultdict(int)
    for lead in leads:
        s = (lead.get("source") or "direct")[:40]
        by_source_leads[s] += 1

    by_campaign_stats = defaultdict(lambda: {"leads": 0, "purchases": 0, "revenue_cents": 0, "source": ""})
    by_source_stats = defaultdict(lambda: {"leads": 0, "purchases": 0, "revenue_cents": 0})
    by_content_stats = defaultdict(lambda: {"purchases": 0, "revenue_cents": 0, "campaign": "", "source": ""})

    # Compte les leads par (source, campaign)
    for lead in leads:
        u = _lead_utm(lead)
        src = (u.get("utm_source") or "direct")[:40]
        camp = (u.get("utm_campaign") or "unknown")[:40]
        by_source_stats[src]["leads"] += 1
        by_campaign_stats[(src, camp)]["leads"] += 1
        by_campaign_stats[(src, camp)]["source"] = src

    # Compte les achats + revenu
    total_revenue_cents = 0
    for tx in purchases:
        u = _tx_utm(tx)
        src = (u.get("utm_source") or "direct")[:40]
        camp = (u.get("utm_campaign") or "unknown")[:40]
        content = (u.get("utm_content") or "-")[:40]
        cents = int(round((tx.get("amount") or 0) * 100))
        total_revenue_cents += cents

        by_source_stats[src]["purchases"] += 1
        by_source_stats[src]["revenue_cents"] += cents

        by_campaign_stats[(src, camp)]["purchases"] += 1
        by_campaign_stats[(src, camp)]["revenue_cents"] += cents
        by_campaign_stats[(src, camp)]["source"] = src

        if content != "-":
            key = (src, camp, content)
            by_content_stats[key]["purchases"] += 1
            by_content_stats[key]["revenue_cents"] += cents
            by_content_stats[key]["campaign"] = camp
            by_content_stats[key]["source"] = src

    def _round(x, d=2):
        try:
            return round(x, d)
        except Exception:
            return x

    by_campaign = []
    for (src, camp), st in by_campaign_stats.items():
        cvr = (st["purchases"] / st["leads"] * 100) if st["leads"] else 0
        by_campaign.append({
            "source": src,
            "campaign": camp,
            "leads": st["leads"],
            "purchases": st["purchases"],
            "revenue_cents": st["revenue_cents"],
            "cvr": _round(cvr, 1),
        })
    by_campaign.sort(key=lambda x: (-x["revenue_cents"], -x["purchases"], -x["leads"]))

    by_source = []
    for src, st in by_source_stats.items():
        cvr = (st["purchases"] / st["leads"] * 100) if st["leads"] else 0
        by_source.append({
            "source": src,
            "leads": st["leads"],
            "purchases": st["purchases"],
            "revenue_cents": st["revenue_cents"],
            "cvr": _round(cvr, 1),
        })
    by_source.sort(key=lambda x: -x["revenue_cents"])

    by_content = []
    for (src, camp, content), st in by_content_stats.items():
        by_content.append({
            "source": src,
            "campaign": camp,
            "content": content,
            "purchases": st["purchases"],
            "revenue_cents": st["revenue_cents"],
        })
    by_content.sort(key=lambda x: -x["revenue_cents"])

    total_leads = len(leads)
    total_purchases = len(purchases)
    purchase_rate = (total_purchases / total_leads * 100) if total_leads else 0

    recent = []
    for tx in purchases[:20]:
        u = _tx_utm(tx)
        recent.append({
            "email": tx.get("user_email"),
            "amount": tx.get("amount"),
            "currency": tx.get("currency"),
            "pack_id": tx.get("pack_id"),
            "utm_source": u.get("utm_source"),
            "utm_campaign": u.get("utm_campaign"),
            "utm_content": u.get("utm_content"),
            "created_at": tx.get("created_at"),
        })

    return {
        "range": {
            "from": since_iso,
            "to": datetime.now(timezone.utc).isoformat(),
            "days": days,
        },
        "totals": {
            "leads": total_leads,
            "purchases": total_purchases,
            "revenue_cents": total_revenue_cents,
            "revenue_eur": _round(total_revenue_cents / 100, 2),
        },
        "funnel": {
            "leads": total_leads,
            "purchases": total_purchases,
            "purchase_rate": _round(purchase_rate, 1),
        },
        "by_campaign": by_campaign[:20],
        "by_source": by_source[:10],
        "by_content": by_content[:10],
        "recent_purchases": recent,
    }
