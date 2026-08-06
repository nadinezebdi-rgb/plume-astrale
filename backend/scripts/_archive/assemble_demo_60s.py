#!/usr/bin/env python3
"""Assemble a 60s vertical demo montage from Sora clips + TTS voice-over.

Structure (60s total):
  0:00-0:03  Hook          → text card + TTS 01
  0:03-0:10  Chapter 1     → sora1_claire_discovers (8s trim to 7s) + TTS 02
  0:10-0:18  Chapter 2     → sora2_solena_portrait (8s) + TTS 03
  0:18-0:28  Chapter 3     → sora3_claire_chat (8s slow) + TTS 04
  0:28-0:38  Chapter 4     → sora4_email_arrives (8s) + TTS 05
  0:38-0:50  Chapter 5     → sora5_reading_pro (8s pro) + TTS 06
  0:50-0:60  CTA           → sora6_community (8s) + TTS 07 + logo overlay

Output: /app/backend/cache/demo_final/plume_astrale_demo_60s.mp4
"""
import subprocess
import sys
from pathlib import Path

SORA_DIR = Path('/app/backend/cache/sora_demo')
TTS_DIR = Path('/app/backend/cache/tts_demo')
OUT_DIR = Path('/app/backend/cache/demo_final')
OUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL = OUT_DIR / 'plume_astrale_demo_60s.mp4'
TMP = OUT_DIR / '_tmp'
TMP.mkdir(exist_ok=True)


def run(cmd, label):
    print(f"  [{label}]  {' '.join(str(x) for x in cmd[:6])}...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("STDERR:", r.stderr[-800:])
        raise SystemExit(f"ffmpeg failed at {label}")


# ─── SEGMENTS DEFINITION ──────────────────────────────────────────
# (label, video_file, video_duration, tts_file, subtitle)
SEGMENTS = [
    ('01_hook',
     None,  # No sora video for hook, we build a text card
     3.0,
     TTS_DIR / '01_hook.mp3',
     "87% des horoscopes\nsont écrits par des bots."),
    ('02_arrivee',
     SORA_DIR / 'sora1_claire_discovers.mp4',
     7.0,
     TTS_DIR / '02_arrivee.mp3',
     "Elle a 43 ans.\nElle trouve une plume."),
    ('03_lectures',
     SORA_DIR / 'sora2_solena_portrait.mp4',
     8.0,
     TTS_DIR / '03_cinq_lectures.mp3',
     "5 lectures. 90 pages. Toi."),
    ('04_chat',
     SORA_DIR / 'sora3_claire_chat.mp4',
     10.0,   # extend chat slower
     TTS_DIR / '04_chat.mp3',
     "L'IA détecte 3 mots.\nSoléna répond en 3 min."),
    ('05_achat',
     SORA_DIR / 'sora4_email_arrives.mp4',
     10.0,
     TTS_DIR / '05_achat.mp3',
     "97 €.\nLivraison en 5 minutes."),
    ('06_livraison',
     SORA_DIR / 'sora5_reading_pro.mp4',
     12.0,
     TTS_DIR / '06_livraison.mp3',
     "Ce paragraphe n'existait pas\nil y a 6 minutes."),
    ('07_cta',
     SORA_DIR / 'sora6_community.mp4',
     10.0,
     TTS_DIR / '07_cta.mp3',
     "Plume Astrale\nplume-astrale.fr"),
]

# ─── STEP 1 · Build each segment individually ─────────────────────
segments_out = []
for label, video, duration, tts, subtitle in SEGMENTS:
    seg_out = TMP / f'seg_{label}.mp4'

    # Escape subtitle text for drawtext (: , \ ')
    sub = subtitle.replace('\\', '\\\\').replace(':', '\\:').replace(',', '\\,').replace("'", "\u2019")

    # Video source: real Sora clip OR generated black card
    if video and video.exists():
        # Trim/slow Sora clip to fit duration
        sora_native = 8.0
        if duration > sora_native:
            # slow motion via setpts
            speed = sora_native / duration
            vf_speed = f"setpts={1/speed}*PTS,"
        elif duration < sora_native:
            vf_speed = ""  # will be trimmed by -t
        else:
            vf_speed = ""
        video_input = ['-stream_loop', '0', '-i', str(video)]
    else:
        # Solid card 720x1280 with subtle gradient
        video_input = ['-f', 'lavfi', '-i',
                       f'color=c=0x1A1A2E:s=720x1280:d={duration},format=yuv420p']
        vf_speed = ""

    # Overlay subtitle at 78% height (safe zone above TikTok UI)
    drawtext = (
        f"drawtext=text='{sub}':"
        f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:"
        f"fontsize=50:fontcolor=white:"
        f"borderw=2:bordercolor=black@0.5:"
        f"x=(w-text_w)/2:y=h*0.72:"
        f"box=1:boxcolor=black@0.35:boxborderw=20:"
        f"line_spacing=12"
    )

    vf = f"{vf_speed}scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,{drawtext}"

    cmd = [
        'ffmpeg', '-y',
        *video_input,
        '-i', str(tts),
        '-t', str(duration),
        '-vf', vf,
        '-af', 'apad',  # pad audio with silence
        '-map', '0:v', '-map', '1:a',
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
        '-c:a', 'aac', '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        str(seg_out),
    ]
    run(cmd, label)
    segments_out.append(seg_out)

# ─── STEP 2 · Concat all segments ─────────────────────────────────
concat_txt = TMP / 'concat.txt'
concat_txt.write_text('\n'.join(f"file '{s}'" for s in segments_out))

cmd = [
    'ffmpeg', '-y',
    '-f', 'concat', '-safe', '0', '-i', str(concat_txt),
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
    '-c:a', 'aac', '-b:a', '192k',
    '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart',
    str(FINAL),
]
run(cmd, 'concat')

size_mb = FINAL.stat().st_size / (1024 * 1024)
print(f"\n✅ FINAL: {FINAL} ({size_mb:.1f} MB)")
