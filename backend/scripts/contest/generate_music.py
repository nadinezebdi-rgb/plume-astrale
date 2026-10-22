"""Génère 70s de musique instrumentale via fal.ai elevenlabs/music."""
import os, sys, time
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

# Use Emergent universal key as FAL_KEY
os.environ['FAL_KEY'] = os.environ.get('EMERGENT_LLM_KEY', '')

import fal_client

PROMPT = (
    "Elegant, mysterious, slightly cosmic and astrological cinematic ambient instrumental "
    "for a premium brand film about personalized astrology books. Slow evolving atmosphere, "
    "warm felt piano, delicate glassy arpeggios, restrained analog synth pads, subtle "
    "celestial shimmer, deep soft bass, sparse orchestral strings, gradual lift suitable for "
    "a pitch deck voiceover, polished spacious mix, tasteful and emotionally optimistic. "
    "No vocals, no singing, no spoken words, no choir, no lyrics, no abrupt drums, no harsh "
    "risers, no copyrighted melody."
)

print('[fal.ai] Génération 70s musique instrumentale cosmique…')
print(f'[fal.ai] Model: fal-ai/elevenlabs/music')
print(f'[fal.ai] Duration: 70s · instrumental: True')
t0 = time.time()

result = fal_client.subscribe(
    'fal-ai/elevenlabs/music',
    arguments={
        'prompt': PROMPT,
        'music_length_ms': 70_000,
        'force_instrumental': True,
        'output_format': 'mp3_44100_128',
    },
    with_logs=False,
)

elapsed = time.time() - t0
print(f'[fal.ai] ✅ Généré en {elapsed:.1f}s')
audio_url = result['audio']['url']
print(f'[fal.ai] URL : {audio_url}')

# Download
import urllib.request
OUT_MP3 = '/app/video_pitch_assets/deck_bgm.mp3'
urllib.request.urlretrieve(audio_url, OUT_MP3)
print(f'[fal.ai] ✅ Téléchargé : {OUT_MP3} ({os.path.getsize(OUT_MP3)/1024:.1f} KB)')
