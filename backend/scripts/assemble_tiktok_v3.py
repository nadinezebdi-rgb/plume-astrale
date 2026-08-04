#!/usr/bin/env python3
"""TikTok pedagogical video v3 — WITHOUT voice-off, WITH joyful music, +2 PDF shots.

Changes from v2:
  - No voice-over audio (silence in video track — music takes over)
  - Add Kabbale cover + page 8 (personalized "Sophie") in the analyses scene
  - Overlay Cheery Monday (Kevin MacLeod, CC BY 3.0) as background music
  - Keep all subtitles / text overlays
"""
import subprocess
from pathlib import Path

SHOTS = Path('/app/backend/cache/plume_shots')
SORA = Path('/app/backend/cache/sora_demo')
MUSIC = Path('/app/backend/cache/music/cheery.mp3')
OUT_DIR = Path('/app/backend/cache/demo_final')
OUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL = OUT_DIR / 'plume_tiktok_v3.mp4'
TMP = OUT_DIR / '_v3'
TMP.mkdir(exist_ok=True)

FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'


SCENES = [
    {'label': 's1_hook', 'src_type': 'img',
     'src': SHOTS / '02_landing_offer.png', 'dur': 4.0, 'kb': 'zoom_in',
     'subtitle': "Ton signe en commentaire\nne suffit pas.",
     'sub_size': 62, 'sub_color': 'white', 'sub_box': 'red@0.85'},

    {'label': 's2_landing', 'src_type': 'img',
     'src': SHOTS / '01_landing_hero.png', 'dur': 4.0, 'kb': 'zoom_in',
     'subtitle': "plume-astrale.fr",
     'sub_size': 72, 'sub_color': '0xE8C766', 'sub_box': 'black@0.6'},

    {'label': 's3_signup', 'src_type': 'img',
     'src': SHOTS / '04_signup_form.png', 'dur': 5.0, 'kb': 'zoom_in',
     'subtitle': "Crée ton compte gratuit\n→ 20 crédits offerts",
     'sub_size': 58, 'sub_color': '0xE8C766', 'sub_box': 'black@0.7'},

    {'label': 's4_accueil', 'src_type': 'img',
     'src': SHOTS / '06_mon_accueil.png', 'dur': 5.0, 'kb': 'zoom_out',
     'subtitle': "Ton espace personnel",
     'sub_size': 64, 'sub_color': 'white', 'sub_box': 'black@0.7'},

    {'label': 's5_solena', 'src_type': 'img',
     'src': SHOTS / '07_chat_solena.png', 'dur': 6.0, 'kb': 'zoom_in',
     'subtitle': "💬 Discute avec Soléna\npas un chatbot",
     'sub_size': 60, 'sub_color': 'white', 'sub_box': '0x6BA9A2@0.85'},

    {'label': 's6_horoscope', 'src_type': 'img',
     'src': SHOTS / '13_quotidien.png', 'dur': 5.0, 'kb': 'zoom_out',
     'subtitle': "Ton horoscope du jour\ncalculé sur TON ciel",
     'sub_size': 58, 'sub_color': 'white', 'sub_box': 'black@0.7'},

    {'label': 's7a_numero', 'src_type': 'img',
     'src': SHOTS / '10_numerologie.png', 'dur': 3.0, 'kb': 'zoom_in',
     'subtitle': "Ta numérologie",
     'sub_size': 64, 'sub_color': 'white', 'sub_box': 'black@0.7'},

    {'label': 's7b_tarot', 'src_type': 'img',
     'src': SHOTS / '11_tarot.png', 'dur': 3.0, 'kb': 'zoom_out',
     'subtitle': "Tes tirages",
     'sub_size': 64, 'sub_color': 'white', 'sub_box': 'black@0.7'},

    # ── NEW · Real PDF shots ────────────────────────────
    {'label': 's7c_karma_cover', 'src_type': 'img',
     'src': SHOTS / 'karma_v2_p-1.png', 'dur': 3.5, 'kb': 'zoom_in',
     'subtitle': "Ton analyse karmique",
     'sub_size': 60, 'sub_color': '0xE8C766', 'sub_box': 'black@0.65'},

    {'label': 's7d_kabbale_cover', 'src_type': 'img',
     'src': SHOTS / 'kabbale_v2_p-01.png', 'dur': 3.5, 'kb': 'zoom_in',
     'subtitle': "Ton Arbre de Vie\nkabbalistique",
     'sub_size': 58, 'sub_color': '0xE8C766', 'sub_box': 'black@0.65'},

    {'label': 's7e_kabbale_perso', 'src_type': 'img',
     'src': SHOTS / 'karma_v2_p-4.png', 'dur': 4.5, 'kb': 'zoom_in',
     'subtitle': "Écrit pour TOI\nprénom + date interpolés",
     'sub_size': 56, 'sub_color': 'white', 'sub_box': 'black@0.7'},

    # ── Emotion + CTA ───────────────────────────────────
    {'label': 's8_emotion', 'src_type': 'video',
     'src': SORA / 'sora5_reading_pro.mp4', 'dur': 6.0, 'kb': None,
     'subtitle': "Quand une lecture\ncite ton prénom...",
     'sub_size': 58, 'sub_color': 'white', 'sub_box': 'black@0.5'},

    {'label': 's9_cta', 'src_type': 'img',
     'src': SHOTS / '01_landing_hero.png', 'dur': 6.0, 'kb': 'zoom_out',
     'subtitle': "plume-astrale.fr\n✨ Lien en bio ✨",
     'sub_size': 68, 'sub_color': '0xE8C766', 'sub_box': 'black@0.75'},
]


def kb_filter(direction, duration):
    fps = 25
    frames = int(duration * fps)
    if direction == 'zoom_in':
        return (f"scale=w=8000:h=-1,zoompan=z='min(zoom+0.0015,1.15)':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=720x1280:fps={fps}")
    elif direction == 'zoom_out':
        return (f"scale=w=8000:h=-1,zoompan=z='if(lte(zoom,1.0),1.15,zoom-0.0015)':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=720x1280:fps={fps}")
    return "scale=720:1280"


def escape_text(s):
    return (s.replace('\\', '\\\\').replace(':', '\\:')
             .replace(',', '\\,').replace("'", '\u2019'))


WATERMARK = (
    f"drawtext=text='P L U M E   A S T R A L E':"
    f"fontfile={FONT_BOLD}:"
    f"fontsize=18:fontcolor=0xE8C766@0.85:"
    f"borderw=1:bordercolor=black@0.5:"
    f"x=w-text_w-24:y=28"
)


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
        print("STDERR:", r.stderr[-600:])
        raise SystemExit(f"ffmpeg failed at {label}")
    print(f"  [✓] {label}")


# ─── Build each scene (silent video only) ─────────────
seg_files = []
total_dur = 0
for scene in SCENES:
    seg = TMP / f"{scene['label']}.mp4"
    if scene['src_type'] == 'img':
        kb = kb_filter(scene.get('kb'), scene['dur'])
        video_input = ['-loop', '1', '-t', str(scene['dur']), '-i', str(scene['src'])]
        vf = f"{kb},{drawtext(scene['subtitle'], scene['sub_size'], scene['sub_color'], scene['sub_box'])},{WATERMARK}"
    else:
        video_input = ['-t', str(scene['dur']), '-i', str(scene['src'])]
        vf = f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,{drawtext(scene['subtitle'], scene['sub_size'], scene['sub_color'], scene['sub_box'])},{WATERMARK}"
    cmd = [
        'ffmpeg', '-y', *video_input,
        '-t', str(scene['dur']),
        '-vf', vf,
        '-an',  # No audio track on segments
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
        '-pix_fmt', 'yuv420p', '-r', '25',
        str(seg),
    ]
    run(cmd, scene['label'])
    seg_files.append(seg)
    total_dur += scene['dur']

# ─── Concat silent video track ─────────────────────────
concat_txt = TMP / 'concat.txt'
concat_txt.write_text('\n'.join(f"file '{s}'" for s in seg_files))
silent_out = TMP / '_silent.mp4'
cmd = [
    'ffmpeg', '-y',
    '-f', 'concat', '-safe', '0', '-i', str(concat_txt),
    '-c', 'copy',
    str(silent_out),
]
run(cmd, 'concat_silent')
print(f"  → silent duration: {total_dur:.1f}s")

# ─── Overlay music with volume fade in/out ─────────────
# Music at 25% volume, fade out over last 2 seconds
music_filter = f"volume=0.25,afade=t=in:d=0.5,afade=t=out:st={total_dur-2}:d=2"
cmd = [
    'ffmpeg', '-y',
    '-i', str(silent_out),
    '-i', str(MUSIC),
    '-filter_complex',
    f"[1:a]{music_filter}[music]",
    '-map', '0:v', '-map', '[music]',
    '-t', str(total_dur),
    '-c:v', 'copy',
    '-c:a', 'aac', '-b:a', '192k',
    '-movflags', '+faststart',
    '-shortest',
    str(FINAL),
]
run(cmd, 'mix_music')

size_mb = FINAL.stat().st_size / (1024 * 1024)
print(f"\n✅ FINAL: {FINAL} ({size_mb:.1f} MB, {total_dur:.0f}s)")
