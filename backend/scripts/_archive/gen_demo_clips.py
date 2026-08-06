"""Batch generation Sora for Plume Astrale demo — runs all clips in parallel threads."""
import sys, time
sys.path.insert(0, '/app/backend')
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from services.sora_service import generate_video_sync

OUT_DIR = Path('/app/backend/cache/sora_demo')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── The 6 clips ────────────────────────────────────────────────────
CLIPS = [
    {
        'name': 'sora1_claire_discovers',
        'model': 'sora-2',
        'seconds': 8,
        'prompt': """Cinematic 9:16 vertical shot. Claire, a 43-year-old French woman with shoulder-length ash-brown hair, wears a cream cashmere sweater, no makeup, gentle laugh lines around her eyes. She sits on a beige linen sofa in a warmly lit Parisian living room at 10pm. Soft golden lamp light from the left, teal blue tones in the window behind her.

Second 1-3: Medium shot from low angle. She opens a MacBook on her lap. The screen glow illuminates her face gradually.
Second 3-5: Extreme close-up on her right eye. Soft reflection of an ethereal astrology website with a woman's portrait appears in her iris.
Second 5-8: Medium shot, her face lit by the screen. She tilts her head slightly, a small smile forms — she's discovering something that speaks to her.

Style: 35mm cinema film grain, shallow depth of field f/1.8, natural window light mixed with warm lamp, Kodak Portra 400 grading. Slow quiet atmosphere. Naturalistic — not stylized.
Audio: absolute silence except distant Paris night ambience. No music, no dialogue.
Avoid: harsh shadows, phone screens, blue light, corporate settings, forced smiles."""
    },
    {
        'name': 'sora2_solena_portrait',
        'model': 'sora-2',
        'seconds': 8,
        'prompt': """Cinematic 9:16 vertical portrait. Soléna, a 52-year-old French astrologer. She has long silver-grey hair with a single loose braid falling over her left shoulder, wears a rust-colored wool shawl over a cream linen dress. Green-hazel eyes, a gentle knowing expression — not smiling, not stern.

Setting: a serene study filled with warm afternoon light. Behind her, a soft-focus bookshelf with old astrology books and a small collection of amber and teal crystals. A single candle burns softly on a wooden desk to the right.

Camera: slow Ken Burns zoom-in from medium shot to medium close-up over 8 seconds. Very slight lateral drift left to right. Depth of field extremely shallow f/1.4.

Style: painterly cinema photography, Roger Deakins lighting. Palette: cream, teal, gold, terracotta.
Audio: ambient silence, distant fabric rustle. No music.
Avoid: mysticism clichés like crystal balls or hands hovering over tarot, purple lighting, corny New Age aesthetic. She looks like a wise French professor, not a fortune teller."""
    },
    {
        'name': 'sora3_claire_chat',
        'model': 'sora-2',
        'seconds': 8,
        'prompt': """Cinematic 9:16 vertical shot. Claire, 43, ash-brown shoulder hair, cream cashmere sweater, sits cross-legged with a laptop on a knitted throw. Same Parisian living room, now 10:23pm, room dimmer, screen glow stronger on her face.

Second 1-4: Medium close-up over her shoulder. Her fingers type slowly. Text forms in a chat bubble on screen — we see fragments: 'Je viens de perdre...'. Her hand hesitates once, then continues.
Second 4-6: Slow push-in on her face. She has finished, is waiting. Lower lip slightly caught between her teeth.
Second 6-8: Her eyes glisten — not full tears, just screen reflection becoming liquid. She exhales once, silent. A single visible breath in the low warm light.

Style: 35mm cinema, natural ambient light only, no key light on her face — everything from the laptop screen. Kodak Portra 400. Shallow focus f/1.8, focus locked on her eyes.
Audio: absolute silence except her one soft exhale.
Avoid: dramatic tears, tissue box in frame, phone notifications, music sting. Must feel intimate, private, like eavesdropping on a real moment."""
    },
    {
        'name': 'sora4_email_arrives',
        'model': 'sora-2',
        'seconds': 8,
        'prompt': """Cinematic 9:16 vertical shot. Same Claire (43, ash-brown hair loosely pulled back, cream robe now, hair slightly messy), morning. She sits at a small rustic wooden kitchen table. Morning light streams through window on left — soft, golden, slightly diffused by sheer white curtains. A cup of black coffee steams in front of her.

Second 1-4: Overhead shot (top-down). Her two hands rest on either side of her phone on the table. The phone screen suddenly lights up with notification banners — 'Plume Astrale' with a small feather icon, stacked (5 notifications). Slight zoom in on the phone.
Second 4-8: Cut to medium shot at eye level across the table. She picks up the phone with her right hand, brings it slowly toward her face. Expression softens from anticipation to quiet joy. She whispers something inaudible, maybe 'déjà'.

Style: golden hour naturalistic lighting, 35mm cinema, Kodak Portra 800 for warmer skin tones. Wide aperture. Slight film grain.
Audio: kitchen ambience — distant church bell, faint coffee pot sound. No music.
Avoid: stock photo aesthetic, phone screen closeups that look like advertising, over-composed frames."""
    },
    {
        'name': 'sora5_reading_pro',
        'model': 'sora-2-pro',
        'seconds': 8,
        'prompt': """Cinematic 9:16 vertical shot. Claire, 43, ash-brown hair pulled back loosely, cream cashmere sweater, sits at her rustic wooden kitchen table by an open window. iPad in front of her displaying a PDF document. Morning sunlight streams sideways through window, catching dust particles.

Slow dolly-in over 8 seconds from medium shot to close-up of her face. She reads silently, lips moving very slightly with each word — she is silently pronouncing them.

At second 5, her expression shifts — she has just read something that touched her. Her right hand slowly rises to her mouth, fingers pressed against her lips. Her eyes stay on the screen. One tear escapes the corner of her right eye and rolls down without her wiping it away.

Style: golden natural window light, soft window bokeh in background, 35mm cinema, Kodak Portra 400. Shallow depth of field f/2.0. Very quiet, still composition. Slight film grain. Painterly, quiet.
Audio: absolute silence. Distant garden birds only. No music, no reading voice.
Avoid: dramatic weeping, tissues, music swelling, anyone else in frame, phone in shot. Single private moment of recognition — not sadness. The tear is one of being seen."""
    },
    {
        'name': 'sora6_community',
        'model': 'sora-2',
        'seconds': 8,
        'prompt': """Cinematic 9:16 vertical composition, illustration-meets-photography. An abstract constellation of soft warm dots forming the shape of a circle of women's faces around a central candle flame. Style: watercolor illustration merged with soft photographic depth — think Studio Ghibli night sky mixed with a Terrence Malick candlelight scene.

Camera: very slow zoom-out over 8 seconds from a single candle flame in the center, revealing progressively more soft dots of light which resolve into faint outlines of women's faces — dozens of them, arranged in a circle, looking inward with peaceful expressions. Features minimal, watercolor-brush-like, not photorealistic.

Palette: deep teal night sky, warm gold candle light, cream and ivory faces, occasional touches of dusty rose.
Audio: single continuous ambient tone, low female humming very faint (not words, not a melody, just breath-humming). Very soft, almost subliminal.
Style: hand-illustrated watercolor overlaid on subtle grain, similar to Plume Astrale pitch deck aesthetic. Organic, gentle, no harsh edges.
Avoid: photorealistic faces, celebrity look-alikes, religious iconography, digital-looking graphics."""
    },
]


def gen_one(clip):
    start = time.time()
    try:
        out = OUT_DIR / f"{clip['name']}.mp4"
        result = generate_video_sync(
            prompt=clip['prompt'],
            output_path=out,
            model=clip['model'],
            size='720x1280',
            seconds=clip['seconds'],
            poll_interval=10.0,
            max_wait_seconds=900.0,
        )
        return clip['name'], True, f"{time.time()-start:.1f}s · {result.stat().st_size // 1024} KB"
    except Exception as e:
        return clip['name'], False, f"{time.time()-start:.1f}s · FAIL: {e}"


if __name__ == '__main__':
    print(f"[batch] launching {len(CLIPS)} clips in parallel...")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(gen_one, c): c['name'] for c in CLIPS}
        for f in as_completed(futures):
            name, ok, info = f.result()
            mark = '✓' if ok else '✗'
            print(f"  [{mark}] {name}: {info}")
    print(f"[batch] total {time.time()-t0:.1f}s")
