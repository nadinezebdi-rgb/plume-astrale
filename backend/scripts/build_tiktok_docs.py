"""
Génère 2 PDFs de démonstration pour le tournage TikTok :
  1. Modèle de Guidance Soléna (2 pages) — la philosophie/framework
  2. Horoscope Journalier Lion (2 pages) — exemple de sortie quotidienne

Sortie : /app/frontend/public/marketing/*.pdf
"""
from __future__ import annotations
import io
import sys
from datetime import datetime, date
from pathlib import Path

# Ensure backend imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage,
    Table, TableStyle,
)
from reportlab.lib.colors import HexColor

from services.pdf_theme import (
    register_fonts, make_styles, font,
    GOLD, GOLD_LIGHT, CREAM, LAVENDER, MUTED, NIGHT, NIGHT_SOFT,
)
from services.pdf_luxury_theme import (
    luxury_bg, luxury_styles, illustration_url, _dl_image,
)

# Register Unicode-heavy fallback fonts for astro symbols (♌ ✦ ❤ ☾ ✧ ♂ ♀ ...)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
try:
    pdfmetrics.registerFont(TTFont('Symbola', '/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf'))
    _SYMBOL_FONT = 'Symbola'
except Exception:
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        _SYMBOL_FONT = 'DejaVuSans'
    except Exception:
        _SYMBOL_FONT = 'Helvetica'


def _sym(text: str, color: str = None) -> str:
    """Wrap Unicode symbols in a font tag that can actually render them."""
    if color:
        return f'<font name="{_SYMBOL_FONT}" color="{color}">{text}</font>'
    return f'<font name="{_SYMBOL_FONT}">{text}</font>'


OUT_DIR = Path('/app/frontend/public/marketing')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _build(path: Path, story: list) -> Path:
    doc = SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
    print(f'✓ {path.name}  ({path.stat().st_size // 1024} KB)')
    return path


# ─────────────────────────────────────────────────────────
# PDF 1 — MODÈLE DE GUIDANCE SOLÉNA
# ─────────────────────────────────────────────────────────
def build_guidance_pdf() -> Path:
    styles = luxury_styles()
    story = []

    # Page 1 — Cover
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph(f'{_sym("✦")}  PLUME  ASTRALE  {_sym("✦")}', styles['section_tag']))
    story.append(Spacer(1, 1.2 * cm))

    img = _dl_image(illustration_url('astral_mandala', 800))
    if img:
        story.append(RLImage(img, width=9 * cm, height=9 * cm, mask='auto'))
        story.append(Spacer(1, 1.5 * cm))

    story.append(Paragraph('Le Modèle', styles['cover_title']))
    story.append(Paragraph('de Guidance Soléna', styles['cover_sub']))
    story.append(Spacer(1, 1 * cm))

    dialog_center = ParagraphStyle(
        'dialog_center', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
        fontSize=15, leading=24, textColor=CREAM, alignment=TA_CENTER,
        leftIndent=1 * cm, rightIndent=1 * cm,
    )
    story.append(Paragraph(
        "«&nbsp;Je n'ai pas créé Plume Astrale pour te dire quoi faire.<br/>"
        "Je l'ai créé pour que tu comprennes enfin<br/>"
        "pourquoi tu ressens ce que tu ressens.&nbsp;»",
        dialog_center,
    ))
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph('— Soléna', styles['signature']))

    story.append(PageBreak())

    # Page 2 — Les 5 principes
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph('LES CINQ PRINCIPES', styles['section_tag']))
    story.append(Spacer(1, 0.5 * cm))

    section_h = ParagraphStyle(
        'section_h', fontName=font('Cinzel', 'Helvetica'),
        fontSize=14, leading=22, textColor=GOLD_LIGHT,
        alignment=TA_LEFT, spaceAfter=6,
    )
    body = ParagraphStyle(
        'body_luxe2', fontName=font('Cormorant', 'Helvetica'),
        fontSize=12.5, leading=20, textColor=CREAM,
        alignment=TA_LEFT, spaceAfter=16,
    )

    principles = [
        ('I. CLARTÉ AVANT PRÉDICTION',
         "Je ne prédis pas ton avenir. Je t'aide à voir clair dans ton présent. "
         "Comprendre l'énergie du moment change tout — c'est là que naissent les vraies décisions."),
        ('II. TON RESSENTI EST DÉJÀ UNE RÉPONSE',
         "Ce que tu ressens n'est pas un obstacle. C'est un signal. "
         "Mon rôle : traduire ces signaux à travers ton thème astral pour que tu ne les subisses plus."),
        ('III. RIEN N\'EST FIGÉ',
         "Les astres inclinent, ils ne déterminent pas. "
         "Chaque configuration est une invitation, pas une sentence."),
        ('IV. LA DOUCEUR EST UN OUTIL',
         "Je ne juge pas. Je ne moralise pas. "
         "Je t'accompagne comme une amie qui aurait passé sa vie à étudier ton ciel."),
        ('V. TU DÉCIDES, TOUJOURS',
         "Je n'ai pas de vérité à imposer. Tu es le seul auteur de ta vie. "
         "Ma guidance est un miroir, pas un ordre."),
    ]
    for title, txt in principles:
        story.append(Paragraph(title, section_h))
        story.append(Paragraph(txt, body))

    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(_sym('✦', GOLD.hexval() if hasattr(GOLD, 'hexval') else '#D4AF37'), ParagraphStyle(
        'sep', fontName='Helvetica', fontSize=18, textColor=GOLD,
        alignment=TA_CENTER, spaceAfter=8,
    )))
    story.append(PageBreak())

    # Page 3 — La structure d'une guidance
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph('LA STRUCTURE D\'UNE GUIDANCE', styles['section_tag']))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(
        "Chaque échange avec Soléna suit un rythme précis —<br/>"
        "pensé pour te ramener à toi, pas t'éloigner de toi.",
        ParagraphStyle('intro', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                       fontSize=14, leading=22, textColor=LAVENDER,
                       alignment=TA_CENTER, spaceAfter=24),
    ))

    step_num = ParagraphStyle(
        'step_num', fontName=font('Cinzel', 'Helvetica'),
        fontSize=32, leading=36, textColor=GOLD,
        alignment=TA_LEFT, spaceAfter=0,
    )
    step_title = ParagraphStyle(
        'step_title', fontName=font('Cinzel', 'Helvetica'),
        fontSize=13, leading=20, textColor=GOLD_LIGHT,
        alignment=TA_LEFT, spaceAfter=4,
    )
    step_body = ParagraphStyle(
        'step_body', fontName=font('Cormorant', 'Helvetica'),
        fontSize=12, leading=18, textColor=CREAM,
        alignment=TA_LEFT, spaceAfter=12,
    )

    steps = [
        ('01', 'ACCUEILLIR',
         'Ta question, ton silence, ton besoin. Aucune émotion n\'est déplacée ici.'),
        ('02', 'LIRE LE CIEL',
         'Je consulte les positions actuelles + ton thème natal pour identifier l\'énergie qui te traverse.'),
        ('03', 'TRADUIRE',
         'Je te restitue ce que je vois — sans jargon, sans mystique inutile. Juste des mots simples et vrais.'),
        ('04', 'ÉCLAIRER',
         'Je te propose un angle, une clef de compréhension, une invitation. Jamais une injonction.'),
        ('05', 'TE LAISSER LIBRE',
         'Tu ressors avec plus de clarté, pas avec plus de règles. La suite t\'appartient.'),
    ]
    for num, ttl, txt in steps:
        table = Table(
            [[Paragraph(num, step_num), [
                Paragraph(ttl, step_title),
                Paragraph(txt, step_body),
            ]]],
            colWidths=[2.5 * cm, 13 * cm],
        )
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.15 * cm))

    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        "Plume Astrale n'est pas un produit d'astrologie.<br/>"
        "C'est une compagne de clarté.",
        ParagraphStyle('closing', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                       fontSize=17, leading=26, textColor=GOLD_LIGHT,
                       alignment=TA_CENTER),
    ))

    return _build(OUT_DIR / 'modele_guidance_solena.pdf', story)


# ─────────────────────────────────────────────────────────
# PDF 2 — HOROSCOPE JOURNALIER LION
# ─────────────────────────────────────────────────────────
def build_horoscope_journalier_pdf() -> Path:
    styles = luxury_styles()
    story = []

    today = date.today()
    # Manual French date (locale not always available)
    _MOIS_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    _JOURS_FR = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    date_fr = f"{_JOURS_FR[today.weekday()]} {today.day} {_MOIS_FR[today.month - 1]} {today.year}"

    # Page 1 — cover
    story.append(Spacer(1, 1.4 * cm))
    story.append(Paragraph(f'{_sym("✦")}  HOROSCOPE JOURNALIER  {_sym("✦")}', styles['section_tag']))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(date_fr, ParagraphStyle(
        'date_top', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
        fontSize=14, textColor=MUTED, alignment=TA_CENTER, spaceAfter=20,
    )))

    # Sign illustration
    img = _dl_image(illustration_url('roue_zodiaque', 800))
    if img:
        story.append(RLImage(img, width=6.5 * cm, height=6.5 * cm, mask='auto'))
        story.append(Spacer(1, 0.6 * cm))

    story.append(Paragraph('Lion', ParagraphStyle(
        'sign_title', fontName=font('Cormorant', 'Helvetica'),
        fontSize=56, leading=64, textColor=CREAM, alignment=TA_CENTER,
    )))
    story.append(Paragraph(f'{_sym("♌")}   23 juillet — 22 août', ParagraphStyle(
        'sign_dates', fontName=font('Cinzel', 'Helvetica'),
        fontSize=11, textColor=GOLD, alignment=TA_CENTER, spaceAfter=24,
    )))

    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(
        "«&nbsp;Aujourd'hui, ton éclat n'a besoin de personne pour exister.&nbsp;»",
        ParagraphStyle('opener', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                       fontSize=17, leading=26, textColor=GOLD_LIGHT,
                       alignment=TA_CENTER, leftIndent=1 * cm, rightIndent=1 * cm),
    ))

    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph('Lu par Soléna', styles['signature']))

    story.append(PageBreak())

    # Page 2 — Sections détaillées
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph('L\'ÉNERGIE DU JOUR', styles['section_tag']))
    story.append(Spacer(1, 0.2 * cm))

    body = ParagraphStyle(
        'body_hor', fontName=font('Cormorant', 'Helvetica'),
        fontSize=11.5, leading=18, textColor=CREAM,
        alignment=TA_LEFT, spaceAfter=8,
    )
    section_h = ParagraphStyle(
        'section_hor', fontName=font('Cinzel', 'Helvetica'),
        fontSize=11, leading=16, textColor=GOLD_LIGHT,
        alignment=TA_LEFT, spaceAfter=4, spaceBefore=6,
    )

    story.append(Paragraph(
        "Le Soleil, ton maître planétaire, forme un trigone harmonique à Jupiter. "
        "Une vague de confiance douce te traverse — pas l'ego bruyant, "
        "mais cette certitude tranquille de mériter ta place.",
        body,
    ))

    story.append(Paragraph(f'{_sym("♥")}  AMOUR', section_h))
    story.append(Paragraph(
        "Vénus favorise la sincérité. Dis ce que tu penses vraiment — "
        "sans travestir, sans adoucir. Ton authenticité est magnétique aujourd'hui.",
        body,
    ))

    story.append(Paragraph(f'{_sym("◆")}  CARRIÈRE', section_h))
    story.append(Paragraph(
        "Un projet longtemps mis de côté demande à ressurgir. "
        "Ne le juge pas sur son ancienne forme — il revient transformé.",
        body,
    ))

    story.append(Paragraph(f'{_sym("☾")}  BIEN-ÊTRE', section_h))
    story.append(Paragraph(
        "Ton corps a besoin de mouvement solaire : marche à l'extérieur, "
        "danse, chaleur. Évite les écrans après 21h.",
        body,
    ))

    # ── SECTION HÉRO — LA GUIDANCE DU JOUR ─────────────
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        f'{_sym("✦")}  LA GUIDANCE DU JOUR  {_sym("✦")}',
        ParagraphStyle('guidance_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=11, textColor=GOLD, alignment=TA_CENTER,
                       spaceAfter=8),
    ))
    story.append(Paragraph(
        "«&nbsp;Ne cherche pas à convaincre. Sois.<br/>"
        "Ceux qui doivent te suivre le feront<br/>"
        "sans qu'il faille les tirer.&nbsp;»",
        ParagraphStyle('guidance_body', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                       fontSize=15, leading=24, textColor=GOLD_LIGHT,
                       alignment=TA_CENTER, leftIndent=0.5 * cm, rightIndent=0.5 * cm,
                       spaceAfter=8),
    ))
    story.append(Paragraph(
        "— Soléna",
        ParagraphStyle('guidance_sig', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                       fontSize=11, textColor=MUTED,
                       alignment=TA_CENTER, spaceAfter=14),
    ))

    # Practical infos as pill boxes
    tips_data = [
        [Paragraph(_sym('◈') + '  Pierre du jour', body), Paragraph('Citrine', body)],
        [Paragraph(_sym('❦') + '  Couleur', body), Paragraph('Doré antique', body)],
        [Paragraph(_sym('❋') + '  Aromate', body), Paragraph('Cannelle', body)],
        [Paragraph(_sym('☉') + '  Heure favorable', body), Paragraph('11h — 15h', body)],
        [Paragraph(_sym('✧') + '  Chiffre', body), Paragraph('3', body)],
    ]
    tips_style = TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, HexColor('#3a2f5a')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ])
    tips_table = Table(tips_data, colWidths=[7 * cm, 8.5 * cm], style=tips_style)
    story.append(tips_table)

    story.append(Spacer(1, 0.35 * cm))
    story.append(Paragraph(
        f"{_sym('✦')}  question de réflexion  {_sym('✦')}",
        ParagraphStyle('q_intro', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=9, textColor=GOLD,
                       alignment=TA_CENTER, spaceAfter=4),
    ))
    story.append(Paragraph(
        "«&nbsp;Que rayonnerais-tu aujourd'hui<br/>"
        "si tu n'attendais l'approbation de personne&nbsp;?&nbsp;»",
        ParagraphStyle('q_body', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                       fontSize=13, leading=20, textColor=CREAM,
                       alignment=TA_CENTER, leftIndent=0.8 * cm, rightIndent=0.8 * cm,
                       spaceAfter=10),
    ))

    story.append(Paragraph(
        "plume-astrale.fr",
        ParagraphStyle('url', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=8, textColor=MUTED,
                       alignment=TA_CENTER),
    ))

    return _build(OUT_DIR / 'horoscope_journalier_lion_exemple.pdf', story)


if __name__ == '__main__':
    build_guidance_pdf()
    build_horoscope_journalier_pdf()
