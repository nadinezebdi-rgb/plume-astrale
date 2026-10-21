"""Transcribe voice-over → precise SRT with word-level sync."""

import asyncio
import json
import os
from pathlib import Path

from emergentintegrations.llm.openai import OpenAISpeechToText

AUDIO = Path('/app/video_pitch_assets/voiceover_en.mp3')
SRT_OUT = Path('/app/video_pitch_assets/plume_astrale_pitch_EN.srt')
KEY = os.environ.get('EMERGENT_LLM_KEY') or 'sk-emergent-6F4035d69E16aAa968'


def fmt(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        s += 1
        ms = 0
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


async def main():
    stt = OpenAISpeechToText(api_key=KEY)
    with AUDIO.open('rb') as f:
        result = await stt.transcribe(
            file=f, model='whisper-1',
            response_format='verbose_json',
            timestamp_granularities=['word'], language='en',
        )
    if isinstance(result, str):
        result = json.loads(result)

    words = result.get('words', [])
    full_text = result.get('text', '')
    print(f'[stt] {len(words)} words · {len(full_text)} chars')

    # Build SRT by sentence (not fixed-size groups). Walk the text in order,
    # for each sentence we need start = first-word start, end = last-word end.
    # We assume whisper's word list is in order; join words with spaces.

    # Clean word tokens
    toks = [{'t': w['word'].strip(), 's': w['start'], 'e': w['end']} for w in words]

    SENT_END = {'.', '?', '!'}
    chunks: list[list[dict]] = []
    cur: list[dict] = []
    for w in toks:
        cur.append(w)
        last_char = w['t'][-1:] if w['t'] else ''
        # Break on sentence end OR after 8 words (soft cap, avoid long cues)
        if last_char in SENT_END or len(cur) >= 8:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)

    lines = []
    for i, grp in enumerate(chunks, start=1):
        start = max(0.0, grp[0]['s'])
        end = min(grp[-1]['e'] + 0.15, 54.5)
        # Join words with a single space
        text = ' '.join(w['t'] for w in grp)
        # Keep clean punctuation spacing
        text = (text.replace(' ,', ',').replace(' .', '.')
                     .replace(' ?', '?').replace(' !', '!')
                     .replace(' ;', ';').replace(' :', ':'))
        lines.append(f'{i}\n{fmt(start)} --> {fmt(end)}\n{text}\n')

    SRT_OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'[OK] {len(chunks)} cues → {SRT_OUT}')
    # Also write a time map so we can resync image durations
    time_map = Path('/app/video_pitch_assets/_word_times.json')
    time_map.write_text(json.dumps({
        'words': toks,
        'duration': toks[-1]['e'] if toks else 0,
    }, indent=2))
    print(f'[OK] word timings → {time_map}')


asyncio.run(main())
