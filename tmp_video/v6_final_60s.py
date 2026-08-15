"""
V6 — Version finale : 60s, chaque scène montrée UNE FOIS, captions style hook
     (Anton bold blanc/or) + musique ambient.

Découpage depuis merged.webm (84s raw V3 recording, skip login gap) :
  0-12s  : Hero home       (source 0-12s)
  12-24s : Horoscope Lion  (source 12.5-24.5s)
  24-36s : Blog            (source 26.3-38.3s)
  36-48s : Mon Espace      (source 43-55s)     ← skip login gap
  48-60s : Cercle Soléna   (source 55.7-67.7s)
Total : 60s
"""
import subprocess
from pathlib import Path

OUT_DIR = Path("/app/tmp_video")
SRC = OUT_DIR / "merged.webm"
MUSIC = OUT_DIR / "ambient_pad.wav"
FINAL = OUT_DIR / "plume_astrale_60s_final.mp4"

FONT_SERIF = "/app/backend/assets/fonts/CormorantGaramond-Bold.ttf"
FONT_ANTON = "/app/backend/assets/fonts/tiktok/Anton-Regular.ttf"

# Segments dans merged.webm (start, end)
SEGMENTS = [
    (0.5, 12.5),   # Hero (12s)
    (12.5, 24.5),  # Horoscope Lion (12s)
    (26.3, 38.3),  # Blog (12s)
    (43.0, 55.0),  # Mon Espace, skip login gap (12s)
    (55.7, 67.7),  # Cercle (12s)
]

# Captions synchronisées avec le 60s final (Anton bold, alternance blanc/or)
CAPTIONS = [
    # HERO 0-12s
    {"text": "COMPRENDRE", "font": FONT_ANTON, "size": 130,
     "y_pct": 0.38, "start": 1.0, "end": 4.5, "color": "white"},
    {"text": "TON PARCOURS.", "font": FONT_ANTON, "size": 130,
     "y_pct": 0.47, "start": 1.4, "end": 4.5, "color": "0xD4AF37"},

    # HOROSCOPE 12-24s
    {"text": "TON HOROSCOPE", "font": FONT_ANTON, "size": 115,
     "y_pct": 0.07, "start": 13.0, "end": 17.0, "color": "white"},
    {"text": "CHAQUE JOUR.", "font": FONT_ANTON, "size": 115,
     "y_pct": 0.14, "start": 13.4, "end": 17.0, "color": "0xD4AF37"},

    # BLOG 24-36s
    {"text": "COMPRENDRE.", "font": FONT_ANTON, "size": 115,
     "y_pct": 0.07, "start": 25.0, "end": 29.0, "color": "white"},
    {"text": "APPROFONDIR.", "font": FONT_ANTON, "size": 115,
     "y_pct": 0.14, "start": 25.4, "end": 29.0, "color": "0xD4AF37"},

    # MON ESPACE 36-48s
    {"text": "TON ESPACE.", "font": FONT_ANTON, "size": 120,
     "y_pct": 0.07, "start": 37.0, "end": 41.0, "color": "white"},
    {"text": "TES CRÉDITS.", "font": FONT_ANTON, "size": 120,
     "y_pct": 0.14, "start": 37.4, "end": 41.0, "color": "0xD4AF37"},

    # CERCLE 48-55s
    {"text": "UN RENDEZ-VOUS", "font": FONT_ANTON, "size": 105,
     "y_pct": 0.07, "start": 49.0, "end": 53.5, "color": "white"},
    {"text": "MENSUEL.", "font": FONT_ANTON, "size": 105,
     "y_pct": 0.14, "start": 49.4, "end": 53.5, "color": "0xD4AF37"},

    # CTA FINAL 55-60s (plein écran)
    {"text": "20 CRÉDITS", "font": FONT_ANTON, "size": 150,
     "y_pct": 0.32, "start": 55.5, "end": 60, "color": "0xD4AF37"},
    {"text": "OFFERTS", "font": FONT_ANTON, "size": 150,
     "y_pct": 0.43, "start": 55.8, "end": 60, "color": "0xD4AF37"},
    {"text": "plume-astrale.fr", "font": FONT_SERIF, "size": 66,
     "y_pct": 0.57, "start": 56.2, "end": 60, "color": "white"},
]


def build_captions():
    filters = []
    for c in CAPTIONS:
        fi, fo = 0.3, 0.4
        alpha_expr = (
            f"if(lt(t,{c['start']}+{fi}),"
            f"(t-{c['start']})/{fi},"
            f"if(gt(t,{c['end']}-{fo}),"
            f"({c['end']}-t)/{fo},1))"
        )
        y_expr = f"h*{c['y_pct']}"
        shadow = (
            f"drawtext=fontfile={c['font']}:text='{c['text']}':"
            f"fontsize={c['size']}:fontcolor=black@0.75:"
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


def build_music():
    """60s ambient pad — même recette que V5."""
    print("▸ Musique ambient 60s…")
    fc = (
        "sine=frequency=110:duration=60[a];"
        "sine=frequency=220:duration=60[b];"
        "sine=frequency=330:duration=60[c];"
        "sine=frequency=440:duration=60[d];"
        "[a]volume=0.35[a2];"
        "[b]volume=0.20[b2];"
        "[c]volume=0.12[c2];"
        "[d]volume=0.06[d2];"
        "[a2][b2][c2][d2]amix=inputs=4:normalize=0[pad];"
        "[pad]tremolo=f=0.25:d=0.15,"
        "aecho=0.8:0.7:400|800|1200:0.4|0.3|0.2,"
        "lowpass=f=2200,"
        "afade=t=in:st=0:d=2,afade=t=out:st=57:d=3,"
        "volume=0.55[out]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-filter_complex", fc, "-map", "[out]",
        "-t", "60", "-ac", "2", "-ar", "44100", "-c:a", "pcm_s16le",
        str(MUSIC),
    ], check=True, capture_output=True)


def main():
    if not SRC.exists():
        raise SystemExit(f"{SRC} manquant")
    build_music()

    # Filter graph : trim segments → concat → scale → captions → fade
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
        f"fade=t=in:st=0:d=0.5,fade=t=out:st=58.5:d=1.5[out]"
    )
    filter_complex = f"{trim_chain};{concat};{final_chain}"

    print("▸ Rendering 60s final…")
    proc = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(SRC),
        "-i", str(MUSIC),
        "-filter_complex", filter_complex,
        "-map", "[out]", "-map", "1:a",
        "-t", "60",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(FINAL),
    ], capture_output=True, text=True)
    if proc.returncode != 0:
        print("STDERR:", proc.stderr[-2000:])
        raise SystemExit("ffmpeg failed")
    print(f"✓ {FINAL} ({FINAL.stat().st_size/(1024*1024):.1f} MB)")


if __name__ == "__main__":
    main()
