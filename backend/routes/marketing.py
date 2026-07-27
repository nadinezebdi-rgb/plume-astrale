"""
Marketing assets endpoints (TikTok / Reels vertical videos).

Public endpoints — generate + serve short vertical videos built from
existing luxury visuals (moon, zodiac, tarot, brand palette).
"""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from services.video_generator import (
    OUTPUT_DIR,
    generate_hook_template_video,
    generate_tiktok_video,
    generate_tirage_video,
)

router = APIRouter()
logger = logging.getLogger(__name__)

DEFAULT_NAME = "plume_tiktok_decouverte.mp4"


@router.get("/marketing/tiktok")
async def get_tiktok_video(
    regenerate: bool = Query(False, description="Force regeneration"),
    preview: bool = Query(False, description="Faster 540x960 render"),
):
    """
    Return the 30s vertical TikTok video (1080x1920).

    - Generated once and cached in /app/backend/cache/marketing_videos/.
    - Pass ?regenerate=true to rebuild from scratch.
    - Pass ?preview=true for a lower-resolution fast render.
    """
    filename = "plume_tiktok_decouverte_preview.mp4" if preview else DEFAULT_NAME
    output_path: Path = OUTPUT_DIR / filename

    if regenerate or not output_path.exists() or output_path.stat().st_size < 100_000:
        try:
            output_path = generate_tiktok_video(
                output_filename=filename,
                preview=preview,
            )
        except Exception as e:
            logger.exception("[marketing] video generation failed")
            raise HTTPException(500, f"Video generation failed: {e}")

    return FileResponse(
        path=str(output_path),
        media_type="video/mp4",
        filename=filename,
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f'inline; filename="{filename}"',
        },
    )


@router.get("/marketing/tiktok/info")
async def get_tiktok_info():
    """Metadata about the current cached video."""
    path = OUTPUT_DIR / DEFAULT_NAME
    if not path.exists():
        return {"exists": False, "hint": "GET /api/marketing/tiktok to generate"}
    stat = path.stat()
    return {
        "exists": True,
        "filename": DEFAULT_NAME,
        "size_kb": stat.st_size // 1024,
        "generated_at": stat.st_mtime,
        "download_url": "/api/marketing/tiktok",
        "specs": {
            "resolution": "1080x1920",
            "duration_seconds": 30,
            "fps": 30,
            "codec": "H.264 / AAC",
        },
    }


@router.get("/marketing/tirage")
async def get_tirage_video(
    regenerate: bool = Query(False, description="Force regeneration"),
    mute: bool = Query(True, description="Silent MP4 (no music)"),
    preview: bool = Query(False, description="Faster 540x960 render"),
):
    """
    Return the "Tirage Gratuit" 30s vertical video (1080x1920).

    Storyboard: 3 card backs → spread Passé/Présent/Futur →
    flip reveal (Le Soleil, La Roue, L'Étoile) → CTA plume-astrale.fr.

    - mute=true (default) → silent — ready to add TikTok music on top.
    - Pass ?regenerate=true to rebuild.
    - Pass ?preview=true for a lower-resolution fast render.
    """
    suffix = "_muted" if mute else ""
    suffix += "_preview" if preview else ""
    filename = f"plume_tiktok_tirage_gratuit{suffix}.mp4"
    output_path: Path = OUTPUT_DIR / filename

    if regenerate or not output_path.exists() or output_path.stat().st_size < 100_000:
        try:
            output_path = generate_tirage_video(
                output_filename=filename,
                mute=mute,
                preview=preview,
            )
        except Exception as e:
            logger.exception("[marketing] tirage video generation failed")
            raise HTTPException(500, f"Video generation failed: {e}")

    return FileResponse(
        path=str(output_path),
        media_type="video/mp4",
        filename=filename,
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f'inline; filename="{filename}"',
        },
    )



# ---------------------------------------------------------------------------
# Hook Template — custom text video (kinetic typography)
# ---------------------------------------------------------------------------

class HookRequest(BaseModel):
    hook: str = Field(..., description="Big accroche (3-8 mots)")
    body: list[str] = Field(..., description="2-5 phrases courtes qui apportent la valeur")
    cta: str = Field("20 CRÉDITS OFFERTS", description="Phrase finale")
    bg: str = Field("moon", description="moon | starfield | zodiac-<sign> | tarot-<slug>")
    duration: float = Field(30.0, ge=10, le=60)
    mute: bool = Field(True, description="Silent — add TikTok music on top")


def _hook_cache_key(payload: dict) -> str:
    import json
    canon = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(canon.encode("utf-8")).hexdigest()[:12]


@router.post("/marketing/hook")
async def create_hook_video(payload: HookRequest = Body(...)):
    """Generate a custom kinetic-typography TikTok video."""
    key = _hook_cache_key(payload.model_dump())
    filename = f"plume_hook_{key}.mp4"
    output_path: Path = OUTPUT_DIR / filename

    if not output_path.exists() or output_path.stat().st_size < 100_000:
        try:
            output_path = generate_hook_template_video(
                hook=payload.hook,
                body=payload.body,
                cta=payload.cta,
                bg_type=payload.bg,
                duration=payload.duration,
                mute=payload.mute,
                output_filename=filename,
            )
        except Exception as e:
            logger.exception("[marketing] hook generation failed")
            raise HTTPException(500, f"Video generation failed: {e}")

    return FileResponse(
        path=str(output_path),
        media_type="video/mp4",
        filename=filename,
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f'inline; filename="{filename}"',
        },
    )


@router.get("/marketing/hook")
async def get_hook_video(
    hook: str = Query(..., min_length=3),
    body: str = Query(..., description="Body lines separated by | (pipe)"),
    cta: str = Query("20 CRÉDITS OFFERTS"),
    bg: str = Query("moon"),
    duration: float = Query(30.0, ge=10, le=60),
    mute: bool = Query(True),
):
    """Quick GET variant — body lines separated by `|`."""
    lines = [ln.strip() for ln in body.split("|") if ln.strip()]
    if not lines:
        raise HTTPException(400, "body must contain at least one non-empty line separated by |")
    payload = HookRequest(
        hook=hook, body=lines, cta=cta, bg=bg,
        duration=duration, mute=mute,
    )
    return await create_hook_video(payload)
