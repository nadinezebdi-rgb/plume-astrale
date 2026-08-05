#!/usr/bin/env python3
"""Generate 3 TikTok hook variants for A/B testing on the same body video.

Each hook = 4s at the start, replaces scene 1 of v3.
Body = scenes 2-9 from v3 (~54s), reused verbatim.

Variants:
  A · Chiffre choc     — "87%" en gros, transition brutale, ambiance intrigante
  B · Question         — question ouverte, focus doux, tempo introspectif
  C · Émotion          — extrait Sora Claire+larme, punchline émotionnelle

Output:
  /app/backend/cache/demo_final/plume_tiktok_hookA_chiffre.mp4
  /app/backend/cache/demo_final/plume_tiktok_hookB_question.mp4
  /app/backend/cache/demo_final/plume_tiktok_hookC_emotion.mp4
"""
import subprocess
from pathlib import Path

SHOTS = Path('/app/backend/cache/plume_shots')
SORA = Path('/app/backend/cache/sora_demo')
MUSIC = Path('/app/backend/cache/music/cheery.mp3')
V3 = Path('/app/backend/cache/demo_final/plume_tiktok_v3.mp4')
OUT_DIR = Path('/app/backend/cache/demo_final')
TMP = OUT_DIR / '_hooks'
TMP.mkdir(parents=True, exist_ok=True)

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
BODY_START = 4.0  # First hook of v3 lasted 4 seconds

WATERMARK = (
    f"drawtext=text='P L U M E   A S T R A L E':"
    f"fontfile={FONT}:"
    f"fontsize=18:fontcolor=0xE8C766@0.85:"
    f"borderw=1:bordercolor=black@0.5:"
    f"x=w-text_w-24:y=28"
)


def esc(s):
    return s.replace('\\', '\\\\').replace(':', '\\:').replace(',', '\\,').replace("'", '\u2019')


def run(cmd, label):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"STDERR ({label}):", r.stderr[-500:])
        raise SystemExit(1)
    print(f"  [✓] {label}")


# ─── HOOK A · Chiffre choc ─────────────────────────────────
# Écran navy, "87%" en énorme, transition rouge, sous-titre choc
hook_a = TMP / 'hookA_chiffre.mp4'
big_number = (
    f"drawtext=text='87%':"
    f"fontfile={FONT}:fontsize=280:fontcolor=0xE8C766:"
    f"borderw=4:bordercolor=black:"
    f"x=(w-text_w)/2:y=h*0.32:"
    f"enable='between(t,0.4,4)'"
)
line1 = (
    f"drawtext=text='des horoscopes':"
    f"fontfile={FONT}:fontsize=46:fontcolor=white:"
    f"x=(w-text_w)/2:y=h*0.60:"
    f"enable='between(t,1.0,4)'"
)
line2 = (
    f"drawtext=text='sont faits par des BOTS':"
    f"fontfile={FONT}:fontsize=46:fontcolor=0xff6b6b:"
    f"borderw=2:bordercolor=black:"
    f"x=(w-text_w)/2:y=h*0.66:"
    f"enable='between(t,1.6,4)'"
)
cmd = [
    '/usr/bin/ffmpeg', '-y',
    '-f', 'lavfi', '-i', 'color=c=0x0a0a1a:s=720x1280:d=4,format=yuv420p',
    '-vf', f"{big_number},{line1},{line2},{WATERMARK}",
    '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
    '-pix_fmt', 'yuv420p', '-r', '25',
    str(hook_a),
]
run(cmd, 'hook A · chiffre')


# ─── HOOK B · Question ─────────────────────────────────────
# Landing avec zoom + question posée en italique doré
hook_b = TMP / 'hookB_question.mp4'
question = (
    f"drawtext=text='Pourquoi ton horoscope':"
    f"fontfile={FONT}:fontsize=54:fontcolor=white:"
    f"borderw=2:bordercolor=black@0.7:"
    f"x=(w-text_w)/2:y=h*0.30:"
    f"box=1:boxcolor=black@0.65:boxborderw=18"
)
question2 = (
    f"drawtext=text='ne parle jamais de TOI ?':"
    f"fontfile={FONT}:fontsize=56:fontcolor=0xE8C766:"
    f"borderw=2:bordercolor=black@0.7:"
    f"x=(w-text_w)/2:y=h*0.37:"
    f"box=1:boxcolor=black@0.65:boxborderw=18:"
    f"enable='between(t,1.0,4)'"
)
kb = (
    "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
    "zoompan=z='min(zoom+0.0025,1.15)':"
    "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=100:s=720x1280:fps=25"
)
cmd = [
    '/usr/bin/ffmpeg', '-y',
    '-loop', '1', '-t', '4', '-i', str(SHOTS / '01_landing_hero.png'),
    '-vf', f"{kb},{question},{question2},{WATERMARK}",
    '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
    '-pix_fmt', 'yuv420p', '-r', '25',
    str(hook_b),
]
run(cmd, 'hook B · question')


# ─── HOOK C · Émotion ──────────────────────────────────────
# Sora Claire+larme + punchline émotionnelle
hook_c = TMP / 'hookC_emotion.mp4'
line1c = (
    f"drawtext=text='Ce paragraphe':"
    f"fontfile={FONT}:fontsize=54:fontcolor=white:"
    f"borderw=2:bordercolor=black@0.7:"
    f"x=(w-text_w)/2:y=h*0.68:"
    f"box=1:boxcolor=black@0.55:boxborderw=18"
)
line2c = (
    f"drawtext=text='l\u2019a fait pleurer.':"
    f"fontfile={FONT}:fontsize=58:fontcolor=0xE8C766:"
    f"borderw=2:bordercolor=black@0.7:"
    f"x=(w-text_w)/2:y=h*0.75:"
    f"box=1:boxcolor=black@0.55:boxborderw=18:"
    f"enable='between(t,1.2,4)'"
)
cmd = [
    '/usr/bin/ffmpeg', '-y',
    '-t', '4', '-i', str(SORA / 'sora5_reading_pro.mp4'),
    '-vf', f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,{line1c},{line2c},{WATERMARK}",
    '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
    '-pix_fmt', 'yuv420p', '-r', '25',
    str(hook_c),
]
run(cmd, 'hook C · émotion')


# ─── BODY · scènes 2-9 de v3 (à partir de 4s) ─────────────
body = TMP / '_body.mp4'
cmd = [
    '/usr/bin/ffmpeg', '-y',
    '-ss', str(BODY_START), '-i', str(V3),
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
    '-c:a', 'aac', '-b:a', '192k',
    '-pix_fmt', 'yuv420p', '-r', '25',
    str(body),
]
run(cmd, 'extract body from v3')


# ─── ASSEMBLE 3 versions ──────────────────────────────────
for label, hook_file in [('A_chiffre', hook_a), ('B_question', hook_b), ('C_emotion', hook_c)]:
    # Concat hook (silent) + body — need matching audio streams. Silence for hook.
    hook_with_silence = TMP / f'_hook_{label}_aud.mp4'
    cmd = [
        '/usr/bin/ffmpeg', '-y',
        '-i', str(hook_file),
        '-f', 'lavfi', '-t', '4', '-i', 'anullsrc=r=44100:cl=stereo',
        '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        str(hook_with_silence),
    ]
    run(cmd, f'hook {label} + silence')

    # Concat
    concat_txt = TMP / f'concat_{label}.txt'
    concat_txt.write_text(f"file '{hook_with_silence}'\nfile '{body}'\n")
    silent_final = TMP / f'_final_silent_{label}.mp4'
    cmd = [
        '/usr/bin/ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', str(concat_txt),
        '-c', 'copy',
        str(silent_final),
    ]
    run(cmd, f'concat {label} video')

    # Overlay music (Cheery Monday) on the full 58s output
    final = OUT_DIR / f'plume_tiktok_hook{label}.mp4'
    cmd = [
        '/usr/bin/ffmpeg', '-y',
        '-i', str(silent_final),
        '-i', str(MUSIC),
        '-filter_complex', "[1:a]volume=0.25,afade=t=in:d=0.5,afade=t=out:st=56:d=2[music]",
        '-map', '0:v', '-map', '[music]',
        '-t', '58',
        '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart', '-shortest',
        str(final),
    ]
    run(cmd, f'final {label}')

    size_mb = final.stat().st_size / (1024 * 1024)
    print(f"    → {final.name} ({size_mb:.1f} MB)")
