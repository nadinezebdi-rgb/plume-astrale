#!/usr/bin/env python3
"""15s Instagram Reels teaser — condensed from Hook A · Chiffre choc.

Structure (15s exactly):
  0-3s   : Hook 87% (accelerated)
  3-6s   : Chat Soléna
  6-9s   : PDF Kabbale personnalisé (Sophie)
  9-12s  : Sora Claire émotion (larme)
  12-15s : CTA plume-astrale.fr
"""
import subprocess
from pathlib import Path

SHOTS = Path('/app/backend/cache/plume_shots')
SORA = Path('/app/backend/cache/sora_demo')
MUSIC = Path('/app/backend/cache/music/cheery.mp3')
OUT_DIR = Path('/app/backend/cache/demo_final')
TMP = OUT_DIR / '_teaser'
TMP.mkdir(parents=True, exist_ok=True)

FONT = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
FFMPEG = '/usr/bin/ffmpeg'

WATERMARK = (
    f"drawtext=text='P L U M E   A S T R A L E':"
    f"fontfile={FONT}:fontsize=18:fontcolor=0xE8C766@0.85:"
    f"borderw=1:bordercolor=black@0.5:"
    f"x=w-text_w-24:y=28"
)


def esc(s):
    return s.replace('\\', '\\\\').replace(':', '\\:').replace(',', '\\,').replace("'", '\u2019')


def drawtext(text, size, color, box_color, y_ratio=0.70):
    lines = text.split('\n')
    # Combine into single drawtext with line breaks if needed
    e = esc(text)
    return (f"drawtext=text='{e}':fontfile={FONT}:"
            f"fontsize={size}:fontcolor={color}:"
            f"borderw=2:bordercolor=black@0.6:"
            f"x=(w-text_w)/2:y=h*{y_ratio}:"
            f"box=1:boxcolor={box_color}:boxborderw=22:"
            f"line_spacing=12")


def run(cmd, label):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"STDERR ({label}):", r.stderr[-500:])
        raise SystemExit(1)
    print(f"  [✓] {label}")


# ─── Scene 1 (3s) · Hook 87% ─────────────────────────
scene1 = TMP / 's1.mp4'
big_87 = (
    f"drawtext=textfile=/tmp/txt_87.txt:fontfile={FONT}:"
    f"fontsize=280:fontcolor=0xE8C766:borderw=4:bordercolor=black:"
    f"x=(w-text_w)/2:y=h*0.28:enable='between(t,0.2,3)'"
)
sub1 = drawtext("des horoscopes\nsont faits par des BOTS", 40, 'white', 'red@0.85', 0.60)
Path('/tmp/txt_87.txt').write_text('87%')
cmd = [FFMPEG, '-y',
       '-f', 'lavfi', '-i', 'color=c=0x0a0a1a:s=720x1280:d=3,format=yuv420p',
       '-vf', f"{big_87},{sub1},{WATERMARK}",
       '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
       '-pix_fmt', 'yuv420p', '-r', '25', str(scene1)]
run(cmd, 'scene 1 · hook 87%')


# ─── Scene 2 (3s) · Chat Soléna ─────────────────────
scene2 = TMP / 's2.mp4'
kb_in = ("scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
         "zoompan=z='min(zoom+0.003,1.15)':x='iw/2-(iw/zoom/2)':"
         "y='ih/2-(ih/zoom/2)':d=75:s=720x1280:fps=25")
sub2 = drawtext("Discute avec Soléna\npas un chatbot", 52, 'white', '0x6BA9A2@0.9', 0.70)
cmd = [FFMPEG, '-y',
       '-loop', '1', '-t', '3', '-i', str(SHOTS / '07_chat_solena.png'),
       '-vf', f"{kb_in},{sub2},{WATERMARK}",
       '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
       '-pix_fmt', 'yuv420p', '-r', '25', str(scene2)]
run(cmd, 'scene 2 · chat')


# ─── Scene 3 (3s) · PDF Kabbale Sophie ──────────────
scene3 = TMP / 's3.mp4'
sub3 = drawtext("Écrit pour TOI\nprénom + date", 50, '0xE8C766', 'black@0.72', 0.70)
cmd = [FFMPEG, '-y',
       '-loop', '1', '-t', '3', '-i', str(SHOTS / 'kabbale_v2_p-01.png'),
       '-vf', f"{kb_in},{sub3},{WATERMARK}",
       '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
       '-pix_fmt', 'yuv420p', '-r', '25', str(scene3)]
run(cmd, 'scene 3 · PDF Sophie')


# ─── Scene 4 (3s) · Sora émotion ────────────────────
scene4 = TMP / 's4.mp4'
sub4 = drawtext("Quand ça te touche...", 52, 'white', 'black@0.55', 0.75)
cmd = [FFMPEG, '-y',
       '-t', '3', '-i', str(SORA / 'sora5_reading_pro.mp4'),
       '-vf', f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,{sub4},{WATERMARK}",
       '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
       '-pix_fmt', 'yuv420p', '-r', '25', str(scene4)]
run(cmd, 'scene 4 · émotion')


# ─── Scene 5 (3s) · CTA ─────────────────────────────
scene5 = TMP / 's5.mp4'
sub5 = drawtext("plume-astrale.fr\n✨ Lien en bio ✨", 60, '0xE8C766', 'black@0.75', 0.68)
kb_out = ("scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
          "zoompan=z='if(lte(zoom,1.0),1.15,zoom-0.003)':x='iw/2-(iw/zoom/2)':"
          "y='ih/2-(ih/zoom/2)':d=75:s=720x1280:fps=25")
cmd = [FFMPEG, '-y',
       '-loop', '1', '-t', '3', '-i', str(SHOTS / '01_landing_hero.png'),
       '-vf', f"{kb_out},{sub5},{WATERMARK}",
       '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
       '-pix_fmt', 'yuv420p', '-r', '25', str(scene5)]
run(cmd, 'scene 5 · CTA')


# ─── Concat + music ─────────────────────────────────
concat = TMP / 'concat.txt'
concat.write_text('\n'.join(f"file '{s}'" for s in [scene1, scene2, scene3, scene4, scene5]))
silent = TMP / '_silent.mp4'
cmd = [FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', str(concat),
       '-c', 'copy', str(silent)]
run(cmd, 'concat')

FINAL = OUT_DIR / 'plume_reels_teaser_15s.mp4'
cmd = [FFMPEG, '-y',
       '-i', str(silent),
       '-i', str(MUSIC),
       '-filter_complex', "[1:a]volume=0.30,afade=t=in:d=0.3,afade=t=out:st=13:d=2[music]",
       '-map', '0:v', '-map', '[music]',
       '-t', '15',
       '-c:v', 'copy',
       '-c:a', 'aac', '-b:a', '192k',
       '-movflags', '+faststart', '-shortest',
       str(FINAL)]
run(cmd, 'mix music')

size_mb = FINAL.stat().st_size / (1024 * 1024)
print(f"\n✅ FINAL: {FINAL} ({size_mb:.1f} MB)")
