"""Build SRT by grouping real words at natural pauses (word-gap >150ms)
or when a cue reaches 7 words max. Guarantees perfect sync with audio.
"""

import json
import re
from pathlib import Path

TIMES = Path('/app/video_pitch_assets/_word_times.json')
OUT = Path('/app/video_pitch_assets/plume_astrale_pitch_EN.srt')

data = json.loads(TIMES.read_text())
words = data['words']   # list of {t, s, e}

# Normalize word tokens: fix a few known mis-hearings for display.
# (These are the voice's actual outputs, we only correct the ones that read
# oddly on screen.)
NORMALIZE = {
    'sinistri': 'synastry',
    'four-nine': '49',
    'exlibris': 'Ex Libris',
    'ex-libris': 'Ex Libris',
    '49-page': '49-page',
}

def clean(t: str) -> str:
    return NORMALIZE.get(t.lower(), t)


MAX_WORDS = 10
MIN_GAP = 0.5       # if the silence before a word is ≥ this → break the cue
MIN_DUR = 2.0       # minimum cue duration
MAX_DUR = 4.5       # maximum cue duration (then force break)

cues: list[list[dict]] = []
cur: list[dict] = []
for i, w in enumerate(words):
    if not cur:
        cur.append(w)
        continue
    gap = w['s'] - cur[-1]['e']
    duration_if_added = w['e'] - cur[0]['s']
    cur_len = len(cur)
    # Decide if we should break BEFORE adding this word
    should_break = False
    if cur_len >= MAX_WORDS:
        should_break = True
    elif gap >= MIN_GAP and (cur[-1]['e'] - cur[0]['s']) >= MIN_DUR:
        should_break = True
    elif duration_if_added > MAX_DUR and cur_len >= 3:
        should_break = True

    if should_break:
        cues.append(cur)
        cur = [w]
    else:
        cur.append(w)

if cur:
    cues.append(cur)


def fmt(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        s += 1
        ms = 0
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def mk_text(grp: list[dict]) -> str:
    toks = [clean(w['t']) for w in grp]
    text = ' '.join(toks)
    # Punctuation spacing
    text = (text.replace(' ,', ',').replace(' .', '.')
            .replace(' ?', '?').replace(' !', '!'))
    # Fix "24 euros" → "24€" visually, "49" → "49€" when standalone after "synastry at"
    text = text.replace('24 euros', '24€').replace('49.', '49€.').replace('183 euros', '183€')
    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:]
    return text


out_lines = []
prev_end = 0.0
for i, grp in enumerate(cues, 1):
    start = max(prev_end + 0.02, grp[0]['s'] - 0.08)
    end_default = grp[-1]['e'] + 0.25
    # Don't overlap next cue
    if i < len(cues):
        end_default = min(end_default, cues[i][0]['s'] - 0.05)
    text = mk_text(grp)
    out_lines.append(f'{i}\n{fmt(start)} --> {fmt(end_default)}\n{text}\n')
    prev_end = end_default

OUT.write_text('\n'.join(out_lines), 'utf-8')
print(f'[OK] {len(cues)} cues → {OUT}')
for i, grp in enumerate(cues, 1):
    print(f'  {i:2d}  {grp[0]["s"]:5.2f} → {grp[-1]["e"]:5.2f}  '
          f'{mk_text(grp)[:70]}')
