"""
V4 — Hook 15s pour Reels / TikTok / Stories.

4 mini-clips coupés dans merged.webm (V3) :
  0-3s   : Hero home (source 3.5-6.5s : belle image, avant fade)
  3-6.5s : Horoscope Lion révélé (source 20-23.5s)
  6.5-10s: Mon espace personnel (source 45.5-49s)
  10-15s : Cercle (source 58-63s) + CTA plein écran

Captions :
  0-2.5s   : "Ton horoscope. Ton parcours."   (giant hook)
  3-6s     : "COMPRIS. PAS DEVINÉ."           (accent)
  6.5-9.5s : "Ton espace. Tes crédits."
  10-15s   : "20 CRÉDITS OFFERTS" (gold) + "plume-astrale.fr"
"""
import subprocess
from pathlib import Path

OUT_DIR = Path("/app/tmp_video")
SRC = OUT_DIR / "merged.webm"
OUT = OUT_DIR / "plume_astrale_hook_15s.mp4"

FONT_SERIF = "/app/backend/assets/fonts/CormorantGaramond-Bold.ttf"
FONT_SANS = "/app/backend/assets/fonts/tiktok/BebasNeue-Regular.ttf"
FONT_ANTON = "/app/backend/assets/fonts/tiktok/Anton-Regular.ttf"

# Segments à extraire (start, end) en secondes, dans merged.webm
SEGMENTS = [
    (3.5, 6.5),    # Hero (3s)
    (20.0, 23.5),  # Horoscope Lion (3.5s)
    (45.5, 49.0),  # Mon Espace (3.5s)
    (58.0, 63.0),  # Cercle (5s)
]

CAPTIONS = [
    # HOOK — giant serif italic sur le hero
    {"text": "Ton horoscope.", "font": FONT_SERIF, "size": 72,
     "y_pct": 0.35, "start": 0.4, "end": 2.8, "color": "white"},
    {"text": "Ton parcours.", "font": FONT_SERIF, "size": 72,
     "y_pct": 0.44, "start": 0.7, "end": 2.8, "color": "0xD4AF37"},
    # Segment 2 — HOROSCOPE
    {"text": "COMPRIS.", "font": FONT_ANTON, "size": 130,
     "y_pct": 0.35, "start": 3.2, "end": 6.2, "color": "white"},
    {"text": "PAS DEVINÉ.", "font": FONT_ANTON, "size": 130,
     "y_pct": 0.45, "start": 3.7, "end": 6.2, "color": "0xD4AF37"},
    # Segment 3 — MON ESPACE
    {"text": "TON ESPACE.", "font": FONT_ANTON, "size": 110,
     "y_pct": 0.36, "start": 6.7, "end": 9.7, "color": "white"},
    {"text": "TES CRÉDITS.", "font": FONT_ANTON, "size": 110,
     "y_pct": 0.45, "start": 7.1, "end": 9.7, "color": "0xD4AF37"},
    # CTA final segment 4
    {"text": "20 CRÉDITS", "font": FONT_ANTON, "size": 140,
     "y_pct": 0.30, "start": 10.3, "end": 15, "color": "0xD4AF37"},
    {"text": "OFFERTS", "font": FONT_ANTON, "size": 140,
     "y_pct": 0.41, "start": 10.6, "end": 15, "color": "0xD4AF37"},
    {"text": "plume-astrale.fr", "font": FONT_SERIF, "size": 64,
     "y_pct": 0.55, "start": 11.0, "end": 15, "color": "white"},
]


def build_captions():
    filters = []
    for c in CAPTIONS:
        fi, fo = 0.25, 0.35
        alpha_expr = (
            f"if(lt(t,{c['start']}+{fi}),"
            f"(t-{c['start']})/{fi},"
            f"if(gt(t,{c['end']}-{fo}),"
            f"({c['end']}-t)/{fo},1))"
        )
        y_expr = f"h*{c['y_pct']}"
        # Ombre plus prononcée pour lisibilité TikTok
        shadow = (
            f"drawtext=fontfile={c['font']}:text='{c['text']}':"
            f"fontsize={c['size']}:fontcolor=black@0.7:"
            f"x=(w-text_w)/2+5:y={y_expr}+6:"
            f"enable='between(t,{c['start']},{c['end']})':"
            f"alpha='{alpha_expr}'"
        )
        text = (
            f"drawtext=fontfile={c['font']}:text='{c['text']}':"
            f"fontsize={c['size']}:fontcolor={c['color']}:"
            f"x=(w-text_w)/2:y={y_expr}:"
            f"enable='between(t,{c['start']},{c['end']})':"
            f"alpha='{alpha_expr}'"
        )
        filters.append(shadow)
        filters.append(text)
    return filters


def main():
    if not SRC.exists():
        raise RuntimeError(f"{SRC} manquant — refais record_plume_v3.py d'abord")

    # Build filter_complex : trim segments then concat then scale + captions + fades
    trims = []
    concat_inputs = []
    for i, (s, e) in enumerate(SEGMENTS):
        trims.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]")
        concat_inputs.append(f"[v{i}]")
    trim_chain = ";".join(trims)
    concat = "".join(concat_inputs) + f"concat=n={len(SEGMENTS)}:v=1:a=0[merged]"

    caption_chain = ",".join(build_captions())
    final_chain = (
        f"[merged]scale=1080:1920:flags=lanczos,"
        f"{caption_chain},"
        f"fade=t=in:st=0:d=0.4,fade=t=out:st=14.2:d=0.8[out]"
    )

    filter_complex = f"{trim_chain};{concat};{final_chain}"

    cmd = [
        "ffmpeg", "-y", "-i", str(SRC),
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-t", "15",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
        str(OUT),
    ]
    print("▸ Rendering hook 15s…")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("STDERR:", proc.stderr[-2000:])
        raise RuntimeError("ffmpeg failed")
    print(f"✓ {OUT} ({OUT.stat().st_size/(1024*1024):.1f} MB)")


if __name__ == "__main__":
    main()
