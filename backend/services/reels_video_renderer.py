"""reels_video_renderer — Génère un MP4 15s de la révélation d'un tirage de tarot.

Produit une vidéo courte (TikTok/Reels/Shorts) qui met en scène le tirage
partagé : titre → révélation séquentielle des cartes → conseil → CTA
« Plume Astrale ». Deux formats :
  - 'vertical' : 1080×1920 (TikTok/Reels/Shorts)
  - 'square'   : 1080×1080 (Instagram feed)

Pipeline :
  1. Build un HTML autonome (styles + animations CSS keyframes, 15 s).
  2. Playwright headless Chromium charge le HTML, le viewport est fixé à
     la taille cible et `record_video_dir` enregistre un WebM.
  3. FFmpeg transcode WebM → MP4 h264 à 30 fps, aux dimensions exactes.
  4. Retourne les bytes MP4.

Zero appel réseau : les fonts sont embarquées en base64 dans la CSS.
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import subprocess
import tempfile
import uuid
from html import escape
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
FONTS_DIR = ROOT / 'assets' / 'book' / 'fonts'

# Résolution Playwright pour chaque format. On enregistre à la taille cible
# finale pour éviter un rescale coûteux côté ffmpeg.
_FORMATS = {
    'vertical': {'w': 1080, 'h': 1920},
    'square':   {'w': 1080, 'h': 1080},
}

_DURATION_S = 15
_FPS = 30

# Chromium headless shell préinstallé (cf. ssr_snapshot.py)
_CHROMIUM_PATH_DEFAULT = '/pw-browsers/chromium_headless_shell-1208/chrome-linux/headless_shell'

TYPE_LABELS = {
    'marseille': 'Tirage Marseille',
    'celtique':  'Croix Celtique',
    'complet':   'Tirage Complet · 78 arcanes',
}

DOMAINE_LABELS = {
    'amour':     'Amour & Relations',
    'travail':   'Carrière & Travail',
    'argent':    'Finances & Abondance',
    'sante':     'Santé & Bien-être',
    'spirituel': 'Spiritualité',
    'general':   'Question Générale',
}


LOGO_SVG_PATH = ROOT / 'assets' / 'book' / 'assets' / 'logo-plume.svg'


# ─── Fonts (embedded base64) ────────────────────────────────────────────

def _font_b64(name: str) -> str:
    """Retourne la font `name` encodée base64 (data URL body), ou '' si absente."""
    path = FONTS_DIR / name
    if not path.is_file():
        return ''
    try:
        return base64.b64encode(path.read_bytes()).decode('ascii')
    except Exception as e:  # pragma: no cover
        logger.warning(f'[reels] font load failed {name}: {e}')
        return ''


def _logo_svg() -> str:
    """Retourne le SVG de la plume (contenu inliné), ou '' si absent."""
    if not LOGO_SVG_PATH.is_file():
        return ''
    try:
        return LOGO_SVG_PATH.read_text(encoding='utf-8')
    except Exception as e:  # pragma: no cover
        logger.warning(f'[reels] logo load failed: {e}')
        return ''


def _qr_png_b64(url: str) -> str:
    """Génère un QR code PNG en base64 (fond parchemin, motifs navy)."""
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_M
    except Exception as e:  # pragma: no cover
        logger.warning(f'[reels] qrcode lib unavailable: {e}')
        return ''
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='#0F1A3C', back_color='#F8F1E3')
        buf = io_module_bytesio()
        img.save(buf, format='PNG')
        return base64.b64encode(buf.getvalue()).decode('ascii')
    except Exception as e:  # pragma: no cover
        logger.warning(f'[reels] qr render failed: {e}')
        return ''


def io_module_bytesio():
    """Lazy BytesIO (évite un import en haut pour un seul usage)."""
    import io as _io
    return _io.BytesIO()


# ─── HTML template ─────────────────────────────────────────────────────

def _card_block_html(card: dict[str, Any], idx: int, total: int, start_s: float,
                     dur_s: float) -> str:
    """Rend un bloc carte avec son propre delay d'animation.

    Chaque carte apparaît avec un flip 3D + fade pendant `dur_s` secondes,
    starting at `start_s`.
    """
    nom = escape(str(card.get('nom') or f'Carte {idx + 1}'))
    position = escape(str(card.get('position') or ''))
    orientation = (card.get('orientation') or '').lower()
    is_rev = orientation == 'renverse'
    is_major = card.get('is_major') is not False  # majeur par défaut
    symbole = escape(str(card.get('symbole') or '✦'))
    rang = escape(str(card.get('rang') or ''))
    suite = escape(str(card.get('suite') or ''))
    couleur = str(card.get('couleur') or '#C9A24B')
    sens_label = 'Renversée' if is_rev else 'Droite'
    sens_glyph = '☽' if is_rev else '☉'

    # Face visuelle : arcane majeur → fond navy + symbole or ;
    # arcane mineur → fond coloré + rang/suite.
    if is_major:
        face = f'''
          <div class="card-art card-art-major">
            <div class="card-art-symbol">{symbole}</div>
          </div>
        '''
    else:
        face = f'''
          <div class="card-art card-art-minor" style="background: linear-gradient(135deg, {couleur}33, {couleur}0a);">
            <div class="card-art-minor-inner">
              <div class="card-art-minor-glyph" style="color: {couleur};">{symbole}</div>
              <div class="card-art-minor-rank">{rang}</div>
              <div class="card-art-minor-suite">de {suite}</div>
            </div>
          </div>
        '''

    rev_class = 'card-rev' if is_rev else ''
    end_s = start_s + dur_s
    return f'''
      <div class="card {rev_class}"
           style="--card-start:{start_s:.3f}s; --card-dur:{dur_s:.3f}s; --card-end:{end_s:.3f}s;">
        <div class="card-pos">{position}</div>
        <div class="card-frame">
          {face}
        </div>
        <div class="card-name">{nom}</div>
        <div class="card-sens">{sens_glyph} {sens_label}</div>
      </div>
    '''


def _build_html(doc: dict[str, Any], fmt: str, share_url: str = '') -> str:
    """Construit le HTML autonome prêt à être enregistré par Playwright.

    `share_url` est optionnel : si fourni, on affiche un QR code en bas à
    droite qui pointe vers l'URL OG du tirage, pour que les Reels partagés
    hors-contexte restent attribuables à la marque.
    """
    dims = _FORMATS.get(fmt, _FORMATS['vertical'])
    W, H = dims['w'], dims['h']
    vertical = (fmt == 'vertical')

    first_name = escape(str(doc.get('first_name') or 'Plume'))
    type_label = TYPE_LABELS.get(doc.get('type', ''), 'Tirage de tarot')
    domaine_label = DOMAINE_LABELS.get(doc.get('domaine', ''), 'Question Générale')
    question = str(doc.get('question') or '').strip()
    data = doc.get('data') or {}
    cartes = data.get('cartes') or []
    synth = data.get('synthese') or {}
    conseil = str(data.get('conseil_final') or '').strip()
    tendance = str(synth.get('tendance_generale') or '').strip()
    fil = str(synth.get('fil_conducteur') or '').strip()

    # Timing (sec) — total 15 s
    T_INTRO_IN  = 0.0  # titre apparaît
    T_INTRO_HOLD = 2.4  # titre pleinement visible → fade out
    T_CARDS_START = 2.8
    T_CARDS_END = 11.0
    T_CONSEIL_IN = 11.0
    T_CONSEIL_HOLD = 13.3
    T_CTA_IN = 13.3
    T_END = 15.0

    # Distribution du temps par carte
    n = max(1, len(cartes))
    cards_total = max(0.5, T_CARDS_END - T_CARDS_START)
    per_card_slot = cards_total / n
    per_card_dur = min(1.6, per_card_slot + 0.6)  # chevauchement léger

    cards_html = []
    for i, c in enumerate(cartes):
        start = T_CARDS_START + i * per_card_slot
        cards_html.append(_card_block_html(c, i, n, start, per_card_dur))
    cards_block = '\n'.join(cards_html)

    # Grille responsive selon nombre de cartes
    if n <= 3:
        grid_cols = 'repeat(3, 1fr)'
    elif n <= 5:
        grid_cols = 'repeat(5, 1fr)' if not vertical else 'repeat(3, 1fr)'
    elif n <= 7:
        grid_cols = 'repeat(4, 1fr)' if not vertical else 'repeat(3, 1fr)'
    else:
        grid_cols = 'repeat(5, 1fr)' if not vertical else 'repeat(4, 1fr)'

    # Fonts (embedded)
    font_regular = _font_b64('CormorantGaramond-Regular.ttf')
    font_bold = _font_b64('CormorantGaramond-Bold.ttf')
    font_italic = _font_b64('CormorantGaramond-Italic.ttf')

    font_face = ''
    if font_regular:
        font_face += (
            "@font-face{font-family:'Cormorant';font-weight:400;font-style:normal;"
            f"src:url(data:font/ttf;base64,{font_regular}) format('truetype');}}\n"
        )
    if font_bold:
        font_face += (
            "@font-face{font-family:'Cormorant';font-weight:700;font-style:normal;"
            f"src:url(data:font/ttf;base64,{font_bold}) format('truetype');}}\n"
        )
    if font_italic:
        font_face += (
            "@font-face{font-family:'Cormorant';font-weight:400;font-style:italic;"
            f"src:url(data:font/ttf;base64,{font_italic}) format('truetype');}}\n"
        )

    # On tronque un peu le conseil pour tenir à l'écran
    conseil_short = conseil
    if len(conseil_short) > 240:
        conseil_short = conseil_short[:237].rsplit(' ', 1)[0] + '…'
    tendance_or_fil = tendance or (fil[:160] + '…' if len(fil) > 160 else fil)

    # Scaling en fonction du format
    title_fs = 92 if vertical else 72
    sub_fs = 36 if vertical else 30
    card_w = 220 if vertical else 160
    card_h = 320 if vertical else 240
    conseil_fs = 46 if vertical else 36
    cta_fs = 72 if vertical else 56

    question_html = ''
    if question:
        q_escaped = escape(question)
        question_html = f'<p class="intro-question">« {q_escaped} »</p>'

    conseil_html = ''
    if conseil_short:
        conseil_html = f'''
          <div class="conseil-wrap">
            <div class="conseil-glyph">✦</div>
            <div class="conseil-label">Conseil des Arcanes</div>
            <div class="conseil-text">{escape(conseil_short)}</div>
          </div>
        '''
    elif tendance_or_fil:
        conseil_html = f'''
          <div class="conseil-wrap">
            <div class="conseil-glyph">✦</div>
            <div class="conseil-label">Fil conducteur</div>
            <div class="conseil-text">{escape(tendance_or_fil)}</div>
          </div>
        '''

    # Watermark : logo plume (bottom-left) + QR code (bottom-right).
    # Les deux restent persistants pendant 15s, à faible opacité au départ
    # puis pleine opacité pendant la phase CTA.
    logo_svg = _logo_svg()
    watermark_logo_html = ''
    if logo_svg:
        watermark_logo_html = f'''
    <div class="watermark watermark-logo">
      {logo_svg}
      <div class="watermark-logo-text">Plume<br/><em>Astrale</em></div>
    </div>
    '''

    watermark_qr_html = ''
    if share_url:
        qr_b64 = _qr_png_b64(share_url)
        if qr_b64:
            watermark_qr_html = f'''
    <div class="watermark watermark-qr">
      <img src="data:image/png;base64,{qr_b64}" alt="QR code" />
      <div class="watermark-qr-caption">Scannez</div>
    </div>
    '''

    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<style>
{font_face}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: {W}px; height: {H}px;
  background: #0b142e;
  color: #F8F1E3;
  font-family: 'Cormorant', 'Georgia', serif;
  overflow: hidden;
}}
body {{
  background:
    radial-gradient(ellipse at 50% 20%, rgba(201,162,75,0.18), transparent 55%),
    radial-gradient(ellipse at 50% 85%, rgba(184,169,232,0.10), transparent 60%),
    linear-gradient(180deg, #0F1A3C 0%, #0b142e 55%, #060a1c 100%);
}}

.stage {{
  width: {W}px; height: {H}px;
  position: relative;
}}

/* ─── étoiles subtiles ─── */
.stars::before, .stars::after {{
  content: ''; position: absolute; inset: 0;
  background-image:
    radial-gradient(1.5px 1.5px at 10% 15%, rgba(248,241,227,0.6), transparent),
    radial-gradient(1px 1px at 30% 35%, rgba(248,241,227,0.5), transparent),
    radial-gradient(1.2px 1.2px at 55% 10%, rgba(248,241,227,0.5), transparent),
    radial-gradient(1px 1px at 70% 45%, rgba(248,241,227,0.4), transparent),
    radial-gradient(1.5px 1.5px at 85% 20%, rgba(248,241,227,0.5), transparent),
    radial-gradient(1px 1px at 20% 70%, rgba(248,241,227,0.4), transparent),
    radial-gradient(1px 1px at 50% 80%, rgba(248,241,227,0.4), transparent),
    radial-gradient(1.2px 1.2px at 80% 90%, rgba(248,241,227,0.5), transparent);
  animation: twinkle 4s ease-in-out infinite;
}}
.stars::after {{ animation-delay: 2s; opacity: .6; }}
@keyframes twinkle {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.3; }}
}}

/* ─── INTRO ─── */
.intro {{
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; padding: 0 60px;
  opacity: 0;
  animation: introShow {_DURATION_S}s linear forwards;
}}
@keyframes introShow {{
  0% {{ opacity: 0; transform: translateY(30px); }}
  5% {{ opacity: 1; transform: translateY(0); }}
  15% {{ opacity: 1; }}
  19% {{ opacity: 0; transform: translateY(-20px); }}
  100% {{ opacity: 0; }}
}}
.intro-eyebrow {{
  color: #C9A24B;
  letter-spacing: 0.35em;
  text-transform: uppercase;
  font-size: {sub_fs - 6}px;
  font-weight: 700;
  margin-bottom: 24px;
}}
.intro-title {{
  font-size: {title_fs}px;
  font-weight: 400;
  line-height: 1.08;
  color: #F8F1E3;
  margin-bottom: 24px;
  text-shadow: 0 2px 24px rgba(201,162,75,0.3);
}}
.intro-title em {{
  font-style: italic;
  color: #C9A24B;
}}
.intro-sub {{
  font-size: {sub_fs}px;
  color: rgba(248,241,227,0.75);
  font-style: italic;
  margin-bottom: 32px;
}}
.intro-question {{
  font-size: {sub_fs}px;
  color: rgba(248,241,227,0.90);
  font-style: italic;
  max-width: 820px;
  line-height: 1.4;
}}

/* ─── CARDS ─── */
.cards-wrap {{
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 60px 40px;
  opacity: 0;
  animation: cardsPhase {_DURATION_S}s linear forwards;
}}
@keyframes cardsPhase {{
  0%, 18% {{ opacity: 0; }}
  20% {{ opacity: 1; }}
  73% {{ opacity: 1; }}
  76% {{ opacity: 0; }}
  100% {{ opacity: 0; }}
}}
.cards-eyebrow {{
  color: #C9A24B;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  font-size: {sub_fs - 8}px;
  font-weight: 700;
  margin-bottom: 28px;
}}
.cards-title {{
  font-size: {title_fs - 24}px;
  color: #F8F1E3;
  margin-bottom: 36px;
}}
.cards-title em {{ color: #C9A24B; font-style: italic; }}
.cards-grid {{
  display: grid;
  grid-template-columns: {grid_cols};
  gap: 22px;
  max-width: {W - 80}px;
  margin: 0 auto;
}}

.card {{
  display: flex; flex-direction: column; align-items: center;
  opacity: 0;
  transform: translateY(26px) rotateY(90deg);
  animation: cardReveal 15s linear forwards;
}}
@keyframes cardReveal {{
  0% {{ opacity: 0; transform: translateY(26px) rotateY(90deg); }}
  100% {{ opacity: 0; transform: translateY(26px) rotateY(90deg); }}
}}
.card {{
  animation-delay: 0s;
  animation-name: cardShow;
}}
@keyframes cardShow {{
  0% {{ opacity: 0; transform: translateY(26px) rotateY(90deg) scale(0.9); }}
  100% {{ opacity: 0; transform: translateY(26px) rotateY(90deg) scale(0.9); }}
}}
/* On applique les keyframes réels via style inline + propriétés custom */
.card {{
  animation: none;
  position: relative;
}}
.card::before {{
  content: '';
  position: absolute; inset: 0;
  pointer-events: none;
}}
/* Astuce : on utilise une classe keyframes générique qui lit --card-start */
.card {{
  --card-start: 0s;
  --card-dur: 1.2s;
  --card-end: 1.2s;
  animation:
    cardFadeIn var(--card-dur) ease-out var(--card-start) forwards,
    cardSettle 0.8s ease-out calc(var(--card-end) + 0s) forwards;
  opacity: 0;
  transform: translateY(30px) rotateY(90deg) scale(0.85);
}}
@keyframes cardFadeIn {{
  from {{ opacity: 0; transform: translateY(30px) rotateY(90deg) scale(0.85); }}
  to   {{ opacity: 1; transform: translateY(0)    rotateY(0)   scale(1); }}
}}
@keyframes cardSettle {{
  from {{ transform: translateY(0) rotateY(0) scale(1); filter: brightness(1.15); }}
  to   {{ transform: translateY(0) rotateY(0) scale(1); filter: brightness(1); }}
}}

.card-pos {{
  font-size: {sub_fs - 12}px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #C9A24B;
  margin-bottom: 10px;
  text-align: center;
  font-weight: 700;
}}
.card-frame {{
  width: {card_w}px; height: {card_h}px;
  border-radius: 14px;
  overflow: hidden;
  border: 2px solid rgba(201,162,75,0.55);
  box-shadow:
    0 0 30px rgba(201,162,75,0.25),
    inset 0 0 20px rgba(0,0,0,0.3);
  background: #0e0a24;
  display: flex; align-items: center; justify-content: center;
}}
.card.card-rev .card-frame {{
  transform: rotate(180deg);
  border-color: rgba(184,169,232,0.65);
  box-shadow:
    0 0 30px rgba(184,169,232,0.25),
    inset 0 0 20px rgba(0,0,0,0.3);
}}
.card-art {{
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
}}
.card-art-major {{
  background: radial-gradient(circle at 50% 35%, #1a2a5a 0%, #0e0a24 70%);
}}
.card-art-symbol {{
  font-size: {int(card_w * 0.6)}px;
  color: #C9A24B;
  text-shadow: 0 0 20px rgba(201,162,75,0.6);
}}
.card-art-minor-inner {{
  text-align: center;
}}
.card-art-minor-glyph {{
  font-size: {int(card_w * 0.5)}px;
  margin-bottom: 6px;
}}
.card-art-minor-rank {{
  color: #F8F1E3;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  font-size: {sub_fs - 10}px;
}}
.card-art-minor-suite {{
  color: rgba(248,241,227,0.7);
  font-size: {sub_fs - 14}px;
  font-style: italic;
}}
.card-name {{
  margin-top: 12px;
  font-size: {sub_fs - 6}px;
  color: #F8F1E3;
  text-align: center;
  font-weight: 600;
  line-height: 1.15;
  max-width: {card_w + 20}px;
}}
.card-sens {{
  margin-top: 4px;
  font-size: {sub_fs - 14}px;
  color: rgba(248,241,227,0.6);
}}

/* ─── CONSEIL ─── */
.conseil-wrap {{
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; padding: 0 80px;
  opacity: 0;
  animation: conseilShow {_DURATION_S}s linear forwards;
}}
@keyframes conseilShow {{
  0%, 72% {{ opacity: 0; transform: scale(0.95); }}
  76%     {{ opacity: 1; transform: scale(1); }}
  87%     {{ opacity: 1; transform: scale(1); }}
  90%     {{ opacity: 0; transform: scale(1.02); }}
  100%    {{ opacity: 0; }}
}}
.conseil-glyph {{
  font-size: {int(cta_fs * 1.3)}px;
  color: #C9A24B;
  margin-bottom: 20px;
  text-shadow: 0 0 30px rgba(201,162,75,0.6);
}}
.conseil-label {{
  color: #C9A24B;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  font-size: {sub_fs - 6}px;
  font-weight: 700;
  margin-bottom: 24px;
}}
.conseil-text {{
  font-size: {conseil_fs}px;
  line-height: 1.4;
  color: #F8F1E3;
  font-style: italic;
  max-width: 920px;
}}

/* ─── CTA ─── */
.cta-wrap {{
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; padding: 0 80px;
  opacity: 0;
  animation: ctaShow {_DURATION_S}s linear forwards;
}}
@keyframes ctaShow {{
  0%, 88% {{ opacity: 0; transform: translateY(20px); }}
  91%     {{ opacity: 1; transform: translateY(0); }}
  100%    {{ opacity: 1; transform: translateY(0); }}
}}
.cta-glyph {{
  font-size: {int(cta_fs * 1.4)}px;
  color: #C9A24B;
  margin-bottom: 30px;
  animation: ctaPulse 1.8s ease-in-out infinite;
  animation-delay: 13s;
}}
@keyframes ctaPulse {{
  0%, 100% {{ transform: scale(1); text-shadow: 0 0 20px rgba(201,162,75,0.5); }}
  50%      {{ transform: scale(1.15); text-shadow: 0 0 40px rgba(201,162,75,0.9); }}
}}
.cta-title {{
  font-size: {cta_fs}px;
  line-height: 1.15;
  margin-bottom: 20px;
  color: #F8F1E3;
}}
.cta-title em {{ color: #C9A24B; font-style: italic; }}
.cta-url {{
  color: #C9A24B;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  font-size: {sub_fs - 2}px;
  font-weight: 700;
  margin-top: 12px;
}}

/* ─── WATERMARK persistant : logo plume (BL) + QR code (BR) ─── */
.watermark {{
  position: absolute;
  bottom: {int(H * 0.025)}px;
  display: flex;
  align-items: center;
  z-index: 10;
  opacity: 0.55;
  animation: wmSettle {_DURATION_S}s linear forwards;
}}
@keyframes wmSettle {{
  0%, 72% {{ opacity: 0.55; }}
  88%     {{ opacity: 1; }}
  100%    {{ opacity: 1; }}
}}
.watermark-logo {{
  left: {int(W * 0.04)}px;
  gap: 10px;
}}
.watermark-logo svg {{
  width: {int(W * 0.055)}px;
  height: auto;
  display: block;
  filter: drop-shadow(0 0 8px rgba(201,162,75,0.35));
}}
.watermark-logo-text {{
  color: #F8F1E3;
  font-family: 'Cormorant', serif;
  font-size: {int(sub_fs * 0.75)}px;
  letter-spacing: 0.08em;
  line-height: 1.1;
}}
.watermark-logo-text em {{
  color: #C9A24B;
  font-style: italic;
  font-weight: 600;
}}
.watermark-qr {{
  right: {int(W * 0.04)}px;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}}
.watermark-qr img {{
  width: {int(W * 0.11)}px;
  height: {int(W * 0.11)}px;
  display: block;
  border-radius: 10px;
  padding: 6px;
  background: rgba(248,241,227,0.95);
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}}
.watermark-qr-caption {{
  color: #C9A24B;
  font-family: 'Cormorant', serif;
  font-size: {int(sub_fs * 0.55)}px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-weight: 700;
}}
</style>
</head>
<body>
  <div class="stage">
    <div class="stars"></div>

    <!-- INTRO (0–2.5s) -->
    <div class="intro">
      <div class="intro-eyebrow">✦ {escape(type_label)} · {escape(domaine_label)} ✦</div>
      <h1 class="intro-title">Le tirage de<br/><em>{first_name}</em></h1>
      {question_html if question_html else f'<p class="intro-sub">Les arcanes vont parler…</p>'}
    </div>

    <!-- CARDS (2.5–11s) -->
    <div class="cards-wrap">
      <div class="cards-eyebrow">Les arcanes révélés</div>
      <div class="cards-grid">
        {cards_block}
      </div>
    </div>

    <!-- CONSEIL (11–13.3s) -->
    {conseil_html}

    <!-- CTA (13.3–15s) -->
    <div class="cta-wrap">
      <div class="cta-glyph">✦</div>
      <h2 class="cta-title">Et vous, <em>que diraient<br/>vos arcanes&nbsp;?</em></h2>
      <div class="cta-url">plume-astrale.fr</div>
    </div>

    <!-- WATERMARK (persistant tout au long de la vidéo) -->
    {watermark_logo_html}
    {watermark_qr_html}
  </div>
</body>
</html>
'''
    return html


# ─── Playwright + FFmpeg pipeline ──────────────────────────────────────

async def _record_webm(html: str, width: int, height: int, out_dir: Path) -> Path:
    """Lance Playwright, enregistre un WebM 15s au viewport donné, retourne son path."""
    # Playwright utilise son propre ffmpeg (bundle) pour record_video_dir —
    # il faut lui indiquer le path des browsers préinstallés. En prod le var
    # PLAYWRIGHT_BROWSERS_PATH n'est pas défini au niveau du supervisor, donc
    # on le fixe ici si manquant.
    os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH', '/pw-browsers')

    from playwright.async_api import async_playwright

    chromium_path = os.environ.get('PLUME_CHROMIUM_PATH', _CHROMIUM_PATH_DEFAULT)
    if not Path(chromium_path).is_file():
        chromium_path = '/usr/bin/chromium'

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=chromium_path,
            args=[
                '--no-sandbox', '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--hide-scrollbars',
                '--mute-audio',
            ],
        )
        try:
            context = await browser.new_context(
                viewport={'width': width, 'height': height},
                device_scale_factor=1,
                record_video_dir=str(out_dir),
                record_video_size={'width': width, 'height': height},
            )
            page = await context.new_page()
            # On charge le HTML directement en data URL — zero round-trip
            await page.set_content(html, wait_until='domcontentloaded', timeout=20000)
            # Attend la fin des animations CSS (15 s + petite marge).
            await page.wait_for_timeout(int(_DURATION_S * 1000 + 400))
            video = page.video
            await page.close()
            await context.close()  # flush video
            webm_path = Path(await video.path()) if video else None
            if not webm_path or not webm_path.is_file():
                # Playwright 1.x : path() peut renvoyer qqchose uniquement
                # après context.close() ; on scanne au cas où.
                webm_files = sorted(out_dir.glob('*.webm'))
                if not webm_files:
                    raise RuntimeError('Playwright n\'a produit aucun fichier vidéo.')
                webm_path = webm_files[-1]
            return webm_path
        finally:
            await browser.close()


def _transcode_mp4(webm_path: Path, mp4_path: Path, width: int, height: int) -> None:
    """Transcode WebM → MP4 h264 en forçant dimensions + 30 fps."""
    ffmpeg_bin = os.environ.get('PLUME_FFMPEG_BIN', '/usr/bin/ffmpeg')
    cmd = [
        ffmpeg_bin, '-y',
        '-i', str(webm_path),
        '-t', str(_DURATION_S),
        '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black',
        '-r', str(_FPS),
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-an',
        str(mp4_path),
    ]
    logger.info(f'[reels] ffmpeg transcode → {mp4_path.name}')
    proc = subprocess.run(cmd, capture_output=True, timeout=90)
    if proc.returncode != 0:
        err = proc.stderr.decode('utf-8', 'replace')[-800:]
        raise RuntimeError(f'ffmpeg failed ({proc.returncode}): {err}')


async def render_reels_video(doc: dict[str, Any], fmt: str = 'vertical',
                             share_url: str = '') -> bytes:
    """Génère un MP4 15 s de la révélation du tirage.

    Cache Emergent Object Storage : clé `tirage-reels/{share_id}-{fmt}.mp4`.
    Les tirages partagés sont immuables → cache sans TTL côté app, le remote
    gère sa propre GC. Si le cache répond, on retourne les bytes sans lancer
    Playwright/ffmpeg (économise ~25 s).

    Args:
        doc: document `shared_tirages` (dict) tel que lu dans MongoDB.
        fmt: 'vertical' (1080×1920, défaut) ou 'square' (1080×1080).
        share_url: URL complète à encoder dans le QR (bottom-right). Omis
                   → pas de QR affiché.

    Returns:
        Bytes MP4 h264 15 s @ 30 fps, prêts à être renvoyés comme StreamingResponse.
    """
    fmt = (fmt or 'vertical').lower()
    if fmt not in _FORMATS:
        fmt = 'vertical'
    dims = _FORMATS[fmt]
    W, H = dims['w'], dims['h']

    share_id = str(doc.get('share_id') or '').strip().lower()

    # ─── Cache remote (Emergent Object Storage) ───────────────────────
    cache_path = f'tirage-reels/{share_id}-{fmt}.mp4' if share_id else ''
    if cache_path:
        try:
            from services.emergent_storage import get_object as _get_obj
            cached = await _get_obj(cache_path)
            if cached and len(cached) > 10_000:  # garde-fou contre blobs vides
                logger.info(f'[reels] cache hit {cache_path} ({len(cached)} B)')
                return cached
        except Exception as e:  # pragma: no cover
            logger.warning(f'[reels] cache read skipped: {e}')

    html = _build_html(doc, fmt, share_url=share_url)
    job_id = uuid.uuid4().hex[:10]

    with tempfile.TemporaryDirectory(prefix=f'plume-reels-{job_id}-') as tmp:
        tmpdir = Path(tmp)
        webm_dir = tmpdir / 'webm'
        webm_dir.mkdir()
        try:
            webm = await _record_webm(html, W, H, webm_dir)
        except Exception as e:
            logger.exception(f'[reels] Playwright capture failed: {e}')
            raise

        mp4 = tmpdir / f'tirage-{fmt}.mp4'
        try:
            _transcode_mp4(webm, mp4, W, H)
        except Exception as e:
            logger.exception(f'[reels] ffmpeg transcode failed: {e}')
            raise

        mp4_bytes = mp4.read_bytes()

    # ─── Push cache (fire-and-forget, pas bloquant pour le user) ──────
    if cache_path and mp4_bytes:
        try:
            from services.emergent_storage import put_object as _put_obj
            # On lance en arrière-plan pour que l'utilisateur reçoive la
            # réponse immédiatement et ne paie pas l'upload (~1-3 s).
            asyncio.create_task(_put_obj(cache_path, mp4_bytes, 'video/mp4'))
        except Exception as e:  # pragma: no cover
            logger.warning(f'[reels] cache write skipped: {e}')

    return mp4_bytes


__all__ = ['render_reels_video']
