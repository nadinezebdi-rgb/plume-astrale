"""
Pexels Videos API service.

Search + download royalty-free stock footage for marketing videos.
Rate limit: 200 req/h, 20k req/month on free tier.
"""
from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

_API_KEY = os.environ.get("PEXELS_API_KEY", "").strip()
_BASE = "https://api.pexels.com"
_CACHE_DIR = BACKEND_DIR / "cache" / "pexels_stock"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _headers() -> dict:
    if not _API_KEY:
        raise RuntimeError("PEXELS_API_KEY missing from backend/.env")
    return {"Authorization": _API_KEY}


def search_videos(
    query: str,
    orientation: str = "portrait",
    size: str = "large",
    per_page: int = 15,
    page: int = 1,
) -> list[dict]:
    """
    Search Pexels for videos matching `query`.

    Returns a list of video dicts with fields: id, width, height, duration,
    video_files (list of {link, quality, width, height, file_type}).
    """
    url = f"{_BASE}/videos/search"
    params = {
        "query": query,
        "orientation": orientation,
        "size": size,
        "per_page": min(per_page, 80),
        "page": page,
    }
    r = requests.get(url, headers=_headers(), params=params, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"Pexels search failed [{r.status_code}]: {r.text[:200]}")

    remaining = r.headers.get("X-Ratelimit-Remaining")
    if remaining:
        logger.info(f"[pexels] rate limit remaining: {remaining}")

    return r.json().get("videos", [])


def _best_portrait_mp4(video: dict, max_height: int = 1920) -> Optional[dict]:
    """
    Pick the best MP4 file: prefer portrait, then largest resolution ≤ max_height.
    Returns dict with 'link', 'width', 'height', 'quality'.
    """
    files = [f for f in video.get("video_files", []) if f.get("file_type") == "video/mp4"]
    if not files:
        return None
    # portrait first, sorted by resolution descending but capped
    portrait = [f for f in files if (f.get("height") or 0) > (f.get("width") or 0)]
    candidates = portrait or files
    candidates = sorted(
        candidates,
        key=lambda f: abs((f.get("height") or 0) - max_height),
    )
    # prefer files whose height <= max_height + 500 (allow 4K then downscale)
    reasonable = [f for f in candidates if (f.get("height") or 0) <= max_height + 500]
    return (reasonable or candidates)[0]


def download_video(video: dict, max_height: int = 1920) -> Optional[Path]:
    """
    Download the best MP4 for a given video dict (from search_videos()).
    Cached by video ID. Returns local Path or None.
    """
    vid = video.get("id")
    if not vid:
        return None
    chosen = _best_portrait_mp4(video, max_height=max_height)
    if not chosen:
        logger.warning(f"[pexels] no MP4 file for video {vid}")
        return None

    dst = _CACHE_DIR / f"pexels_{vid}.mp4"
    if dst.exists() and dst.stat().st_size > 100_000:
        return dst

    logger.info(f"[pexels] downloading video {vid} "
                f"({chosen.get('width')}x{chosen.get('height')})...")
    try:
        with requests.get(chosen["link"], stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(dst, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
        logger.info(f"[pexels] saved {dst} ({dst.stat().st_size // 1024} KB)")
        return dst
    except Exception as e:
        logger.exception(f"[pexels] download failed for {vid}: {e}")
        if dst.exists():
            dst.unlink()
        return None


def get_first_video(query: str, min_duration: float = 4.0) -> Optional[dict]:
    """
    Convenience: return the first portrait video for `query` with duration
    ≥ min_duration. Fallback to any orientation if no portrait match.
    """
    for orientation in ("portrait", "landscape"):
        try:
            videos = search_videos(query, orientation=orientation, per_page=15)
        except Exception as e:
            logger.warning(f"[pexels] search error: {e}")
            continue
        # filter by duration
        good = [v for v in videos if (v.get("duration") or 0) >= min_duration]
        if good:
            return good[0]
        if videos:
            return videos[0]
    return None


def get_and_download(query: str, min_duration: float = 4.0) -> Optional[Path]:
    """Search + download in one call. Returns local path or None."""
    v = get_first_video(query, min_duration=min_duration)
    if not v:
        return None
    return download_video(v)
