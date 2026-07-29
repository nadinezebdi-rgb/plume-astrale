"""
Convert Plume Astrale PDFs into vertical 9:16 scroll-through MP4s ready
to embed in TikTok video montages.

Usage:
    python3 scripts/pdf_to_scroll_video.py
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

# Ensure MoviePy uses system ffmpeg (bundled 7.0.2 static build has issues)
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
os.environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from PIL import Image
from moviepy.editor import VideoClip

W, H = 1080, 1920
FPS = 30
DPI = 200  # PDF render density (higher = crisper text)
PAGE_GAP_PX = 60  # small gap between pages
TOP_HOLD = 1.2  # seconds to hold on the top
BOTTOM_HOLD = 1.5  # seconds to hold on the bottom
SCROLL_TIME = 4.0  # seconds actively scrolling


def _render_pdf_to_pngs(pdf_path: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / pdf_path.stem
    # Clean previous
    for f in out_dir.glob(f"{pdf_path.stem}-*.png"):
        f.unlink()
    subprocess.run(
        ["pdftoppm", "-r", str(DPI), str(pdf_path), str(base), "-png"],
        check=True, capture_output=True,
    )
    return sorted(out_dir.glob(f"{pdf_path.stem}-*.png"))


def _build_scroll_strip(png_paths: list[Path]) -> Image.Image:
    """
    Stack PDF pages vertically into one tall image resized so each page
    matches the target width W. Small gap between pages, matching bg color.
    """
    pages = []
    for p in png_paths:
        im = Image.open(p).convert("RGB")
        # Scale so width = W
        scale = W / im.width
        new_h = int(im.height * scale)
        im = im.resize((W, new_h), Image.LANCZOS)
        pages.append(im)

    # Sample gap color from top-left pixel of first page (bg)
    gap_color = pages[0].getpixel((5, 5))
    total_h = sum(p.height for p in pages) + PAGE_GAP_PX * max(0, len(pages) - 1)
    strip = Image.new("RGB", (W, total_h), gap_color)
    y = 0
    for i, p in enumerate(pages):
        strip.paste(p, (0, y))
        y += p.height + (PAGE_GAP_PX if i < len(pages) - 1 else 0)
    return strip


def _build_scroll_video(strip: Image.Image, out_path: Path,
                        scroll_time: float = SCROLL_TIME,
                        top_hold: float = TOP_HOLD,
                        bottom_hold: float = BOTTOM_HOLD) -> Path:
    """
    Create a vertical scroll video that pans a 1080x1920 window down
    the tall strip image. Falls back to a "letterbox" if the strip is
    shorter than one screen height (unlikely for A4).
    """
    strip_arr = np.array(strip)
    strip_h = strip_arr.shape[0]

    # Total scroll distance (in px) — from y=0 to y = strip_h - H
    max_offset = max(0, strip_h - H)
    duration = top_hold + scroll_time + bottom_hold

    def make_frame(t: float) -> np.ndarray:
        if t < top_hold:
            y = 0
        elif t < top_hold + scroll_time:
            # Ease-in-out cubic
            p = (t - top_hold) / scroll_time
            eased = 3 * p ** 2 - 2 * p ** 3
            y = int(max_offset * eased)
        else:
            y = max_offset
        y = max(0, min(y, max_offset))
        window = strip_arr[y:y + H, :, :]
        # Pad if needed (shouldn't happen given max_offset math)
        if window.shape[0] < H:
            pad = np.zeros((H - window.shape[0], W, 3), dtype=np.uint8)
            window = np.vstack([window, pad])
        return window

    clip = VideoClip(make_frame, duration=duration).set_fps(FPS)
    # Fade in/out
    clip = clip.fadein(0.3).fadeout(0.4)

    clip.write_videofile(
        str(out_path),
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="medium",
        bitrate="6500k",
        threads=4,
        logger=None,
    )
    print(f"✓ {out_path.name} ({out_path.stat().st_size // 1024} KB, {duration:.1f}s)")
    return out_path


def build_scroll_video_for_pdf(pdf_path: Path, out_dir: Path,
                                scroll_time: float = SCROLL_TIME) -> Path:
    print(f"\n▶ {pdf_path.name}")
    tmp_pngs_dir = Path("/tmp/pdf_scroll_pngs")
    pngs = _render_pdf_to_pngs(pdf_path, tmp_pngs_dir)
    print(f"  · rendered {len(pngs)} page(s)")
    strip = _build_scroll_strip(pngs)
    print(f"  · strip: {strip.width}x{strip.height}px")
    out_path = out_dir / f"{pdf_path.stem}_scroll.mp4"
    return _build_scroll_video(strip, out_path, scroll_time=scroll_time)


if __name__ == "__main__":
    out_dir = Path("/app/frontend/public/marketing")
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = [
        (Path("/app/frontend/public/marketing/modele_guidance_solena.pdf"), 5.0),
        (Path("/app/frontend/public/marketing/horoscope_journalier_lion_exemple.pdf"), 4.0),
    ]
    for pdf, scroll_dur in pdfs:
        build_scroll_video_for_pdf(pdf, out_dir, scroll_time=scroll_dur)
