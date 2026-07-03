"""
Bibliotheque visuelle — API routes.

Endpoints (admin uniquement) :
  POST   /api/library/generate         → lance la generation en background
  POST   /api/library/generate/{slug}  → regenere UN asset (force)
  GET    /api/library/status           → etat manifest + progression
  GET    /api/library/catalog          → catalogue theorique (56 assets)
  GET    /api/library/file/{cat}/{f}   → serveur statique des PNG/SVG
  POST   /api/library/glyphs-svg       → (re)genere les 22 SVG glyphes
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Header
from fastapi.responses import FileResponse

from services.library_generator import (
    LIBRARY_ROOT,
    generate_batch,
    generate_one,
    get_manifest,
)
from services.library_prompts import ALL_ASSETS, list_by_category
from services.library_svg_glyphs import generate_all_svg
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/library", tags=["library"])


# ─────────────────────────────────────────────────────────────
# Verif admin (via bearer supabase JWT + flag is_admin)
# ─────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────
@router.get("/catalog")
async def catalog():
    """Renvoie le catalogue theorique (56 assets prevus)."""
    return {
        "total": len(ALL_ASSETS),
        "by_category": {
            "signs":   len(list_by_category("signs")),
            "planets": len(list_by_category("planets")),
            "houses":  len(list_by_category("houses")),
            "tarot":   len(list_by_category("tarot")),
        },
        "assets": [
            {"slug": a["slug"], "category": a["category"], "title": a["title"]}
            for a in ALL_ASSETS
        ],
    }


@router.get("/status")
async def status():
    """Renvoie le manifest complet (etat de chaque asset)."""
    m = get_manifest()
    done = sum(1 for a in m["assets"].values() if a.get("status") == "ok")
    errors = sum(1 for a in m["assets"].values() if a.get("status") == "error")
    return {
        "total_planned": len(ALL_ASSETS),
        "done": done,
        "errors": errors,
        "pending": len(ALL_ASSETS) - done - errors,
        "assets": m["assets"],
        "runs": m.get("runs", [])[-3:],
    }


@router.post("/generate", dependencies=[Depends(require_admin)])
async def start_batch(
    background: BackgroundTasks,
    category: Optional[str] = None,
    force: bool = False,
):
    """Lance la generation en background. Si category est fournie, ne genere que celle-ci."""
    slugs = None
    if category:
        slugs = [a["slug"] for a in list_by_category(category)]
        if not slugs:
            raise HTTPException(400, f"Unknown category: {category}")

    async def _run():
        try:
            await generate_batch(slugs=slugs, force=force)
        except Exception as e:
            logger.exception(f"[library] batch failed: {e}")

    background.add_task(lambda: asyncio.run(_run()))
    return {
        "status": "started",
        "count": len(slugs) if slugs else len(ALL_ASSETS),
        "force": force,
        "category": category,
    }


@router.post("/generate/{slug}", dependencies=[Depends(require_admin)])
async def regenerate_one(slug: str):
    """Regenere immediatement un seul asset (force=True)."""
    try:
        entry = await generate_one(slug, force=True)
        return entry
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.exception(f"[library] regen {slug} failed")
        raise HTTPException(500, str(e))


@router.post("/glyphs-svg", dependencies=[Depends(require_admin)])
async def regen_glyphs():
    """(Re)genere les 22 SVG glyphes."""
    idx = generate_all_svg()
    return {"generated": len(idx), "items": idx}


@router.get("/file/{category}/{filename}")
async def serve_file(category: str, filename: str):
    """Serveur statique des assets (PNG + SVG). Public en lecture."""
    if category not in {"signs", "planets", "houses", "tarot", "glyphs-svg", "style-refs"}:
        raise HTTPException(404, "Unknown category")
    # empeche path traversal
    fname = Path(filename).name
    p = LIBRARY_ROOT / category / fname
    if not p.exists() or not p.is_file():
        raise HTTPException(404, "File not found")
    media_type = "image/svg+xml" if fname.endswith(".svg") else "image/png"
    return FileResponse(p, media_type=media_type)
