"""
Sora 2 (OpenAI Videos API) service via Emergent LLM Key.

Async flow:
  1. POST /v1/videos → returns { id, status: 'queued' }
  2. Poll GET /v1/videos/{id} until status == 'completed' (or 'failed')
  3. GET /v1/videos/{id}/content → MP4 bytes (temp URL, download quickly)

Pricing (Feb 2026): sora-2 $0.10/s, sora-2-pro $0.30/s.
Deprecation: 2026-09-24 per OpenAI docs.
"""
from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Literal, Optional

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

_BASE = os.environ.get("SORA_BASE_URL", "https://api.openai.com").rstrip("/")
_CACHE_DIR = BACKEND_DIR / "cache" / "sora_videos"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _resolve_key() -> str:
    """
    Prefer OPENAI_API_KEY (direct account access) if present, else fallback
    to EMERGENT_LLM_KEY. Sora 2 requires an OpenAI-compatible key.
    """
    k = os.environ.get("OPENAI_API_KEY", "").strip()
    if k:
        return k
    return os.environ.get("EMERGENT_LLM_KEY", "").strip()


def _headers() -> dict:
    k = _resolve_key()
    if not k:
        raise RuntimeError("No OPENAI_API_KEY / EMERGENT_LLM_KEY available")
    return {"Authorization": f"Bearer {k}"}


def create_video(
    prompt: str,
    model: Literal["sora-2", "sora-2-pro"] = "sora-2-pro",
    size: str = "1080x1920",
    seconds: int | str = 4,
) -> dict:
    """Create a Sora video generation job. Returns job dict with 'id'."""
    files = {
        "model": (None, model),
        "prompt": (None, prompt),
        "size": (None, size),
        "seconds": (None, str(seconds)),
    }
    logger.info(f"[sora] creating job: model={model} size={size} seconds={seconds}")
    r = requests.post(f"{_BASE}/v1/videos", headers=_headers(),
                      files=files, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"Sora create failed [{r.status_code}]: {r.text[:500]}")
    return r.json()


def get_video(video_id: str) -> dict:
    """Poll a job status."""
    r = requests.get(f"{_BASE}/v1/videos/{video_id}",
                     headers=_headers(), timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Sora get failed [{r.status_code}]: {r.text[:500]}")
    return r.json()


def download_content(video_id: str, dst_path: Path) -> Path:
    """Download the completed video content to `dst_path`."""
    r = requests.get(f"{_BASE}/v1/videos/{video_id}/content",
                     headers=_headers(), timeout=180, stream=True)
    if r.status_code >= 400:
        raise RuntimeError(f"Sora download failed [{r.status_code}]: {r.text[:500]}")
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 64):
            if chunk:
                f.write(chunk)
    return dst_path


def generate_video_sync(
    prompt: str,
    output_path: Path | None = None,
    model: Literal["sora-2", "sora-2-pro"] = "sora-2-pro",
    size: str = "1080x1920",
    seconds: int = 4,
    poll_interval: float = 8.0,
    max_wait_seconds: float = 600.0,
) -> Path:
    """
    Blocking helper: create job, poll until completed, download.
    Returns local Path to the MP4.
    """
    job = create_video(prompt, model=model, size=size, seconds=seconds)
    video_id = job["id"]
    logger.info(f"[sora] job {video_id} status={job.get('status')}")

    start = time.time()
    while True:
        if time.time() - start > max_wait_seconds:
            raise TimeoutError(f"Sora job {video_id} timed out after {max_wait_seconds}s")
        time.sleep(poll_interval)
        info = get_video(video_id)
        status = info.get("status")
        progress = info.get("progress")
        logger.info(f"[sora] {video_id} status={status} progress={progress}")
        if status == "completed":
            break
        if status in ("failed", "canceled", "error"):
            err = info.get("error") or info
            raise RuntimeError(f"Sora job {video_id} failed: {err}")

    dst = output_path or (_CACHE_DIR / f"sora_{video_id}.mp4")
    download_content(video_id, dst)
    logger.info(f"[sora] saved {dst} ({dst.stat().st_size // 1024} KB)")
    # Enregistre le coût dans la jauge admin (usage sora_2 ou sora_2_pro).
    try:
        from services.app_settings import record_llm_call
        usage_key = 'sora_2_pro' if model == 'sora-2-pro' else 'sora_2'
        record_llm_call(usage_key, tokens_estimate=0, units=float(seconds))
    except Exception:
        pass
    return dst


CACHE_DIR = _CACHE_DIR
