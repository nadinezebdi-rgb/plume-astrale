"""Generate French voice-over for the 60s vertical demo via OpenAI TTS.

Uses the storyboard 9:16 script chapter by chapter. Each chapter → 1 mp3.
Voice: 'nova' (mature, warm, French-capable).
"""
import sys, time
sys.path.insert(0, '/app/backend')
from pathlib import Path
from services.tts_service import synthesize

OUT_DIR = Path('/app/backend/cache/tts_demo')
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHAPTERS = [
    ('01_hook', "Quatre-vingt-sept pour cent des horoscopes en ligne sont écrits par des bots."),
    ('02_arrivee', "Claire, quarante-trois ans, cherche une astrologue. Elle trouve une plume."),
    ('03_cinq_lectures', "Cinq lectures. Quatre-vingt-dix pages. Toi."),
    ('04_chat', "Elle écrit qu'elle a perdu sa mère. L'intelligence artificielle transfère à un humain. Soléna répond en trois minutes."),
    ('05_achat', "Quatre-vingt-dix-sept euros. Livraison instantanée. Elle valide."),
    ('06_livraison', "Ce paragraphe n'existait pas il y a six minutes. Il n'existera plus jamais pour personne d'autre."),
    ('07_cta', "Plume Astrale. Lien en bio. Trois clics, cinq minutes."),
]

if __name__ == '__main__':
    total_chars = 0
    t0 = time.time()
    for name, text in CHAPTERS:
        out = OUT_DIR / f"{name}.mp3"
        try:
            synthesize(text, voice='nova', model='tts-1-hd', output_path=out, speed=0.92)
            total_chars += len(text)
            print(f"  ✓ {name}: {len(text)}c → {out.stat().st_size // 1024} KB")
        except Exception as e:
            print(f"  ✗ {name}: FAIL {e}")
    dur = time.time() - t0
    est_cost = (total_chars / 1_000_000) * 30  # tts-1-hd $30/M
    print(f"\nTotal: {total_chars} chars, {dur:.1f}s, ~${est_cost:.3f}")
