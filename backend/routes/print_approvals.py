"""Routes flow d'approbation 72h "Vous lisez avant qu'on imprime".

Chemin de la cliente :
    1. Reçoit email avec 2 boutons.
    2. Approuve → GET /r/approve/{token} (montré comme un lien direct 1-clic).
    3. Refuse → clique un lien "dire pourquoi ça ne va pas" → front /relecture/{refuse_token}
       → POST /api/print-approval/refuse/{refuse_token} avec raison optionnelle.

Chemin admin :
    - GET /api/admin/print-approvals — liste dossiers en cours (auth admin requise).

Le flow initial `create_print_approval(...)` est déclenché depuis le webhook Stripe
Édition Reliée (à câbler quand le produit sera activé dans Stripe).
"""
from __future__ import annotations
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from services.print_approval_service import (
    approve as approve_service,
    get_by_token,
    list_pending,
    refuse as refuse_service,
)

logger = logging.getLogger(__name__)

# Router monté sous /api (les routes admin y sont)
api_router = APIRouter(prefix='/print-approval', tags=['print-approval'])


# ── Modèles ────────────────────────────────────────────────────

class RefuseRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=1000)


# ── Route publique 1-clic (GET pour lien email) ────────────────

@api_router.get('/approve/{token}', response_class=HTMLResponse)
async def approve_via_link(token: str):
    """Lien 1-clic depuis l'email : approuve et affiche une page de confirmation."""
    result = await approve_service(token)
    if not result:
        return HTMLResponse(_error_page(
            title='Lien introuvable',
            message=(
                "Ce lien de relecture n'est pas valide ou a déjà été utilisé. "
                "Si vous pensez qu'il s'agit d'une erreur, écrivez-nous à "
                '<a href="mailto:contact@plume-astrale.fr" style="color:#D4AF37;">contact@plume-astrale.fr</a>.'
            ),
        ), status_code=404)

    already = result.get('already')
    return HTMLResponse(_success_page(
        title="Merci — nous lançons l'impression." if not already else "C'est déjà validé.",
        message=(
            "Votre livre part en fabrication maintenant. Comptez cinq jours ouvrés "
            "pour l'impression, la reliure et l'expédition. Vous recevrez un email "
            "avec le numéro de suivi dès qu'il quittera l'atelier."
            if not already
            else "Vous avez déjà approuvé ce livre. L'impression est en cours ou a été livrée."
        ),
    ))


# ── Routes API ─────────────────────────────────────────────────

@api_router.get('/{token}')
async def get_approval_by_token(token: str):
    """Renvoie les infos publiques d'un dossier (via refuse_token)."""
    row = get_by_token(token, kind='refuse')
    if not row:
        raise HTTPException(status_code=404, detail='Dossier introuvable.')
    return {
        'id': row['id'],
        'status': row['status'],
        'pdf_url': row['pdf_url'],
        'purchaser_first_name': row.get('purchaser_first_name'),
        'recipient_first_name': row.get('recipient_first_name'),
        'deadline_at': row['deadline_at'],
        'created_at': row['created_at'],
    }


@api_router.post('/refuse/{token}')
async def refuse_via_form(token: str, payload: RefuseRequest):
    """Refus explicite avec raison optionnelle (depuis la page /relecture/{token})."""
    result = await refuse_service(token, reason=payload.reason)
    if not result:
        raise HTTPException(status_code=404, detail='Dossier introuvable.')
    return {
        'success': True,
        'status': result.get('status'),
        'already': bool(result.get('already')),
    }


# ── Routes admin ───────────────────────────────────────────────
# À monter en amont dans server.py via api_router.include_router(admin_print_approvals_router)
admin_router = APIRouter(prefix='/admin', tags=['admin-print-approvals'])


@admin_router.get('/print-approvals')
async def admin_list_print_approvals(limit: int = 50):
    """Liste des dossiers de relecture (admin)."""
    limit = max(1, min(limit, 200))
    return {'items': list_pending(limit=limit), 'count_returned': None}


# ── HTML helpers ──────────────────────────────────────────────

def _page_wrap(inner: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Plume Astrale · Relecture</title>
<style>
  body {{ margin:0; font-family: Georgia, 'Cormorant Garamond', serif; background: #0C0918; color: #F0E6D3; min-height:100vh; display:flex; align-items:center; justify-content:center; padding: 40px 24px; }}
  .wrap {{ max-width: 560px; text-align:center; }}
  .eyebrow {{ font-family:'Cinzel', serif; font-size: 11px; letter-spacing: 0.32em; color:#D4AF37; text-transform:uppercase; margin: 0 0 18px; }}
  h1 {{ font-family:'Playfair Display', Georgia, serif; font-size: 32px; font-weight: 400; margin: 0 0 20px; color: #F5EEE0; line-height: 1.2; }}
  p {{ font-size: 17px; line-height: 1.7; margin: 0 0 16px; color: rgba(240,230,211,0.85); }}
  a.cta {{ display:inline-block; margin-top: 28px; padding: 14px 30px; background: linear-gradient(135deg,#D4AF37,#E8C766); color: #0F1A3C; text-decoration:none; font-family:'Cinzel',serif; font-size: 12px; letter-spacing:0.24em; text-transform:uppercase; border-radius:4px; font-weight:600; }}
  .sig {{ margin-top: 34px; font-style: italic; color: #E8C766; font-size: 18px; }}
</style></head>
<body><div class="wrap">{inner}</div></body></html>"""


def _success_page(*, title: str, message: str) -> str:
    return _page_wrap(f"""
        <p class="eyebrow">Plume Astrale · Édition Reliée</p>
        <h1>{title}</h1>
        <p>{message}</p>
        <a class="cta" href="https://plume-astrale.fr">RETOUR AU SANCTUAIRE</a>
        <p class="sig">— Nadine</p>
    """)


def _error_page(*, title: str, message: str) -> str:
    return _page_wrap(f"""
        <p class="eyebrow">Plume Astrale · Édition Reliée</p>
        <h1>{title}</h1>
        <p>{message}</p>
        <a class="cta" href="https://plume-astrale.fr">RETOUR AU SANCTUAIRE</a>
    """)
