"""OpenAI TTS via Emergent LLM Key — voix off française pour la démo.

Voix conseillées (français) :
- nova : mature, chaude, 30-40 ans (recommandée pour Soléna)
- shimmer : plus jeune, brillante
- alloy : neutre, journalistique
- fable : conteuse, expressive

Coût : $15 par million de caractères (tts-1) ou $30/M (tts-1-hd).
Tracké dans app_settings.record_llm_call('tts', units=nb_chars).
"""
from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Literal
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND_DIR / ".env")

_BASE = os.environ.get("SORA_BASE_URL", "https://api.openai.com").rstrip("/")
_CACHE_DIR = _BACKEND_DIR / "cache" / "tts"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _resolve_key() -> str:
    k = os.environ.get("OPENAI_API_KEY", "").strip()
    if k:
        return k
    return os.environ.get("EMERGENT_LLM_KEY", "").strip()


def _headers() -> dict:
    key = _resolve_key()
    if not key:
        raise RuntimeError("No OPENAI_API_KEY / EMERGENT_LLM_KEY available")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def synthesize(
    text: str,
    voice: Literal["nova", "shimmer", "alloy", "fable", "onyx", "echo"] = "nova",
    model: Literal["tts-1", "tts-1-hd"] = "tts-1-hd",
    output_path: Path | None = None,
    speed: float = 0.95,
) -> Path:
    """Synthesize French speech and save to MP3. Returns Path."""
    if not text or not text.strip():
        raise ValueError("Empty TTS text")
    payload = {
        "model": model,
        "voice": voice,
        "input": text.strip(),
        "speed": max(0.25, min(4.0, speed)),
    }
    logger.info(f"[tts] {model}/{voice} → {len(text)} chars")
    r = requests.post(f"{_BASE}/v1/audio/speech",
                      headers=_headers(), json=payload, timeout=180)
    if r.status_code >= 400:
        raise RuntimeError(f"TTS failed [{r.status_code}]: {r.text[:400]}")
    dst = output_path or (_CACHE_DIR / f"tts_{abs(hash(text)) % 10**9}.mp3")
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 32):
            if chunk:
                f.write(chunk)
    # Track cost
    try:
        from services.app_settings import record_llm_call
        record_llm_call("tts", units=float(len(text)))
    except Exception:
        pass
    return dst
