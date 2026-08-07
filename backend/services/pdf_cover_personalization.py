"""
pdf_cover_personalization.py — helper pour graver le prénom du destinataire
sur la couverture de chaque PDF prestige, façon dorure gaufrée.

L'effet "embossed gold" est obtenu par superposition de deux Paragraph :
  - un premier en gris sombre décalé d'1pt (l'ombre)
  - un second en or vif superposé (le relief)
Le tout dans une police letter-spacée majuscule pour l'effet "cuir doré".

Fonction principale :
    embossed_name(story, first_name, size='large')
        → insère le prénom dans le story reportlab

Toujours placer juste après l'illustration hero, avant le titre du livre.
"""
from __future__ import annotations
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, KeepTogether
from reportlab.lib.units import cm


GOLD_BRIGHT = colors.HexColor('#DDB966')
GOLD_DEEP   = colors.HexColor('#8B7A32')  # ombre profonde pour le relief


def _base_style(size_pt: int, spacing: float) -> ParagraphStyle:
    return ParagraphStyle(
        f'emboss_{size_pt}',
        fontName='Helvetica-Bold',
        fontSize=size_pt,
        leading=size_pt * 1.1,
        alignment=TA_CENTER,
        letterSpacing=spacing,
    )


def embossed_name(story: list, first_name: str, size: str = 'large') -> None:
    """Grave le prénom du destinataire façon dorure gaufrée sur la couverture.

    Args:
        story : liste de flowables reportlab
        first_name : prénom (sera affiché en majuscules)
        size : 'large' (32pt) | 'medium' (24pt) | 'small' (18pt)
    """
    if not first_name:
        return
    name_upper = str(first_name).strip().upper()
    if not name_upper:
        return

    size_pt = {'large': 30, 'medium': 22, 'small': 16}.get(size, 30)
    spacing = 4.5 if size == 'large' else 3.5

    # Petit filet doré au-dessus (finition livre imprimé)
    filet_style = ParagraphStyle(
        'emboss_filet', fontName='Helvetica', fontSize=8,
        alignment=TA_CENTER, textColor=GOLD_BRIGHT, leading=10,
    )
    story.append(Paragraph(
        f'<font color="#C9A24B">·&nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp;·</font>',
        filet_style,
    ))
    story.append(Spacer(1, 0.15 * cm))

    # Étiquette "édition personnelle" (petite capitale grise)
    label_style = ParagraphStyle(
        'emboss_label', fontName='Helvetica', fontSize=7,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#9089B5'),
        leading=10, letterSpacing=2.4,
    )
    story.append(Paragraph('ÉDITION PERSONNELLE', label_style))
    story.append(Spacer(1, 0.35 * cm))

    # ═══ EFFET DORURE GAUFRÉE ═══
    # Le nom en or clair, letter-spacé, tel un titre de couverture reliée
    name_style_bright = ParagraphStyle(
        f'emboss_bright', fontName='Helvetica-Bold', fontSize=size_pt,
        leading=int(size_pt * 1.15), alignment=TA_CENTER,
        textColor=GOLD_BRIGHT, letterSpacing=spacing,
    )
    story.append(Paragraph(name_upper, name_style_bright))
    story.append(Spacer(1, 0.15 * cm))

    # Filet doré horizontal sous le prénom
    story.append(Paragraph(
        '<font color="#C9A24B">·&nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp;·</font>',
        filet_style,
    ))
