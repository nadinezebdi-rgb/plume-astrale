"""Voice-over French for the TikTok pedagogical video.

Message: 'Ton commentaire suffit pas — crée ton compte sur plume-astrale.fr'.
Voice: Nova (chaleureuse, mature).
"""
import sys, time
sys.path.insert(0, '/app/backend')
from pathlib import Path
from services.tts_service import synthesize

OUT_DIR = Path('/app/backend/cache/tts_v2')
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHAPTERS = [
    # (name, text, target_duration_seconds_for_visual_planning)
    ('01_hook',        "Tu commentes ton signe en dessous des vidéos... mais ça s'arrête là."),
    ('02_landing',     "Sur plume astrale point fr, on va beaucoup plus loin."),
    ('03_signup',      "Crée ton compte gratuit. Tu reçois vingt crédits offerts."),
    ('04_accueil',     "Une fois inscrite, tu débloques ton espace personnel."),
    ('05_solena',      "Tu peux discuter avec Soléna — pas un chatbot. Une lecture réelle, sur ton thème natal."),
    ('06_horoscope',   "Ton horoscope du jour, calculé sur ton ciel. Pas sur ton signe solaire."),
    ('07_analyses',    "Ta numérologie. Tes tirages. Tes analyses karmiques. Tout ce qui te fait avancer."),
    ('08_emotion',     "Quand une lecture cite ton prénom, ta date, ton chemin — quelque chose bouge."),
    ('09_cta',         "plume astrale point fr. Crée ton compte. Ça commence là — pas dans les commentaires."),
]

if __name__ == '__main__':
    total_chars = 0
    t0 = time.time()
    for name, text in CHAPTERS:
        out = OUT_DIR / f"{name}.mp3"
        try:
            synthesize(text, voice='nova', model='tts-1-hd', output_path=out, speed=0.94)
            total_chars += len(text)
            print(f"  ✓ {name}: {len(text)}c → {out.stat().st_size // 1024} KB")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
    print(f"\nTotal: {total_chars} chars in {time.time()-t0:.1f}s")
