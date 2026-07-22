"""
Marketing assets endpoints (TikTok / Reels vertical videos).

Public endpoints — generate + serve short vertical videos built from
existing luxury visuals (moon, zodiac, tarot, brand palette).
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from services.video_generator import (
    OUTPUT_DIR,
    generate_tiktok_video,
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
