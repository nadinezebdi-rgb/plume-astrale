"""
V5 — Combine Hook 15s + V3 60s captions + musique ambient synthétisée.

Total : 75s (15s hook + 60s content story).

Musique : synthèse ffmpeg d'un pad cinématique (A minor pentatonic) :
  - Drone bass sine 110Hz (A2)
  - Root pad 220Hz (A3)
  - 5th 330Hz (E4)
  - Tremolo lent 0.2 Hz pour souffle
  - Reverb via aecho
  - Fade in 2s, sustain, fade out 3s
Volume : -18 dB pour laisser captions lisibles.
"""
import subprocess
from pathlib import Path

OUT_DIR = Path("/app/tmp_video")
HOOK = OUT_DIR / "plume_astrale_hook_15s.mp4"
FULL = OUT_DIR / "plume_astrale_60s_captions.mp4"
FINAL = OUT_DIR / "plume_astrale_75s_full.mp4"
MUSIC = OUT_DIR / "ambient_pad.wav"

DURATION = 75

# ── Step 1 : générer musique ambient ──────────────────────────────────
def build_music():
    print("▸ Synthèse pad cinématique…")
    # Multi-layer synth + tremolo + reverb + LP filter
    fc = (
        # 3 drones sinusoïdales harmoniques (A minor)
        "sine=frequency=110:duration={d}[a];"
        "sine=frequency=220:duration={d}[b];"
        "sine=frequency=330:duration={d}[c];"
        "sine=frequency=440:duration={d}[d];"
        # Mix layers with different volumes
        "[a]volume=0.35[a2];"
        "[b]volume=0.20[b2];"
        "[c]volume=0.12[c2];"
        "[d]volume=0.06[d2];"
        "[a2][b2][c2][d2]amix=inputs=4:normalize=0[pad];"
        # Slow tremolo LFO (breath) + reverb (echo)
        "[pad]tremolo=f=0.25:d=0.15,"
        "aecho=0.8:0.7:400|800|1200:0.4|0.3|0.2,"
        # Low-pass for warmth
        "lowpass=f=2200,"
        # Global envelope fades
        "afade=t=in:st=0:d=2,afade=t=out:st={fo}:d=3,"
        # Master volume
        "volume=0.55[out]"
    ).format(d=DURATION, fo=DURATION - 3)

    subprocess.run([
        "ffmpeg", "-y",
        "-filter_complex", fc,
        "-map", "[out]",
        "-t", str(DURATION),
        "-ac", "2", "-ar", "44100",
        "-c:a", "pcm_s16le",
        str(MUSIC),
    ], check=True, capture_output=True)
    print(f"  ✓ {MUSIC} ({MUSIC.stat().st_size/1024:.0f} KB)")


# ── Step 2 : concat hook + full ──────────────────────────────────────
def concat_videos():
    print("▸ Concat hook 15s + V3 60s…")
    concat_txt = OUT_DIR / "concat_v5.txt"
    concat_txt.write_text(
        f"file '{HOOK.resolve()}'\nfile '{FULL.resolve()}'\n"
    )
    concat_mp4 = OUT_DIR / "concat_v5.mp4"
    # Re-encode to normalize timescale (concat demuxer needs same encode params)
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "25",
        "-an",
        str(concat_mp4),
    ], check=True, capture_output=True)
    print(f"  ✓ {concat_mp4} ({concat_mp4.stat().st_size/(1024*1024):.1f} MB)")
    return concat_mp4


# ── Step 3 : combine video + music ───────────────────────────────────
def combine(video):
    print("▸ Mix audio + video…")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(MUSIC),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(FINAL),
    ], check=True, capture_output=True)
    print(f"  ✓ {FINAL} ({FINAL.stat().st_size/(1024*1024):.1f} MB)")


if __name__ == "__main__":
    if not HOOK.exists() or not FULL.exists():
        raise SystemExit("Videos manquantes — lance record_plume_v3.py et hook_15s.py d'abord")
    build_music()
    concat = concat_videos()
    combine(concat)
    print(f"\n✓ FINAL: {FINAL}")
