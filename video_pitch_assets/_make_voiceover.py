"""Regenerate the voice-over v2 : slower + astrology-api credit."""

import asyncio
import os
from pathlib import Path

from emergentintegrations.llm.openai import OpenAITextToSpeech

OUT = Path('/app/video_pitch_assets/voiceover_en.mp3')
KEY = os.environ.get('EMERGENT_LLM_KEY') or 'sk-emergent-6F4035d69E16aAa968'

SCRIPT = (
    "What if astrology wasn't about predicting your future, "
    "but about understanding yourself better, today? "
    "Meet Plume Astrale — literary astrology, tarot and numerology. "
    "Four reading paths, tailored to real-life questions: "
    "know yourself, understand your relationships, "
    "explore a question, reflect on your cycle. "
    "Each reading becomes a personal book — "
    "a forty-nine page edition of your birth chart. "
    "Precise charts, powered by Astrology-API. "
    "Poetic chapters, composed by GPT. "
    "A printed-book quality PDF, delivered by email. "
    "Natal theme at twenty-four euros. "
    "Synastry at forty-nine. "
    "And on the last page, something unique: "
    "a signature designed to be gifted. "
    "Your Ex Libris — a cut-out astral card "
    "to print, to keep, or to offer. "
    "One hundred and eighty-three euros in Facebook Ads. "
    "One hundred and four payments. "
    "Thirteen times return on ad spend. "
    "Stripe live. Real users. Validated by the market. "
    "Plume Astrale — understand yourself, today."
)

async def main():
    tts = OpenAITextToSpeech(api_key=KEY)
    audio = await tts.generate_speech(
        text=SCRIPT, model='tts-1-hd', voice='nova',
        speed=0.88, response_format='mp3',
    )
    OUT.write_bytes(audio)
    print(f'OK · {len(audio)} bytes → {OUT}')

asyncio.run(main())
