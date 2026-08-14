"""Cercle Soléna — rapport mensuel PDF envoyé le 1er du mois à chaque abonné.

Le PDF contient l'humeur du mois complète, personnalisée par signe zodiacal.
Envoyé par email via Resend en pièce jointe.

Idempotent : garde en mémoire (fichier /tmp) le mois où on a déjà envoyé
pour ne pas double-envoyer sur un restart.
"""
from __future__ import annotations
import asyncio
import base64
import logging
import os
from datetime import datetime, timezone, timedelta
from io import BytesIO
from pathlib import Path
from typing import Optional

import httpx
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from services.monthly_mood_content import (
    get_sign_from_birthdate, get_monthly_mood, MONTH_NAMES_FR,
)
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

LAST_RUN_FILE = Path('/tmp/plume_cercle_monthly_last_run.txt')  # stocke 'YYYY-MM'
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')

# ═══════════════════════ Charte graphique ═══════════════════════
NIGHT_BLUE = (0.039, 0.067, 0.157)   # #0A1128
INK_BLUE = (0.059, 0.102, 0.235)     # #0F1A3C
GOLD = (0.722, 0.578, 0.353)         # #B8935A
GOLD_LIGHT = (0.788, 0.635, 0.294)   # #C9A24B
IVORY = (0.969, 0.961, 0.941)        # #F7F5F0
IVORY_DIM = (0.85, 0.84, 0.82)

# Try to register serif + sans fonts. Fallback to Helvetica.
_FONT_SERIF = 'Helvetica'
_FONT_SERIF_ITALIC = 'Helvetica-Oblique'
_FONT_SERIF_BOLD = 'Helvetica-Bold'
_FONT_SANS = 'Helvetica'
_FONT_SANS_BOLD = 'Helvetica-Bold'


def _register_fonts_once():
    global _FONT_SERIF, _FONT_SERIF_ITALIC, _FONT_SERIF_BOLD
    try:
        # Try Playfair from any known location
        candidates_serif = [
            '/app/backend/assets/fonts/PlayfairDisplay-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
        ]
        candidates_serif_italic = [
            '/app/backend/assets/fonts/PlayfairDisplay-Italic.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf',
        ]
        for p in candidates_serif:
            if Path(p).exists():
                pdfmetrics.registerFont(TTFont('PlumeSerif', p))
                _FONT_SERIF = 'PlumeSerif'
                _FONT_SERIF_BOLD = 'PlumeSerif'
                break
        for p in candidates_serif_italic:
            if Path(p).exists():
                pdfmetrics.registerFont(TTFont('PlumeSerifItalic', p))
                _FONT_SERIF_ITALIC = 'PlumeSerifItalic'
                break
    except Exception as e:
        logger.warning(f'[cercle_monthly] font registration failed (fallback Helvetica): {e}')


_register_fonts_once()


# ═══════════════════════ PDF Generation ═══════════════════════

def _draw_starry_background(c: canvas.Canvas, w: float, h: float):
    """Fond dégradé bleu nuit + étoiles."""
    # Rectangle solide bleu nuit
    c.setFillColorRGB(*NIGHT_BLUE)
    c.rect(0, 0, w, h, stroke=0, fill=1)
    # Étoiles
    import random
    rng = random.Random(42)  # seed fixe pour reproductibilité
    c.setFillColorRGB(*IVORY)
    for _ in range(60):
        x = rng.uniform(0, w)
        y = rng.uniform(0, h)
        r = rng.uniform(0.3, 1.2)
        c.setFillAlpha(rng.uniform(0.2, 0.6))
        c.circle(x, y, r, stroke=0, fill=1)
    c.setFillAlpha(1)


def _draw_gold_moon(c: canvas.Canvas, cx: float, cy: float, radius: float):
    """Lune dorée avec halo doux."""
    # Halo
    for i in range(8, 0, -1):
        c.setFillColorRGB(*GOLD)
        c.setFillAlpha(0.04 * i / 8)
        c.circle(cx, cy, radius * (1 + i * 0.15), stroke=0, fill=1)
    # Corps
    c.setFillAlpha(1)
    c.setFillColorRGB(*IVORY)
    c.circle(cx, cy, radius, stroke=0, fill=1)
    c.setFillColorRGB(*GOLD)
    c.setFillAlpha(0.3)
    c.circle(cx + radius * 0.25, cy - radius * 0.15, radius * 0.8, stroke=0, fill=1)
    c.setFillAlpha(1)


def _draw_gold_divider(c: canvas.Canvas, cx: float, y: float, width: float = 40 * mm):
    """Trait doré fin centré."""
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.5)
    c.line(cx - width / 2, y, cx + width / 2, y)


def _wrap_text(c: canvas.Canvas, text: str, font: str, size: float, max_width: float) -> list:
    """Word-wrap simple pour ReportLab."""
    words = text.split()
    lines = []
    current = ''
    for w in words:
        test = f'{current} {w}'.strip()
        if c.stringWidth(test, font, size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def _draw_paragraph(c: canvas.Canvas, text: str, x: float, y: float, font: str, size: float,
                    max_width: float, line_height: float, color: tuple = IVORY) -> float:
    """Renvoie le y final après avoir écrit le paragraphe."""
    c.setFont(font, size)
    c.setFillColorRGB(*color)
    lines = _wrap_text(c, text, font, size, max_width)
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height
    return y


def generate_monthly_pdf(first_name: str, sign_name: str, sign_element: str,
                         month_index: int, year: int) -> bytes:
    """Génère le PDF du rapport mensuel. Renvoie les bytes."""
    mood = get_monthly_mood(sign_element, month_index)
    month_name = mood['month_name']
    month_cap = month_name.capitalize()

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    margin = 22 * mm
    text_width = w - 2 * margin

    # ─── PAGE 1 · Couverture ───
    _draw_starry_background(c, w, h)
    _draw_gold_moon(c, w / 2, h - 90 * mm, 22 * mm)

    # Kicker
    c.setFont(_FONT_SANS, 8.5)
    c.setFillColorRGB(*GOLD)
    kicker = f'CERCLE SOLÉNA  ·  RAPPORT MENSUEL  ·  {month_cap.upper()} {year}'
    kw = c.stringWidth(kicker, _FONT_SANS, 8.5)
    # letter-spacing via drawString multiple
    c.drawString((w - kw) / 2 - 20, h - 130 * mm, kicker)

    # Titre principal
    c.setFont(_FONT_SERIF, 26)
    c.setFillColorRGB(*IVORY)
    title = "L'humeur"
    tw = c.stringWidth(title, _FONT_SERIF, 26)
    c.drawString((w - tw) / 2, h - 155 * mm, title)

    c.setFont(_FONT_SERIF_ITALIC, 34)
    c.setFillColorRGB(*GOLD_LIGHT)
    sub = f'de {month_name}'
    sw = c.stringWidth(sub, _FONT_SERIF_ITALIC, 34)
    c.drawString((w - sw) / 2, h - 175 * mm, sub)

    _draw_gold_divider(c, w / 2, h - 195 * mm)

    # Sous-titre — signe
    c.setFont(_FONT_SANS, 11)
    c.setFillColorRGB(*IVORY_DIM)
    signl = f'Personnalisé pour {first_name or "vous"} · Signe {sign_name}'
    slw = c.stringWidth(signl, _FONT_SANS, 11)
    c.drawString((w - slw) / 2, h - 205 * mm, signl)

    # Note bas de page
    c.setFont(_FONT_SANS, 8)
    c.setFillColorRGB(*GOLD)
    footer = 'Plume Astrale · Comprendre les périodes de votre vie'
    fw = c.stringWidth(footer, _FONT_SANS, 8)
    c.drawString((w - fw) / 2, 20 * mm, footer)
    c.showPage()

    # ─── PAGE 2 · Le climat du mois ───
    _draw_starry_background(c, w, h)
    y = h - 30 * mm

    c.setFont(_FONT_SANS, 8.5)
    c.setFillColorRGB(*GOLD)
    c.drawString(margin, y, f'CHAPITRE I  ·  LE CLIMAT DE {month_cap.upper()}')
    y -= 15 * mm

    c.setFont(_FONT_SERIF_ITALIC, 20)
    c.setFillColorRGB(*IVORY)
    title_lines = _wrap_text(c, mood['title'], _FONT_SERIF_ITALIC, 20, text_width)
    for line in title_lines:
        c.drawString(margin, y, line)
        y -= 9 * mm
    y -= 4 * mm

    _draw_gold_divider(c, margin + 20 * mm, y, width=40 * mm)
    y -= 10 * mm

    y = _draw_paragraph(c, mood['body'], margin, y, _FONT_SERIF, 12,
                       text_width, 6.5 * mm, color=IVORY)
    c.showPage()

    # ─── PAGE 3 · Votre lecture personnelle ───
    _draw_starry_background(c, w, h)
    y = h - 30 * mm

    c.setFont(_FONT_SANS, 8.5)
    c.setFillColorRGB(*GOLD)
    c.drawString(margin, y, f'CHAPITRE II  ·  VOTRE LECTURE  ·  {sign_name.upper()}')
    y -= 15 * mm

    c.setFont(_FONT_SERIF_ITALIC, 20)
    c.setFillColorRGB(*GOLD_LIGHT)
    intro = f'Pour vous, signe {sign_name}'
    c.drawString(margin, y, intro)
    y -= 10 * mm

    _draw_gold_divider(c, margin + 20 * mm, y, width=40 * mm)
    y -= 10 * mm

    y = _draw_paragraph(c, mood['accent'], margin, y, _FONT_SERIF, 13,
                       text_width, 7 * mm, color=IVORY)
    y -= 8 * mm

    # Élément
    c.setFont(_FONT_SANS, 8.5)
    c.setFillColorRGB(*GOLD)
    c.drawString(margin, y, f'ÉLÉMENT  ·  {sign_element.upper()}')
    y -= 8 * mm

    element_words = {
        'Feu': "Votre élément est le Feu : l'élan, l'action, l'audace. Ce mois, apprenez à le focaliser.",
        'Terre': "Votre élément est la Terre : la constance, la matière, l'incarnation. Ce mois, laissez-la porter fruit.",
        'Air': "Votre élément est l'Air : l'idée, la parole, le lien. Ce mois, écoutez ce qui circule.",
        'Eau': "Votre élément est l'Eau : le sentir, l'intuition, la profondeur. Ce mois, honorez vos ressentis.",
    }
    y = _draw_paragraph(c, element_words.get(sign_element, ''), margin, y, _FONT_SERIF, 11,
                       text_width, 6 * mm, color=IVORY_DIM)
    c.showPage()

    # ─── PAGE 4 · Journal intime — 3 questions ───
    _draw_starry_background(c, w, h)
    y = h - 30 * mm

    c.setFont(_FONT_SANS, 8.5)
    c.setFillColorRGB(*GOLD)
    c.drawString(margin, y, "CHAPITRE III  ·  VOS TROIS QUESTIONS DU MOIS")
    y -= 15 * mm

    c.setFont(_FONT_SERIF_ITALIC, 20)
    c.setFillColorRGB(*IVORY)
    c.drawString(margin, y, 'À écrire, à relire, à traverser')
    y -= 10 * mm

    _draw_gold_divider(c, margin + 20 * mm, y, width=40 * mm)
    y -= 12 * mm

    c.setFont(_FONT_SERIF, 11)
    c.setFillColorRGB(*IVORY_DIM)
    intro_prompts = ("Prenez un carnet. Répondez sans réfléchir trop longtemps. "
                    "La vérité vient rarement à la première ligne — elle vient à la troisième.")
    y = _draw_paragraph(c, intro_prompts, margin, y, _FONT_SERIF, 11,
                       text_width, 6 * mm, color=IVORY_DIM)
    y -= 8 * mm

    for i, prompt in enumerate(mood['prompts'], 1):
        c.setFont(_FONT_SERIF_ITALIC, 13)
        c.setFillColorRGB(*GOLD_LIGHT)
        c.drawString(margin, y, f'{i}.')
        y = _draw_paragraph(c, prompt, margin + 10 * mm, y, _FONT_SERIF, 13,
                           text_width - 10 * mm, 6.5 * mm, color=IVORY)
        y -= 6 * mm

    # Signature bas de page
    y = 25 * mm
    _draw_gold_divider(c, w / 2, y, width=30 * mm)
    y -= 8 * mm
    c.setFont(_FONT_SERIF_ITALIC, 10)
    c.setFillColorRGB(*IVORY_DIM)
    signoff = 'Avec vous, ce mois-ci comme les suivants — Soléna'
    sfw = c.stringWidth(signoff, _FONT_SERIF_ITALIC, 10)
    c.drawString((w - sfw) / 2, y, signoff)

    c.save()
    return buf.getvalue()


# ═══════════════════════ Email sender ═══════════════════════

def _build_html_email(first_name: str, sign_name: str, month_name: str) -> str:
    return f"""
    <div style="font-family:Georgia,serif;background:#0A1128;padding:32px 24px;color:#F7F5F0;max-width:600px;margin:0 auto;">
      <div style="text-align:center;padding-bottom:32px;border-bottom:1px solid rgba(184,147,90,0.25);">
        <div style="font-size:11px;letter-spacing:0.35em;color:#B8935A;text-transform:uppercase;margin-bottom:16px;font-family:Arial,sans-serif;">
          ✦ Plume Astrale ✦ Cercle Soléna
        </div>
        <h1 style="font-size:32px;font-weight:400;color:#F7F5F0;margin:0;line-height:1.2;">
          L'humeur de <em style="color:#C9A24B;">{month_name}</em>
        </h1>
        <p style="color:rgba(247,245,240,0.72);font-size:14px;margin-top:12px;">
          Votre rapport mensuel · Signe {sign_name}
        </p>
      </div>

      <div style="padding:32px 0;line-height:1.75;font-size:15px;color:rgba(247,245,240,0.9);">
        <p>Bonjour {first_name or 'et bienvenue'},</p>
        <p>
          Voici votre rapport mensuel — l'humeur de {month_name}, écrite pour vous.
          Il vous accompagne comme un carnet à consulter au fil des jours : le climat général
          du mois, votre lecture personnelle en tant que signe {sign_name}, et trois questions
          à traverser cette semaine.
        </p>
        <p>
          Le PDF est joint à ce message. Nous vous conseillons de l'imprimer ou de le
          garder ouvert dans un onglet — il gagne à être relu plusieurs fois dans le mois.
        </p>
        <p style="padding:16px 0;border-top:1px solid rgba(184,147,90,0.20);margin-top:24px;">
          <strong style="color:#C9A24B;">✦ Petit cadeau bonus</strong> — vous trouverez aussi
          en pièce jointe un <strong>mini-visuel Instagram</strong> tout prêt, avec votre
          citation du mois. Si vous voulez le partager en story ou en feed, tag
          <em>@plumeastrale</em> — chaque partage aide d'autres personnes à trouver leur cap.
        </p>
      </div>

      <div style="text-align:center;padding:24px 0;border-top:1px solid rgba(184,147,90,0.20);">
        <p style="color:rgba(247,245,240,0.5);font-size:12px;margin:0 0 8px;">
          Rendez-vous le mois prochain.
        </p>
        <p style="color:#B8935A;font-style:italic;font-size:14px;margin:0;">
          — Soléna
        </p>
      </div>

      <div style="text-align:center;padding-top:16px;font-size:10px;color:rgba(184,147,90,0.55);letter-spacing:0.14em;">
        <a href="https://plume-astrale.fr" style="color:#B8935A;text-decoration:none;">plume-astrale.fr</a>
      </div>
    </div>
    """


async def _send_report_email(email: str, first_name: str, sign_name: str, month_name: str,
                             pdf_bytes: bytes, ig_bytes: bytes | None = None) -> Optional[str]:
    if not RESEND_API_KEY:
        logger.warning('[cercle_monthly] RESEND_API_KEY absent — email non envoyé')
        return None
    pdf_b64 = base64.b64encode(pdf_bytes).decode('ascii')
    pdf_filename = f'humeur-de-{month_name}.pdf'
    subject = f"L'humeur de {month_name} · votre rapport Cercle Soléna"
    html = _build_html_email(first_name, sign_name, month_name)
    attachments = [{'filename': pdf_filename, 'content': pdf_b64}]
    if ig_bytes:
        ig_b64 = base64.b64encode(ig_bytes).decode('ascii')
        attachments.append({
            'filename': f'ig-{sign_name.lower()}-{month_name}.png',
            'content': ig_b64,
        })
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {RESEND_API_KEY}',
                    'Content-Type': 'application/json',
                },
                json={
                    'from': SENDER_EMAIL,
                    'to': [email],
                    'subject': subject,
                    'html': html,
                    'attachments': attachments,
                },
            )
            if r.status_code >= 400:
                logger.warning(f'[cercle_monthly] Resend error {r.status_code}: {r.text[:300]}')
                return None
            try:
                return r.json().get('id')
            except Exception:
                return None
    except Exception as e:
        logger.error(f'[cercle_monthly] send failure for {email}: {e}')
        return None


# ═══════════════════════ Subscribers query ═══════════════════════

def _fetch_active_cercle_subscribers() -> list:
    """Récupère la liste des abonnés Cercle Soléna actifs.
    Filtre : premium_status = 'active' ET (premium_until dans le futur OU null)."""
    sb = get_admin_client()
    if not sb:
        return []
    try:
        # On sélectionne tous les profils premium_status='active' avec email + birth_date
        res = sb.table('profiles').select(
            'id,email,prenom,birth_date,premium_status,premium_until'
        ).eq('premium_status', 'active').execute()
        rows = res.data or []
    except Exception as e:
        logger.warning(f'[cercle_monthly] fetch subscribers failed: {e}')
        return []

    now = datetime.now(timezone.utc)
    subs = []
    for r in rows:
        if not r.get('email') or not r.get('birth_date'):
            continue
        # Vérifier premium_until s'il existe
        pu = r.get('premium_until')
        if pu:
            try:
                until = datetime.fromisoformat(pu.replace('Z', '+00:00'))
                if until <= now:
                    continue
            except Exception:
                pass
        subs.append(r)
    return subs


# ═══════════════════════ Orchestration ═══════════════════════

def _current_month_key() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m')


def _already_sent_this_month() -> bool:
    if not LAST_RUN_FILE.exists():
        return False
    try:
        return LAST_RUN_FILE.read_text().strip() == _current_month_key()
    except Exception:
        return False


def _mark_sent_this_month() -> None:
    try:
        LAST_RUN_FILE.write_text(_current_month_key())
    except Exception as e:
        logger.warning(f'[cercle_monthly] mark_sent failed: {e}')


async def send_monthly_reports_to_all() -> dict:
    """Génère + envoie les rapports mensuels à tous les abonnés Cercle actifs.
    Renvoie {'sent': n, 'failed': m, 'skipped': k}."""
    now = datetime.now(timezone.utc)
    month_index = now.month - 1
    year = now.year

    subs = _fetch_active_cercle_subscribers()
    logger.info(f'[cercle_monthly] {len(subs)} abonné(e)s Cercle Soléna actif(ve)s à servir')

    sent = 0
    failed = 0
    skipped = 0
    for sub in subs:
        email = sub['email']
        first_name = sub.get('prenom') or ''
        sign_info = get_sign_from_birthdate(sub['birth_date'])
        if not sign_info:
            skipped += 1
            logger.warning(f'[cercle_monthly] birth_date invalide pour {email}, skip')
            continue
        sign_name, sign_element = sign_info
        try:
            pdf_bytes = await asyncio.to_thread(
                generate_monthly_pdf, first_name, sign_name, sign_element, month_index, year,
            )
            month_name = MONTH_NAMES_FR[month_index]
            # Génère aussi le mini-visuel IG partageable (empowerment ambassadrice)
            ig_bytes = None
            try:
                from services.instagram_visual import generate_ig_visual
                mood_accent = get_monthly_mood(sign_element, month_index)['accent']
                ig_bytes = await asyncio.to_thread(
                    generate_ig_visual, sign_name, month_name, mood_accent,
                )
            except Exception as e:
                logger.warning(f'[cercle_monthly] IG visual generation failed for {email}: {e}')
            eid = await _send_report_email(email, first_name, sign_name, month_name, pdf_bytes, ig_bytes)
            if eid:
                sent += 1
                logger.info(f'[cercle_monthly] ✓ envoyé à {email} (id={eid}, {sign_name}/{sign_element})')
            else:
                failed += 1
        except Exception as e:
            failed += 1
            logger.exception(f'[cercle_monthly] échec pour {email}: {e}')
        # Petit throttle pour ne pas saturer Resend
        await asyncio.sleep(0.3)

    return {'sent': sent, 'failed': failed, 'skipped': skipped, 'total': len(subs)}


# ═══════════════════════ Scheduler loop ═══════════════════════

def _seconds_until_next_first_of_month() -> float:
    """Nombre de secondes jusqu'au 1er du mois prochain à 6h UTC."""
    now = datetime.now(timezone.utc)
    # Cible : 1er du mois courant à 6h UTC
    target_this_month = now.replace(day=1, hour=6, minute=0, second=0, microsecond=0)
    if now < target_this_month:
        return (target_this_month - now).total_seconds()
    # On a dépassé le 1er 6h → viser le 1er du mois prochain
    if now.month == 12:
        target_next = target_this_month.replace(year=now.year + 1, month=1)
    else:
        target_next = target_this_month.replace(month=now.month + 1)
    return (target_next - now).total_seconds()


async def cercle_monthly_report_loop() -> None:
    """Boucle asyncio : lance l'envoi le 1er du mois à 6h UTC.
    Idempotent : vérifie LAST_RUN_FILE pour ne pas double-envoyer."""
    logger.info('[cercle_monthly] boucle démarrée — cible 1er du mois 6h UTC')

    # Recovery au démarrage : si on est le 1er après 6h et qu'on n'a pas encore tourné
    now = datetime.now(timezone.utc)
    if now.day == 1 and now.hour >= 6 and not _already_sent_this_month():
        logger.info('[cercle_monthly] recovery — pas encore envoyé ce mois, lancement immédiat')
        try:
            result = await send_monthly_reports_to_all()
            logger.info(f'[cercle_monthly] résultat recovery : {result}')
            _mark_sent_this_month()
        except Exception as e:
            logger.exception(f'[cercle_monthly] recovery failed: {e}')

    while True:
        sleep_s = _seconds_until_next_first_of_month()
        days = int(sleep_s // 86400)
        h = int((sleep_s % 86400) // 3600)
        logger.info(f'[cercle_monthly] prochain envoi dans {days}j {h}h')
        try:
            await asyncio.sleep(sleep_s)
        except asyncio.CancelledError:
            logger.info('[cercle_monthly] boucle arrêtée (CancelledError)')
            raise
        # C'est l'heure
        if _already_sent_this_month():
            logger.info('[cercle_monthly] déjà envoyé ce mois-ci, on saute')
            await asyncio.sleep(3600)
            continue
        try:
            result = await send_monthly_reports_to_all()
            logger.info(f'[cercle_monthly] résultat mensuel : {result}')
            _mark_sent_this_month()
        except Exception as e:
            logger.exception(f'[cercle_monthly] envoi mensuel échoué : {e}')
        # Marge de 2h pour éviter re-déclenchement
        await asyncio.sleep(7200)
