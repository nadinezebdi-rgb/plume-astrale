"""
Bibliotheque visuelle — service de generation via Gemini Nano Banana.

- Utilise emergentintegrations + EMERGENT_LLM_KEY
- Passe les 3 images de reference (crab, flowers, wheel) comme style anchor
- Sauve chaque image en 3 resolutions (2048, 1080, 512) sur disque
- Ecrit un manifest.json avec l'etat de la generation
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from PIL import Image
from dotenv import load_dotenv

from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

from services.library_prompts import ALL_ASSETS, STYLE_REF_FILES, get_asset

load_dotenv()
logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────
# Config
# ────────────────────────────────────────────────────────────────
LIBRARY_ROOT = Path("/app/backend/assets/library")
STYLE_REFS_DIR = LIBRARY_ROOT / "style-refs"
MANIFEST_PATH = LIBRARY_ROOT / "manifest.json"
MODEL_ID = "gemini-3.1-flash-image-preview"

RESOLUTIONS = {
    "hq": 2048,   # impression PDF
    "sq": 1080,   # cartes Instagram
    "web": 512,   # web / thumbnails
}


# ────────────────────────────────────────────────────────────────
# Manifest — etat de la bibliotheque
# ────────────────────────────────────────────────────────────────
def _load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"assets": {}, "runs": []}


def _save_manifest(m: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")


def get_manifest() -> dict:
    return _load_manifest()


# ────────────────────────────────────────────────────────────────
# Style anchor — charge les 3 images de reference en base64
# ────────────────────────────────────────────────────────────────
def _load_style_refs() -> list[ImageContent]:
    refs = []
    for fname in STYLE_REF_FILES:
        p = STYLE_REFS_DIR / fname
        if not p.exists():
            logger.warning(f"[library] missing style ref: {p}")
            continue
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        refs.append(ImageContent(b64))
    return refs


# ────────────────────────────────────────────────────────────────
# Generation d'un asset unique
# ────────────────────────────────────────────────────────────────
async def generate_one(slug: str, force: bool = False) -> dict:
    """Genere un seul asset et sauvegarde ses 3 resolutions."""
    asset = get_asset(slug)
    if not asset:
        raise ValueError(f"Unknown asset slug: {slug}")

    manifest = _load_manifest()
    existing = manifest["assets"].get(slug)
    if existing and existing.get("status") == "ok" and not force:
        logger.info(f"[library] {slug} already generated, skipping (use force=True to regen)")
        return existing

    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        raise RuntimeError("EMERGENT_LLM_KEY not set in environment")

    category_dir = LIBRARY_ROOT / asset["category"]
    category_dir.mkdir(parents=True, exist_ok=True)

    style_refs = _load_style_refs()
    session_id = f"lib-{slug}-{uuid.uuid4().hex[:6]}"

    chat = (
        LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=(
                "You are a master illustrator generating a coherent visual library "
                "of astrology art. Match the exact style of the provided reference "
                "images (deep navy, gold filigree, ornate mystical, painterly)."
            ),
        )
        .with_model("gemini", MODEL_ID)
        .with_params(modalities=["image", "text"])
    )

    msg = UserMessage(
        text=asset["prompt"],
        file_contents=style_refs if style_refs else None,
    )

    logger.info(f"[library] generating {slug} …")
    try:
        _, images = await chat.send_message_multimodal_response(msg)
    except Exception as e:
        logger.error(f"[library] {slug} generation failed: {e}")
        manifest["assets"][slug] = {
            "slug": slug,
            "category": asset["category"],
            "title": asset["title"],
            "status": "error",
            "error": str(e)[:400],
        }
        _save_manifest(manifest)
        return manifest["assets"][slug]

    if not images:
        manifest["assets"][slug] = {
            "slug": slug,
            "category": asset["category"],
            "title": asset["title"],
            "status": "error",
            "error": "no image returned by model",
        }
        _save_manifest(manifest)
        return manifest["assets"][slug]

    # Prend la premiere image, decode, sauvegarde en 3 tailles
    img_b64 = images[0]["data"]
    raw = base64.b64decode(img_b64)

    # Sauve original en HQ puis redimensionne
    hq_path = category_dir / f"{slug}_2048.png"
    hq_path.write_bytes(raw)

    with Image.open(hq_path) as im:
        im = im.convert("RGB")
        # HQ = tel quel (ou upscale si < 2048)
        if max(im.size) < RESOLUTIONS["hq"]:
            im.thumbnail((RESOLUTIONS["hq"], RESOLUTIONS["hq"]), Image.LANCZOS)
        else:
            im = im.resize((RESOLUTIONS["hq"], RESOLUTIONS["hq"]), Image.LANCZOS)
        im.save(hq_path, "PNG", optimize=True)

        # Version 1080
        sq_path = category_dir / f"{slug}_1080.png"
        im.resize((RESOLUTIONS["sq"], RESOLUTIONS["sq"]), Image.LANCZOS).save(
            sq_path, "PNG", optimize=True
        )

        # Version 512 (web)
        web_path = category_dir / f"{slug}_512.png"
        im.resize((RESOLUTIONS["web"], RESOLUTIONS["web"]), Image.LANCZOS).save(
            web_path, "PNG", optimize=True
        )

    entry = {
        "slug": slug,
        "category": asset["category"],
        "title": asset["title"],
        "status": "ok",
        "files": {
            "hq":  f"/api/library/file/{asset['category']}/{slug}_2048.png",
            "sq":  f"/api/library/file/{asset['category']}/{slug}_1080.png",
            "web": f"/api/library/file/{asset['category']}/{slug}_512.png",
        },
        "prompt": asset["prompt"][:200],
    }
    manifest["assets"][slug] = entry
    _save_manifest(manifest)
    logger.info(f"[library] {slug} OK")
    return entry


# ────────────────────────────────────────────────────────────────
# Batch — genere tout ce qui manque
# ────────────────────────────────────────────────────────────────
async def generate_batch(
    slugs: Optional[list[str]] = None,
    force: bool = False,
    on_progress=None,
) -> dict:
    """
    Genere tous les assets (ou une sous-liste).
    Traite en sequentiel pour eviter le rate limit Gemini.
    """
    targets = slugs if slugs else [a["slug"] for a in ALL_ASSETS]
    run_id = uuid.uuid4().hex[:8]
    logger.info(f"[library] batch run {run_id} — {len(targets)} asset(s)")

    manifest = _load_manifest()
    run_entry = {"run_id": run_id, "total": len(targets), "done": 0, "errors": 0}
    manifest.setdefault("runs", []).append(run_entry)
    _save_manifest(manifest)

    for i, slug in enumerate(targets):
        try:
            entry = await generate_one(slug, force=force)
            if entry.get("status") == "ok":
                run_entry["done"] += 1
            else:
                run_entry["errors"] += 1
        except Exception as e:
            logger.error(f"[library] batch {slug} fatal: {e}")
            run_entry["errors"] += 1

        # petit throttle pour respecter le rate limit
        await asyncio.sleep(1.0)

        # sauve l'avancement
        m = _load_manifest()
        m["runs"][-1] = run_entry
        _save_manifest(m)

        if on_progress:
            try:
                on_progress(i + 1, len(targets), slug)
            except Exception:
                pass

    logger.info(
        f"[library] batch run {run_id} done — {run_entry['done']} ok, "
        f"{run_entry['errors']} err"
    )
    return run_entry
