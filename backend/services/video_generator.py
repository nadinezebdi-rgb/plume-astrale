"""
TikTok Video Generator for Plume Astrale.

Generates a 30s vertical (1080x1920) marketing video composed of:
  - Scene 1 (0-6s):  Hook mystique with tagline
  - Scene 2 (6-15s): Aperçu Thème Natal (zodiac signs carousel)
  - Scene 3 (15-24s): Aperçu Tarot (3 major arcana flipping)
  - Scene 4 (24-30s): CTA "20 crédits offerts"

Uses MoviePy + FFmpeg. Text is pre-rendered via PIL (no ImageMagick needed).
Ambient music track is procedurally synthesized with FFmpeg.
"""

from __future__ import annotations

import logging
import math
import os
import random
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

import numpy as np
import requests
from dotenv import load_dotenv
from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    VideoClip,
    concatenate_videoclips,
)
from PIL import Image, ImageDraw, ImageFilter, ImageFont

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BACKEND_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
LIB_DIR = ASSETS_DIR / "library"
OUTPUT_DIR = BACKEND_DIR / "cache" / "marketing_videos"
TAROT_CACHE_DIR = BACKEND_DIR / "cache" / "tarot_downloads"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TAROT_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Ensure Supabase env is loaded even when running standalone
load_dotenv(BACKEND_DIR / ".env")

W, H = 1080, 1920
FPS = 30
DURATION = 30

# Palette (deep plum / gold luxury)
BG_DEEP = (12, 8, 26)
BG_MID = (28, 18, 52)
GOLD = (212, 176, 96)
GOLD_LIGHT = (240, 214, 155)
IVORY = (242, 235, 220)
STAR_WHITE = (255, 250, 235)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")


def _tarot_cdn() -> str | None:
    """Resolve Supabase CDN base at call-time (env may load after import)."""
    base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    return f"{base}/storage/v1/object/public/library/tarot" if base else None

FONT_TITLE = str(FONTS_DIR / "Cinzel-Bold.ttf")
FONT_SUB = str(FONTS_DIR / "CormorantGaramond-Italic.ttf")
FONT_BODY = str(FONTS_DIR / "CormorantGaramond-Regular.ttf")


# ---------------------------------------------------------------------------
# Background & particles
# ---------------------------------------------------------------------------

def _cosmic_background(seed: int = 7) -> Image.Image:
    """Deep plum radial gradient with soft stars."""
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H), BG_DEEP)
    px = img.load()
    cx, cy = W / 2, H * 0.45
    max_d = math.hypot(cx, cy) * 1.1
    for y in range(H):
        for x in range(0, W, 2):  # step 2 to save time
            d = math.hypot(x - cx, y - cy) / max_d
            t = max(0.0, 1.0 - d)
            r = int(BG_DEEP[0] + (BG_MID[0] - BG_DEEP[0]) * t)
            g = int(BG_DEEP[1] + (BG_MID[1] - BG_DEEP[1]) * t)
            b = int(BG_DEEP[2] + (BG_MID[2] - BG_DEEP[2]) * t)
            px[x, y] = (r, g, b)
            if x + 1 < W:
                px[x + 1, y] = (r, g, b)
    # stars
    draw = ImageDraw.Draw(img)
    for _ in range(220):
        sx, sy = rnd.randint(0, W - 1), rnd.randint(0, H - 1)
        s = rnd.choice([1, 1, 1, 2, 2, 3])
        alpha = rnd.randint(120, 255)
        draw.ellipse((sx - s, sy - s, sx + s, sy + s),
                     fill=(STAR_WHITE[0], STAR_WHITE[1], STAR_WHITE[2]))
        _ = alpha
    return img.filter(ImageFilter.GaussianBlur(0.3))


def _sparkle_layer(seed: int = 11, count: int = 60) -> Image.Image:
    """Transparent PNG with golden sparkles for overlay."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for _ in range(count):
        x, y = rnd.randint(40, W - 40), rnd.randint(40, H - 40)
        r = rnd.choice([2, 3, 3, 4, 5])
        col = GOLD_LIGHT if rnd.random() < 0.5 else STAR_WHITE
        draw.ellipse((x - r, y - r, x + r, y + r),
                     fill=(col[0], col[1], col[2], 220))
    return img.filter(ImageFilter.GaussianBlur(0.8))


# ---------------------------------------------------------------------------
# Text rendering (PIL -> RGBA numpy array)
# ---------------------------------------------------------------------------

def _draw_star_ornament(size: int, color: tuple[int, int, int] = GOLD_LIGHT) -> Image.Image:
    """4-branch elongated star (fleur-de-lys style ✦) drawn programmatically."""
    s = size
    img = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = s
    # 4-point star via two elongated diamonds
    a = int(s * 0.9)   # long axis
    b = int(s * 0.18)  # short axis
    # vertical diamond
    d.polygon([(cx, cy - a), (cx + b, cy), (cx, cy + a), (cx - b, cy)],
              fill=(color[0], color[1], color[2], 255))
    # horizontal diamond
    d.polygon([(cx - a, cy), (cx, cy - b), (cx + a, cy), (cx, cy + b)],
              fill=(color[0], color[1], color[2], 255))
    # 4 small diagonal accents
    ad = int(s * 0.35)
    for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        d.ellipse((cx + dx * ad - 6, cy + dy * ad - 6,
                   cx + dx * ad + 6, cy + dy * ad + 6),
                  fill=(color[0], color[1], color[2], 220))
    # inner glow via blur composite
    glow = img.filter(ImageFilter.GaussianBlur(6))
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out = Image.alpha_composite(out, glow)
    out = Image.alpha_composite(out, img)
    return out


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.getlength(test) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _render_text(
    text: str,
    font_path: str,
    size: int,
    color: tuple[int, int, int] = IVORY,
    max_w: int = 900,
    line_spacing: float = 1.15,
    glow: bool = True,
    letter_spacing: int = 0,
    align: str = "center",
) -> Image.Image:
    font = ImageFont.truetype(font_path, size)
    lines = _wrap_text(text, font, max_w)
    # measure
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    total_h = line_h * len(lines) + 40
    max_line_w = int(max((font.getlength(l) for l in lines), default=0)) + max(80, letter_spacing * 6)
    canvas_w = min(W, max(300, max_line_w + 80))
    img = Image.new("RGBA", (canvas_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    y = 20
    for line in lines:
        if letter_spacing > 0:
            widths = [font.getlength(ch) for ch in line]
            total_w = sum(widths) + letter_spacing * max(0, len(line) - 1)
        else:
            total_w = font.getlength(line)
        if align == "center":
            x = (canvas_w - total_w) / 2
        elif align == "left":
            x = 20
        else:
            x = canvas_w - total_w - 20
        if letter_spacing > 0:
            cx = x
            for i, ch in enumerate(line):
                draw.text((cx, y), ch, font=font, fill=color)
                cx += widths[i] + letter_spacing
        else:
            draw.text((x, y), line, font=font, fill=color)
        y += line_h
    if glow:
        glow_img = img.filter(ImageFilter.GaussianBlur(6))
        out = Image.new("RGBA", img.size, (0, 0, 0, 0))
        out = Image.alpha_composite(out, glow_img)
        out = Image.alpha_composite(out, img)
        return out
    return img


def _pil_to_clip(img: Image.Image, duration: float) -> ImageClip:
    arr = np.array(img.convert("RGBA"))
    return ImageClip(arr, transparent=True, duration=duration)


# ---------------------------------------------------------------------------
# Asset loading
# ---------------------------------------------------------------------------

def _load_local_image(path: Path, size: tuple[int, int] | None = None) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    if size:
        img.thumbnail(size, Image.LANCZOS)
    return img


def _download_tarot(card_filename: str) -> Path | None:
    """Download from Supabase public storage (cached)."""
    local = TAROT_CACHE_DIR / card_filename
    if local.exists() and local.stat().st_size > 1000:
        return local
    # Try local library first
    local_lib = LIB_DIR / "tarot" / card_filename
    if local_lib.exists():
        shutil.copy(local_lib, local)
        return local
    if not local_lib.exists() and not _tarot_cdn():
        return None
    cdn = _tarot_cdn()
    if not cdn:
        return None
    url = f"{cdn}/{card_filename}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        local.write_bytes(r.content)
        return local
    except Exception as e:
        logger.warning(f"[video] tarot download failed {card_filename}: {e}")
        return None


# ---------------------------------------------------------------------------
# Ambient music (procedural)
# ---------------------------------------------------------------------------

def _generate_ambient_track(out_path: Path, duration: float = DURATION) -> Path:
    """
    Create a soft mystical ambient pad using FFmpeg's synth filters.
    Layered sine drones + subtle chorus + reverb-like delay for depth.
    Fade in/out. Royalty-free (procedural).
    """
    # Chord: A minor (A2 + C3 + E3 + A3) — 220Hz base
    freqs = [110.0, 164.81, 220.0, 329.63]  # A2, E3, A3, E4
    inputs: list[str] = []
    filter_parts: list[str] = []
    for i, f in enumerate(freqs):
        inputs += ["-f", "lavfi", "-i", f"sine=frequency={f}:duration={duration}"]
        # gentle LFO tremolo variance
        filter_parts.append(f"[{i}:a]volume=0.18,tremolo=f=0.{i+2}:d=0.15[a{i}]")
    mix_inputs = "".join(f"[a{i}]" for i in range(len(freqs)))
    filter_complex = ";".join(filter_parts) + (
        f";{mix_inputs}amix=inputs={len(freqs)}:normalize=0[mix]"
        f";[mix]aecho=0.8:0.88:60|120:0.4|0.3,highpass=f=80,lowpass=f=2200"
        f",afade=t=in:st=0:d=1.5,afade=t=out:st={duration-2}:d=2[out]"
    )
    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-t", f"{duration}",
        "-ac", "2", "-ar", "44100", "-b:a", "192k",
        str(out_path),
    ]
    logger.info("[video] synthesizing ambient track...")
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path


# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------

def _paste_center(bg: Image.Image, fg: Image.Image, cx: int, cy: int,
                  scale: float = 1.0) -> Image.Image:
    """Return bg with fg pasted centered at (cx, cy), scaled."""
    out = bg.copy()
    if scale != 1.0:
        nw = max(1, int(fg.width * scale))
        nh = max(1, int(fg.height * scale))
        fg = fg.resize((nw, nh), Image.LANCZOS)
    out.paste(fg, (cx - fg.width // 2, cy - fg.height // 2), fg)
    return out


def _make_base_frames(bg: Image.Image) -> np.ndarray:
    return np.array(bg.convert("RGB"))


def _scene_hook(duration: float, bg_arr: np.ndarray) -> VideoClip:
    """Scene 1: cosmic background + moon zoom + tagline."""
    moon = _load_local_image(LIB_DIR / "planets" / "moon_1080.png", (900, 900))

    def make_frame(t: float) -> np.ndarray:
        # Zoom moon from 0.5 to 0.85
        p = t / duration
        scale = 0.55 + 0.30 * p
        img = Image.fromarray(bg_arr).convert("RGBA")
        img = _paste_center(img, moon, W // 2, int(H * 0.42), scale=scale)
        return np.array(img.convert("RGB"))

    base = VideoClip(make_frame, duration=duration).set_fps(FPS)

    # Tagline appears at 1.5s, stays until end
    tag = _render_text(
        "Découvre les périodes qui vont\nréellement compter pour toi",
        FONT_TITLE, size=64, color=IVORY, max_w=960, glow=True,
        letter_spacing=2,
    )
    tag_clip = (
        _pil_to_clip(tag, duration - 1.2)
        .set_position(("center", int(H * 0.72)))
        .set_start(1.2)
        .crossfadein(0.8)
    )

    small = _render_text("PLUME  •  ASTRALE", FONT_TITLE, size=32,
                        color=GOLD_LIGHT, letter_spacing=8, glow=False, max_w=900)
    small_clip = (
        _pil_to_clip(small, duration)
        .set_position(("center", int(H * 0.10)))
        .crossfadein(0.6)
    )

    # Small ornamental stars flanking the brand text
    star_small = _draw_star_ornament(18, color=GOLD_LIGHT)
    left_star = (
        _pil_to_clip(star_small, duration)
        .set_position((int(W * 0.18), int(H * 0.10) + 6))
        .crossfadein(0.6)
    )
    right_star = (
        _pil_to_clip(star_small, duration)
        .set_position((int(W * 0.78), int(H * 0.10) + 6))
        .crossfadein(0.6)
    )

    return CompositeVideoClip([base, small_clip, left_star, right_star, tag_clip], size=(W, H))


def _scene_natal(duration: float, bg_arr: np.ndarray) -> VideoClip:
    """Scene 2: zodiac carousel + Thème Natal title."""
    signs_dir = LIB_DIR / "signs"
    order = [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    ]
    imgs = [_load_local_image(signs_dir / f"{s}_1080.png", (760, 760)) for s in order]
    per_slot = duration / 5.0  # show 5 signs (with overlap)
    picks = [imgs[0], imgs[2], imgs[4], imgs[7], imgs[10]]

    def make_frame(t: float) -> np.ndarray:
        base = Image.fromarray(bg_arr).convert("RGBA")
        idx = min(len(picks) - 1, int(t / per_slot))
        local_t = (t - idx * per_slot) / per_slot  # 0..1
        # Slide in from right, slide out to left, with scale breathing
        # x offset in pixels
        x_off = int((1 - local_t) * 600 if local_t < 0.5 else (local_t - 0.5) * -1200)
        scale = 0.85 + 0.10 * math.sin(math.pi * local_t)
        img = picks[idx]
        base = _paste_center(base, img, W // 2 + x_off, int(H * 0.45), scale=scale)
        # if next available, ghost preview coming in
        if idx + 1 < len(picks) and local_t > 0.6:
            nxt = picks[idx + 1]
            fade = (local_t - 0.6) / 0.4
            # blend by pasting semi-transparent
            nxt_a = nxt.copy()
            alpha = nxt_a.split()[3].point(lambda p: int(p * (0.35 * fade)))
            nxt_a.putalpha(alpha)
            base = _paste_center(base, nxt_a, W // 2 + int(500 * (1 - fade)),
                                int(H * 0.45), scale=0.7)
        return np.array(base.convert("RGB"))

    base = VideoClip(make_frame, duration=duration).set_fps(FPS)

    title = _render_text("Ton Thème Natal Ultra", FONT_TITLE, size=68,
                         color=GOLD_LIGHT, glow=True, letter_spacing=3, max_w=1000)
    sub = _render_text("40+ pages personnalisées", FONT_SUB, size=44,
                       color=IVORY, glow=True)
    t_clip = (
        _pil_to_clip(title, duration - 0.4)
        .set_position(("center", int(H * 0.80)))
        .set_start(0.4).crossfadein(0.5)
    )
    s_clip = (
        _pil_to_clip(sub, duration - 0.8)
        .set_position(("center", int(H * 0.90)))
        .set_start(0.8).crossfadein(0.5)
    )
    return CompositeVideoClip([base, t_clip, s_clip], size=(W, H))


def _scene_tarot(duration: float, bg_arr: np.ndarray) -> VideoClip:
    """Scene 3: 3 tarot cards flipping in."""
    picks = [
        "19_le_soleil_1080.png",
        "17_l_etoile_1080.png",
        "21_le_monde_1080.png",
    ]
    card_imgs: list[Image.Image] = []
    for name in picks:
        p = _download_tarot(name)
        if p and p.exists():
            card_imgs.append(_load_local_image(p, (520, 780)))
    if not card_imgs:
        # fallback: use signs
        card_imgs = [_load_local_image(LIB_DIR / "signs" / "leo_1080.png", (520, 780))] * 3

    # Card positions: left, center, right
    slot_xs = [int(W * 0.22), int(W * 0.50), int(W * 0.78)]
    slot_y = int(H * 0.48)
    reveal_at = [0.4, 1.6, 2.8]  # seconds
    reveal_dur = 0.8

    def make_frame(t: float) -> np.ndarray:
        base = Image.fromarray(bg_arr).convert("RGBA")
        for i, img in enumerate(card_imgs):
            start = reveal_at[i]
            if t < start:
                continue
            p = min(1.0, (t - start) / reveal_dur)
            # scale from 0 to 1 (flip effect via horizontal scale abs)
            scale_y = 0.7 + 0.3 * p
            # simulate flip: horizontal scale goes 0.05 -> 1.0 via cos
            flip = abs(math.cos((1 - p) * math.pi / 2))
            scale_x = 0.05 + 0.95 * flip
            iw = max(1, int(img.width * scale_x))
            ih = max(1, int(img.height * scale_y))
            resized = img.resize((iw, ih), Image.LANCZOS)
            # subtle floating after reveal
            hover = 0
            if p >= 1.0:
                hover = int(8 * math.sin((t - start - reveal_dur) * 2.2 + i))
            base.paste(resized,
                       (slot_xs[i] - resized.width // 2,
                        slot_y - resized.height // 2 + hover),
                       resized)
        return np.array(base.convert("RGB"))

    base = VideoClip(make_frame, duration=duration).set_fps(FPS)

    title = _render_text("Tirage de Tarot", FONT_TITLE, size=76,
                         color=GOLD_LIGHT, glow=True, letter_spacing=3)
    sub = _render_text("Les cartes te parlent", FONT_SUB, size=44,
                       color=IVORY, glow=True)
    t_clip = (
        _pil_to_clip(title, duration - 0.2)
        .set_position(("center", int(H * 0.13)))
        .set_start(0.2).crossfadein(0.5)
    )
    s_clip = (
        _pil_to_clip(sub, duration - 0.6)
        .set_position(("center", int(H * 0.83)))
        .set_start(0.6).crossfadein(0.5)
    )
    return CompositeVideoClip([base, t_clip, s_clip], size=(W, H))


def _scene_cta(duration: float, bg_arr: np.ndarray) -> VideoClip:
    """Scene 4: 20 crédits offerts + plume-astrale.fr."""
    # Add gold radial halo
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    cx, cy = W // 2, int(H * 0.45)
    for r in range(700, 0, -20):
        alpha = int(70 * (r / 700))
        hd.ellipse((cx - r, cy - r, cx + r, cy + r),
                   fill=(GOLD[0], GOLD[1], GOLD[2], max(0, 40 - alpha // 20)))
    halo = halo.filter(ImageFilter.GaussianBlur(60))

    bg_pil = Image.fromarray(bg_arr).convert("RGBA")
    bg_pil = Image.alpha_composite(bg_pil, halo)
    bg_final = np.array(bg_pil.convert("RGB"))

    def make_frame(t: float) -> np.ndarray:
        return bg_final

    base = VideoClip(make_frame, duration=duration).set_fps(FPS)

    big = _render_text("20 crédits offerts", FONT_TITLE, size=110,
                       color=GOLD_LIGHT, glow=True, letter_spacing=3)
    star = _draw_star_ornament(60, color=GOLD_LIGHT)
    sub = _render_text("À ton inscription", FONT_SUB, size=52,
                       color=IVORY, glow=True)
    url = _render_text("plume-astrale.fr", FONT_TITLE, size=54,
                       color=IVORY, glow=True, letter_spacing=4)

    star_c = _pil_to_clip(star, duration).set_position(("center", int(H * 0.22))).crossfadein(0.4)
    big_c = _pil_to_clip(big, duration).set_position(("center", int(H * 0.38))).crossfadein(0.6)
    sub_c = (
        _pil_to_clip(sub, duration - 0.3)
        .set_position(("center", int(H * 0.52)))
        .set_start(0.3).crossfadein(0.6)
    )
    url_c = (
        _pil_to_clip(url, duration - 0.8)
        .set_position(("center", int(H * 0.74)))
        .set_start(0.8).crossfadein(0.6)
    )

    return CompositeVideoClip([base, star_c, big_c, sub_c, url_c], size=(W, H))


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------

def generate_tiktok_video(
    output_filename: str = "plume_tiktok_decouverte.mp4",
    preview: bool = False,
) -> Path:
    """
    Build the full 30s vertical TikTok video. Returns path to the MP4.
    Set preview=True for a 480p faster render.
    """
    output_path = OUTPUT_DIR / output_filename

    logger.info("[video] building cosmic background...")
    bg = _cosmic_background(seed=7)
    sparkles = _sparkle_layer()
    bg_with_sparkles = Image.alpha_composite(bg.convert("RGBA"), sparkles)
    bg_arr = np.array(bg_with_sparkles.convert("RGB"))

    logger.info("[video] scene 1: hook...")
    s1 = _scene_hook(6.5, bg_arr)
    logger.info("[video] scene 2: natal...")
    s2 = _scene_natal(9.5, bg_arr)
    logger.info("[video] scene 3: tarot...")
    s3 = _scene_tarot(9.5, bg_arr)
    logger.info("[video] scene 4: cta...")
    s4 = _scene_cta(6.5, bg_arr)

    # cross-fade transitions
    s2 = s2.crossfadein(0.5)
    s3 = s3.crossfadein(0.5)
    s4 = s4.crossfadein(0.5)

    video = concatenate_videoclips([s1, s2, s3, s4], method="compose", padding=-0.5)
    # Trim to exact target duration
    video = video.set_duration(min(video.duration, float(DURATION)))

    # Audio
    logger.info("[video] generating ambient audio...")
    audio_path = OUTPUT_DIR / "_ambient_pad.aac"
    try:
        _generate_ambient_track(audio_path, duration=video.duration)
        audio = (
            AudioFileClip(str(audio_path))
            .subclip(0, video.duration)
            .volumex(0.55)
            .audio_fadein(1.0)
            .audio_fadeout(1.5)
        )
        video = video.set_audio(audio)
    except Exception as e:
        logger.warning(f"[video] audio generation failed, exporting silent: {e}")

    # Export
    logger.info(f"[video] rendering to {output_path}...")
    target_size = (W, H) if not preview else (540, 960)
    if preview:
        video = video.resize(target_size)
    video.write_videofile(
        str(output_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="6000k",
        threads=4,
        logger=None,
        temp_audiofile=str(OUTPUT_DIR / "_temp_audio.m4a"),
        remove_temp=True,
    )
    logger.info(f"[video] done: {output_path} ({output_path.stat().st_size // 1024} KB)")
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    out = generate_tiktok_video()
    print(f"Generated: {out}")


# ---------------------------------------------------------------------------
# Scenario 2: "Tirage Gratuit" (3-card past/present/future)
# ---------------------------------------------------------------------------

def _draw_card_back(width: int = 520, height: int = 780) -> Image.Image:
    """Draw a luxury tarot card back (deep navy + gold filigree ornaments)."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Card face — deep midnight
    face = (18, 12, 40)
    edge = 8
    d.rounded_rectangle((edge, edge, width - edge, height - edge),
                        radius=18, fill=face)
    # Double gold border
    d.rounded_rectangle((edge, edge, width - edge, height - edge),
                        radius=18, outline=(GOLD[0], GOLD[1], GOLD[2], 255), width=3)
    inner = 22
    d.rounded_rectangle((inner, inner, width - inner, height - inner),
                        radius=12, outline=(GOLD_LIGHT[0], GOLD_LIGHT[1], GOLD_LIGHT[2], 200), width=1)

    # Central compass / rosette
    cx, cy = width // 2, height // 2
    R = min(width, height) // 5
    # Outer ring
    d.ellipse((cx - R, cy - R, cx + R, cy + R),
              outline=(GOLD[0], GOLD[1], GOLD[2], 255), width=2)
    d.ellipse((cx - R + 8, cy - R + 8, cx + R - 8, cy + R - 8),
              outline=(GOLD_LIGHT[0], GOLD_LIGHT[1], GOLD_LIGHT[2], 200), width=1)

    # 8-point star inside the ring
    for i in range(8):
        angle = i * math.pi / 4
        x2 = cx + int(R * 0.75 * math.cos(angle))
        y2 = cy + int(R * 0.75 * math.sin(angle))
        d.line((cx, cy, x2, y2),
               fill=(GOLD_LIGHT[0], GOLD_LIGHT[1], GOLD_LIGHT[2], 220), width=2)
    # Inner filled star
    star = _draw_star_ornament(int(R * 0.55), color=GOLD_LIGHT)
    img.paste(star, (cx - star.width // 2, cy - star.height // 2), star)

    # 4 corner flourishes (small stars)
    corner_star = _draw_star_ornament(14, color=GOLD_LIGHT)
    for (px, py) in [(48, 48), (width - 48, 48),
                     (48, height - 48), (width - 48, height - 48)]:
        img.paste(corner_star,
                  (px - corner_star.width // 2, py - corner_star.height // 2),
                  corner_star)

    # "Plume Astrale" text at bottom
    try:
        font_small = ImageFont.truetype(FONT_TITLE, 20)
        text = "PLUME  ASTRALE"
        tw = font_small.getlength(text)
        d.text((cx - tw / 2, height - 60), text,
               font=font_small, fill=(GOLD_LIGHT[0], GOLD_LIGHT[1], GOLD_LIGHT[2], 220))
    except Exception:
        pass

    # Subtle vignette / grain — softness at corners
    return img


def _scene_tirage_hook(duration: float, bg_arr: np.ndarray) -> VideoClip:
    """Scene 1 (Tirage): 3 card backs stacked + hook."""
    back = _draw_card_back(440, 660)
    # Rotate 3 cards, stacked with slight offsets
    backs = [
        back.rotate(a, resample=Image.BICUBIC, expand=True)
        for a in (-8, 0, 8)
    ]

    def make_frame(t: float) -> np.ndarray:
        base = Image.fromarray(bg_arr).convert("RGBA")
        # Cards float up slightly
        p = t / duration
        cy = int(H * 0.48 + math.sin(p * math.pi * 2) * 6)
        for i, b in enumerate(backs):
            offset_x = (i - 1) * 40
            base.paste(b, (W // 2 - b.width // 2 + offset_x,
                           cy - b.height // 2), b)
        return np.array(base.convert("RGB"))

    base = VideoClip(make_frame, duration=duration).set_fps(FPS)

    hook = _render_text("Tire ta carte du jour", FONT_TITLE, size=76,
                        color=GOLD_LIGHT, glow=True, letter_spacing=3, max_w=1000)
    sub = _render_text("Passé  •  Présent  •  Futur", FONT_SUB, size=48,
                       color=IVORY, glow=True)
    hook_c = (
        _pil_to_clip(hook, duration - 0.3)
        .set_position(("center", int(H * 0.12)))
        .set_start(0.3).crossfadein(0.6)
    )
    sub_c = (
        _pil_to_clip(sub, duration - 0.7)
        .set_position(("center", int(H * 0.83)))
        .set_start(0.7).crossfadein(0.5)
    )
    return CompositeVideoClip([base, hook_c, sub_c], size=(W, H))


def _scene_tirage_spread(duration: float, bg_arr: np.ndarray) -> VideoClip:
    """Scene 2: 3 card backs slide apart into position (Passé / Présent / Futur)."""
    back = _draw_card_back(300, 450)
    slot_xs = [int(W * 0.22), int(W * 0.50), int(W * 0.78)]
    slot_y = int(H * 0.48)
    labels_text = ["PASSÉ", "PRÉSENT", "FUTUR"]

    def make_frame(t: float) -> np.ndarray:
        base = Image.fromarray(bg_arr).convert("RGBA")
        p = min(1.0, t / (duration * 0.7))  # spread completes at 70% of scene
        # Ease-out cubic
        eased = 1 - (1 - p) ** 3
        for i in range(3):
            start_x = W // 2
            end_x = slot_xs[i]
            cur_x = int(start_x + (end_x - start_x) * eased)
            # Slight rotation as cards land
            angle = (i - 1) * (1 - eased) * 20
            b = back.rotate(angle, resample=Image.BICUBIC, expand=True)
            base.paste(b, (cur_x - b.width // 2, slot_y - b.height // 2), b)
        return np.array(base.convert("RGB"))

    base = VideoClip(make_frame, duration=duration).set_fps(FPS)

    title = _render_text("Les cartes se dévoilent", FONT_TITLE, size=60,
                         color=GOLD_LIGHT, glow=True, letter_spacing=3, max_w=1000)
    t_clip = (
        _pil_to_clip(title, duration - 0.3)
        .set_position(("center", int(H * 0.12)))
        .set_start(0.3).crossfadein(0.5)
    )

    # Labels appear once cards are in place (after 70% of scene)
    label_clips = []
    for i, txt in enumerate(labels_text):
        lbl = _render_text(txt, FONT_TITLE, size=32,
                           color=GOLD_LIGHT, glow=True, letter_spacing=4, max_w=400)
        lc = (
            _pil_to_clip(lbl, duration - duration * 0.7)
            .set_position((slot_xs[i] - 100, int(H * 0.72)))
            .set_start(duration * 0.7).crossfadein(0.4)
        )
        label_clips.append(lc)

    return CompositeVideoClip([base, t_clip] + label_clips, size=(W, H))


def _scene_tirage_reveal(duration: float, bg_arr: np.ndarray) -> VideoClip:
    """Scene 3: 3 cards flip one by one revealing Soleil, Roue de Fortune, Étoile."""
    picks = [
        ("19_le_soleil_1080.png",       "Le Soleil"),
        ("10_la_roue_de_fortune_1080.png", "La Roue"),
        ("17_l_etoile_1080.png",        "L'Étoile"),
    ]
    card_imgs: list[tuple[Image.Image, str]] = []
    for fname, name in picks:
        p = _download_tarot(fname)
        if p and p.exists():
            card_imgs.append((_load_local_image(p, (420, 630)), name))
    while len(card_imgs) < 3:
        card_imgs.append((_draw_card_back(420, 630), "?"))

    back = _draw_card_back(420, 630)
    slot_xs = [int(W * 0.22), int(W * 0.50), int(W * 0.78)]
    slot_y = int(H * 0.48)
    reveal_at = [0.5, 4.0, 7.5]
    reveal_dur = 1.2

    def make_frame(t: float) -> np.ndarray:
        base = Image.fromarray(bg_arr).convert("RGBA")
        for i, (img, name) in enumerate(card_imgs):
            start = reveal_at[i]
            if t < start:
                # Show back
                base.paste(back,
                           (slot_xs[i] - back.width // 2,
                            slot_y - back.height // 2), back)
                continue
            p = min(1.0, (t - start) / reveal_dur)
            # Flip: 0..0.5 shrink back to 0.05, 0.5..1.0 grow front to 1.0
            if p < 0.5:
                # shrinking back
                sx = 1.0 - (p / 0.5) * 0.95
                iw = max(1, int(back.width * sx))
                ih = back.height
                rez = back.resize((iw, ih), Image.LANCZOS)
                base.paste(rez,
                           (slot_xs[i] - rez.width // 2,
                            slot_y - rez.height // 2), rez)
            else:
                # growing front
                sx = 0.05 + ((p - 0.5) / 0.5) * 0.95
                iw = max(1, int(img.width * sx))
                ih = img.height
                rez = img.resize((iw, ih), Image.LANCZOS)
                # subtle floating after full reveal
                hover = int(6 * math.sin((t - start - reveal_dur) * 2.0 + i)) if p >= 1.0 else 0
                base.paste(rez,
                           (slot_xs[i] - rez.width // 2,
                            slot_y - rez.height // 2 + hover), rez)
        return np.array(base.convert("RGB"))

    base = VideoClip(make_frame, duration=duration).set_fps(FPS)

    title = _render_text("Ton tirage", FONT_TITLE, size=70,
                         color=GOLD_LIGHT, glow=True, letter_spacing=4, max_w=1000)
    t_clip = (
        _pil_to_clip(title, duration - 0.2)
        .set_position(("center", int(H * 0.11)))
        .set_start(0.2).crossfadein(0.4)
    )

    # Card name labels appear after each reveal
    labels_text = ["Le Soleil", "La Roue", "L'Étoile"]
    label_clips = []
    for i, txt in enumerate(labels_text):
        lbl = _render_text(txt, FONT_SUB, size=38,
                           color=IVORY, glow=True, max_w=400)
        appear = reveal_at[i] + reveal_dur
        lc = (
            _pil_to_clip(lbl, duration - appear)
            .set_position((slot_xs[i] - 120, int(H * 0.78)))
            .set_start(appear).crossfadein(0.4)
        )
        label_clips.append(lc)

    return CompositeVideoClip([base, t_clip] + label_clips, size=(W, H))


def _scene_tirage_cta(duration: float, bg_arr: np.ndarray) -> VideoClip:
    """Scene 4 (Tirage): CTA vers tirage complet."""
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    cx, cy = W // 2, int(H * 0.45)
    for r in range(700, 0, -20):
        hd.ellipse((cx - r, cy - r, cx + r, cy + r),
                   fill=(GOLD[0], GOLD[1], GOLD[2], max(0, 40 - r // 30)))
    halo = halo.filter(ImageFilter.GaussianBlur(60))
    bg_pil = Image.fromarray(bg_arr).convert("RGBA")
    bg_pil = Image.alpha_composite(bg_pil, halo)
    bg_final = np.array(bg_pil.convert("RGB"))

    def make_frame(t: float) -> np.ndarray:
        return bg_final

    base = VideoClip(make_frame, duration=duration).set_fps(FPS)

    star = _draw_star_ornament(60, color=GOLD_LIGHT)
    line1 = _render_text("Ton tirage complet t'attend", FONT_TITLE, size=72,
                         color=GOLD_LIGHT, glow=True, letter_spacing=2, max_w=1000)
    line2 = _render_text("20 crédits offerts", FONT_SUB, size=56,
                         color=IVORY, glow=True)
    url = _render_text("plume-astrale.fr", FONT_TITLE, size=54,
                       color=IVORY, glow=True, letter_spacing=4)

    star_c = _pil_to_clip(star, duration).set_position(("center", int(H * 0.22))).crossfadein(0.4)
    l1_c = _pil_to_clip(line1, duration).set_position(("center", int(H * 0.38))).crossfadein(0.6)
    l2_c = (
        _pil_to_clip(line2, duration - 0.3)
        .set_position(("center", int(H * 0.52)))
        .set_start(0.3).crossfadein(0.6)
    )
    url_c = (
        _pil_to_clip(url, duration - 0.8)
        .set_position(("center", int(H * 0.74)))
        .set_start(0.8).crossfadein(0.6)
    )
    return CompositeVideoClip([base, star_c, l1_c, l2_c, url_c], size=(W, H))


def generate_tirage_video(
    output_filename: str = "plume_tiktok_tirage_gratuit.mp4",
    mute: bool = True,
    preview: bool = False,
) -> Path:
    """
    Generate the "Tirage Gratuit" 30s vertical video.

    Scene 1 (5.5s): Hook — 3 stacked card backs + "Tire ta carte du jour"
    Scene 2 (7.0s): Spread — cards slide to Passé/Présent/Futur positions
    Scene 3 (12.0s): Reveal — cards flip revealing Le Soleil / La Roue / L'Étoile
    Scene 4 (5.5s): CTA — "Ton tirage complet t'attend / plume-astrale.fr"

    mute=True → silent MP4 (perfect to add TikTok music on top).
    """
    output_path = OUTPUT_DIR / output_filename

    logger.info("[video/tirage] building background...")
    bg = _cosmic_background(seed=13)
    sparkles = _sparkle_layer(seed=17)
    bg_with_sparkles = Image.alpha_composite(bg.convert("RGBA"), sparkles)
    bg_arr = np.array(bg_with_sparkles.convert("RGB"))

    logger.info("[video/tirage] scene 1: hook + card backs...")
    s1 = _scene_tirage_hook(6.0, bg_arr)
    logger.info("[video/tirage] scene 2: spread...")
    s2 = _scene_tirage_spread(7.5, bg_arr)
    logger.info("[video/tirage] scene 3: reveal...")
    s3 = _scene_tirage_reveal(12.5, bg_arr)
    logger.info("[video/tirage] scene 4: cta...")
    s4 = _scene_tirage_cta(6.0, bg_arr)

    s2 = s2.crossfadein(0.5)
    s3 = s3.crossfadein(0.5)
    s4 = s4.crossfadein(0.5)

    video = concatenate_videoclips([s1, s2, s3, s4], method="compose", padding=-0.5)
    video = video.set_duration(min(video.duration, float(DURATION)))

    if not mute:
        logger.info("[video/tirage] generating ambient audio...")
        try:
            audio_path = OUTPUT_DIR / "_ambient_pad_tirage.aac"
            _generate_ambient_track(audio_path, duration=video.duration)
            audio = (
                AudioFileClip(str(audio_path))
                .subclip(0, video.duration)
                .volumex(0.55)
                .audio_fadein(1.0)
                .audio_fadeout(1.5)
            )
            video = video.set_audio(audio)
        except Exception as e:
            logger.warning(f"[video/tirage] audio failed: {e}")

    logger.info(f"[video/tirage] rendering to {output_path}...")
    if preview:
        video = video.resize((540, 960))
    video.write_videofile(
        str(output_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac" if not mute else None,
        preset="medium",
        bitrate="6000k",
        threads=4,
        logger=None,
        temp_audiofile=str(OUTPUT_DIR / "_temp_audio_tirage.m4a") if not mute else None,
        remove_temp=True,
    )
    logger.info(f"[video/tirage] done: {output_path} "
                f"({output_path.stat().st_size // 1024} KB)")
    return output_path
