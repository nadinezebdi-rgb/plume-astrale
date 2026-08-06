#!/usr/bin/env python3
"""Assemble a pedagogical 60s TikTok video from real plume-astrale.fr screenshots.

Message: 'Ton commentaire ne suffit pas — crée ton compte gratuit sur plume-astrale.fr'.

Uses:
  - 13 real screenshots 720×1280 (portrait)
  - 9 TTS chapters (voice Nova FR)
  - 1 Sora clip (Ch5 emotional peak) for scene 8
  - Ken Burns effect (slow zoom) on each screenshot
  - Bold subtitles overlaid in the safe zone
  - Bottom pill with URL + arrow highlights on key CTAs

Output: /app/backend/cache/demo_final/plume_tiktok_v2.mp4
"""
import subprocess
from pathlib import Path

SHOTS = Path('/app/backend/cache/plume_shots')
TTS = Path('/app/backend/cache/tts_v2')
SORA = Path('/app/backend/cache/sora_demo')
OUT_DIR = Path('/app/backend/cache/demo_final')
OUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL = OUT_DIR / 'plume_tiktok_v2.mp4'
TMP = OUT_DIR / '_v2'
TMP.mkdir(exist_ok=True)

# ─── Font paths ─────────────────────────────────────────────
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
FONT_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

# ─── Scenes (source, duration, subtitle, ken_burns_direction, tts) ─
# source_type: 'img' | 'video'
SCENES = [
    # ── 1. HOOK — 5s
    {
        'label': 's1_hook', 'src_type': 'img',
        'src': SHOTS / '02_landing_offer.png',   # neutral BG
        'dur': 5.0, 'kb': 'zoom_in',
        'subtitle': "Ton signe en commentaire\nne suffit pas.",
        'sub_size': 62, 'sub_color': 'white',
        'sub_box': 'red@0.85',
        'tts': TTS / '01_hook.mp3',
    },
    # ── 2. LANDING — 5s
    {
        'label': 's2_landing', 'src_type': 'img',
        'src': SHOTS / '01_landing_hero.png',
        'dur': 5.0, 'kb': 'zoom_in',
        'subtitle': "plume-astrale.fr",
        'sub_size': 70, 'sub_color': '0xE8C766',
        'sub_box': 'black@0.6',
        'tts': TTS / '02_landing.mp3',
    },
    # ── 3. SIGNUP — 6s
    {
        'label': 's3_signup', 'src_type': 'img',
        'src': SHOTS / '04_signup_form.png',
        'dur': 6.0, 'kb': 'zoom_in',
        'subtitle': "Crée ton compte gratuit\n→ 20 crédits offerts",
        'sub_size': 58, 'sub_color': '0xE8C766',
        'sub_box': 'black@0.7',
        'tts': TTS / '03_signup.mp3',
    },
    # ── 4. MON ACCUEIL — 6s
    {
        'label': 's4_accueil', 'src_type': 'img',
        'src': SHOTS / '06_mon_accueil.png',
        'dur': 6.0, 'kb': 'zoom_out',
        'subtitle': "Ton espace personnel",
        'sub_size': 62, 'sub_color': 'white',
        'sub_box': 'black@0.7',
        'tts': TTS / '04_accueil.mp3',
    },
    # ── 5. CHAT SOLENA — 8s
    {
        'label': 's5_solena', 'src_type': 'img',
        'src': SHOTS / '07_chat_solena.png',
        'dur': 8.0, 'kb': 'zoom_in',
        'subtitle': "💬 Discute avec Soléna\npas un chatbot",
        'sub_size': 60, 'sub_color': 'white',
        'sub_box': '0x6BA9A2@0.85',
        'tts': TTS / '05_solena.mp3',
    },
    # ── 6. HOROSCOPE — 7s
    {
        'label': 's6_horoscope', 'src_type': 'img',
        'src': SHOTS / '13_quotidien.png',
        'dur': 7.0, 'kb': 'zoom_out',
        'subtitle': "Ton horoscope du jour\ncalculé sur TON ciel",
        'sub_size': 58, 'sub_color': 'white',
        'sub_box': 'black@0.7',
        'tts': TTS / '06_horoscope.mp3',
    },
    # ── 7. ANALYSES — 8s (montage rapide)
    # For simplicity, use numerologie shot; could be a fast crossfade later
    {
        'label': 's7_analyses', 'src_type': 'img',
        'src': SHOTS / '10_numerologie.png',
        'dur': 4.0, 'kb': 'zoom_in',
        'subtitle': "Ta numérologie",
        'sub_size': 62, 'sub_color': 'white',
        'sub_box': 'black@0.7',
        'tts': None,  # part 1 of 07_analyses.mp3 (split later or use full)
    },
    {
        'label': 's7b_tarot', 'src_type': 'img',
        'src': SHOTS / '11_tarot.png',
        'dur': 4.0, 'kb': 'zoom_out',
        'subtitle': "Tes tirages",
        'sub_size': 62, 'sub_color': 'white',
        'sub_box': 'black@0.7',
        'tts': TTS / '07_analyses.mp3',
    },
    # ── 8. EMOTIONAL SORA — 8s
    {
        'label': 's8_emotion', 'src_type': 'video',
        'src': SORA / 'sora5_reading_pro.mp4',
        'dur': 8.0, 'kb': None,
        'subtitle': "Quand une lecture\ncite ton prénom...",
        'sub_size': 58, 'sub_color': 'white',
        'sub_box': 'black@0.5',
        'tts': TTS / '08_emotion.mp3',
    },
    # ── 9. CTA — 7s
    {
        'label': 's9_cta', 'src_type': 'img',
        'src': SHOTS / '01_landing_hero.png',
        'dur': 7.0, 'kb': 'zoom_out',
        'subtitle': "plume-astrale.fr\n✨ Lien en bio ✨",
        'sub_size': 68, 'sub_color': '0xE8C766',
        'sub_box': 'black@0.75',
        'tts': TTS / '09_cta.mp3',
    },
]


def kb_filter(direction, duration):
    """Ken Burns effect: slow zoom in/out with slight pan.
    Returns ffmpeg vf snippet."""
    fps = 25
    frames = int(duration * fps)
    if direction == 'zoom_in':
        # Zoom from 1.0 to 1.15
        return (f"scale=w=8000:h=-1,zoompan=z='min(zoom+0.0015,1.15)':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=720x1280:fps={fps}")
    elif direction == 'zoom_out':
        # Zoom from 1.15 to 1.0
        return (f"scale=w=8000:h=-1,zoompan=z='if(lte(zoom,1.0),1.15,zoom-0.0015)':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=720x1280:fps={fps}")
    return "scale=720:1280"


def escape_text(s):
    return (s.replace('\\', '\\\\')
             .replace(':', '\\:')
             .replace(',', '\\,')
             .replace("'", '\u2019'))


def drawtext(text, size, color, box_color):
    esc = escape_text(text)
    return (f"drawtext=text='{esc}':"
            f"fontfile={FONT_BOLD}:"
            f"fontsize={size}:fontcolor={color}:"
            f"borderw=2:bordercolor=black@0.6:"
            f"x=(w-text_w)/2:y=h*0.70:"
            f"box=1:boxcolor={box_color}:boxborderw=24:"
            f"line_spacing=14")


def run(cmd, label):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("STDERR:", r.stderr[-800:])
        raise SystemExit(f"ffmpeg failed at {label}")
    print(f"  [✓] {label}")


# ─── Build each scene ────────────────────────────────────────
seg_files = []
for scene in SCENES:
    seg = TMP / f"{scene['label']}.mp4"

    # Video source
    if scene['src_type'] == 'img':
        kb = kb_filter(scene.get('kb'), scene['dur'])
        video_input = ['-loop', '1', '-t', str(scene['dur']), '-i', str(scene['src'])]
        vf = f"{kb},{drawtext(scene['subtitle'], scene['sub_size'], scene['sub_color'], scene['sub_box'])}"
    else:  # video
        video_input = ['-t', str(scene['dur']), '-i', str(scene['src'])]
        vf = f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,{drawtext(scene['subtitle'], scene['sub_size'], scene['sub_color'], scene['sub_box'])}"

    # Audio: use TTS if present, else silence
    if scene.get('tts') and scene['tts'].exists():
        audio_input = ['-i', str(scene['tts'])]
        audio_map = ['-map', '1:a', '-af', 'apad,volume=1.2']
    else:
        # silence of scene duration
        audio_input = ['-f', 'lavfi', '-t', str(scene['dur']), '-i', 'anullsrc=r=44100:cl=mono']
        audio_map = ['-map', '1:a']

    cmd = [
        'ffmpeg', '-y',
        *video_input,
        *audio_input,
        '-t', str(scene['dur']),
        '-vf', vf,
        '-map', '0:v',
        *audio_map,
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
        '-c:a', 'aac', '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-r', '25',
        str(seg),
    ]
    run(cmd, scene['label'])
    seg_files.append(seg)


# ─── Concat all scenes ───────────────────────────────────────
concat_txt = TMP / 'concat.txt'
concat_txt.write_text('\n'.join(f"file '{s}'" for s in seg_files))

cmd = [
    'ffmpeg', '-y',
    '-f', 'concat', '-safe', '0', '-i', str(concat_txt),
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
    '-c:a', 'aac', '-b:a', '192k',
    '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart',
    str(FINAL),
]
run(cmd, 'CONCAT')

size_mb = FINAL.stat().st_size / (1024 * 1024)
print(f"\n✅ FINAL: {FINAL} ({size_mb:.1f} MB)")
