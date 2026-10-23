#!/bin/bash
# Plume Astrale pitch video — v2
# - Elegant subtitles (Helvetica-like, no black blob, soft shadow)
# - Positioned at ~85% of height (lower)
# - Longer time on numbers slide (14 s)

set -e
cd /app/video_pitch_assets

mkdir -p build
for img in \
  shot_01_hero_desktop.jpeg \
  shot_03_pathways.jpeg \
  shot_04_theme_natal.jpeg \
  shot_06_synastrie.jpeg \
  shot_05_moncompte_exlibris.jpeg \
  shot_07_ex_libris_png.png \
  slide_market_validation.png \
  shot_admin_06_pdfs_envoyes.jpeg
do
  out="build/$(basename "$img" | sed 's/\.[^.]*$//').png"
  ffmpeg -y -loglevel error -i "$img" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#10182d,format=yuv420p" \
    -frames:v 1 "$out"
done

# Timeline aligned to actual spoken timings (54 s total)
# hero         0 →  6 s   "What if astrology / today?"
# pathways     6 → 11 s   "Meet Plume Astrale / 4 reading paths"
# theme-natal 11 → 15 s   "4 paths / Know yourself..."
# synastrie   15 → 19 s   "Explore a question / Your cycle"
# moncompte   19 → 26 s   "Each reading / 49-page / GPT-powered"
# ex-libris   26 → 37 s   "Natal 24€ / something unique / Your Ex Libris" ← MONEY
# validation  37 → 48 s   "183€ / 104 payments / 13× ROAS"             ← NUMBERS
# admin       48 → 54 s   "Stripe live / Validated / Plume Astrale"

cat > build/concat.txt <<EOF
file 'shot_01_hero_desktop.png'
duration 6
file 'shot_03_pathways.png'
duration 5
file 'shot_04_theme_natal.png'
duration 4
file 'shot_06_synastrie.png'
duration 4
file 'shot_05_moncompte_exlibris.png'
duration 7
file 'shot_07_ex_libris_png.png'
duration 11
file 'slide_market_validation.png'
duration 11
file 'shot_admin_06_pdfs_envoyes.png'
duration 6
file 'shot_admin_06_pdfs_envoyes.png'
EOF

# Subtitle style explained :
# - FontName=Arial          → readable, universally available
# - Fontsize=16             → discreet, ~22 px rendered (not shouting)
# - PrimaryColour=&HF7F3EAFF→ ivory (BGR + alpha)
# - BackColour=&H66101818FF → navy with 60% opacity (BGR + alpha, aa = 100 - 66hex ≈ 60%)
# - BorderStyle=3           → opaque filled box (vs 4 = per-line box; vs 1 = outline)
# - Outline=0, Shadow=1     → no hard outline, only soft shadow
# - MarginV=90              → distance from BOTTOM in pixels (bigger = HIGHER)
#                              → we want LOWER so use 55
# - Alignment=2             → bottom-center

ffmpeg -y -loglevel warning \
  -f concat -safe 0 -i build/concat.txt \
  -i voiceover_en.mp3 \
  -vf "fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#10182d,ass=plume_astrale_pitch_EN.ass" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 44100 \
  -shortest \
  plume_astrale_pitch_60s.mp4

echo "---"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 plume_astrale_pitch_60s.mp4
ls -la plume_astrale_pitch_60s.mp4
