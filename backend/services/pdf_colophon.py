"""
pdf_colophon.py — colophon Nocturne partagé pour tous les PDFs Plume Astrale.

Insère en dernière page :
  - Sceau doré + citation Soléna
  - Code de parrainage + QR code (converti en JPEG compressé)
  - Signature « — Soléna, voix éditoriale de Plume Astrale »
  - Kicker JetBrains Mono en pied avec édition/date

Usage :
    from services.pdf_colophon import build_colophon
    story = build_colophon(
        story,
        styles,
        prenom='Sophie',
        referral_code='SOPH1234',
        referral_link='https://plume-astrale.fr/?ref=SOPH1234',
        product_name='Thème Natal',
    )

Le code est safe : si `qrcode` est absent ou la génération échoue, la page
tombe en fallback texte-only (aucun crash).
"""
from __future__ import annotations
import logging
from datetime import datetime
from io import BytesIO
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, PageBreak, Image as RLImage, KeepTogether

logger = logging.getLogger(__name__)


def _generate_qr_bytes(url: str, box_size: int = 8) -> Optional[bytes]:
    """Génère un QR code PNG pour l'URL de parrainage. Retourne None en cas d'échec."""
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_M
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_M,
            box_size=box_size,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='#0F1A3C', back_color='#F5EEE0')
        buf = BytesIO()
        img.save(buf, format='PNG')
        raw = buf.getvalue()
        # Compression douce — les QR sont déjà petits (~1 Ko), mais on garantit
        # une taille minime dans le PDF.
        try:
            from services.pdf_luxury_helpers import compress_image_bytes
            return compress_image_bytes(raw, max_width=400, quality=92, force_jpeg=False)
        except Exception:
            return raw
    except Exception as e:
        logger.warning(f'[pdf_colophon] QR generation failed: {e}')
        return None


def build_colophon(
    story: list,
    styles: dict,
    prenom: str,
    referral_code: Optional[str] = None,
    referral_link: Optional[str] = None,
    product_name: str = 'Plume Astrale',
) -> None:
    """Ajoute au `story` reportlab une page colophon Nocturne complète.

    Sans effet cassant : si `referral_code` est absent, la page se réduit à
    la citation Soléna + signature (pas de QR ni de bloc partenariat).
    """
    from services.pdf_theme import (
        register_fonts, font, GOLD, GOLD_LIGHT, CREAM, MUTED, LAVENDER,
    )
    register_fonts()

    display_font = font('Cinzel', 'Helvetica')
    display_bold = font('Cinzel-Bold', 'Helvetica-Bold')
    italic = font('Cormorant-Italic', 'Helvetica-Oblique')
    body = font('Cormorant', 'Helvetica')

    # ═══ Ouverture — sceau doré + citation ═══
    story.append(Spacer(1, 2.2 * cm))
    story.append(Paragraph(
        f'<font name="OrnamentSerif" color="#D4AF37" size="24">✦</font>',
        ParagraphStyle('colophon_star', fontName=display_font,
                       fontSize=24, alignment=TA_CENTER, leading=28),
    ))
    story.append(Spacer(1, 0.8 * cm))

    citation_style = ParagraphStyle(
        'colophon_citation', fontName=italic,
        fontSize=15, textColor=LAVENDER,
        alignment=TA_CENTER, leading=22, spaceAfter=8,
    )
    story.append(Paragraph(
        f'« Ton ciel n\'écrit pas ton destin,<br/>'
        f'{prenom or "voyageuse"} — il éclaire simplement<br/>'
        f'le chemin que tu es libre d\'emprunter. »',
        citation_style,
    ))
    story.append(Spacer(1, 0.5 * cm))

    signature_style = ParagraphStyle(
        'colophon_signature', fontName=italic,
        fontSize=13, textColor=GOLD, alignment=TA_CENTER, leading=16,
    )
    story.append(Paragraph(
        '— Soléna,<br/>'
        '<font size="10" color="#9089B5">voix éditoriale de Plume Astrale</font>',
        signature_style,
    ))
    story.append(Spacer(1, 1.4 * cm))

    # ═══ Bloc partenariat (uniquement si code parrainage disponible) ═══
    if referral_code and referral_link:
        # Ligne de séparation dorée
        story.append(Paragraph(
            '<font color="#D4AF37">'
            '<font name="OrnamentSerif">─ ✦ ─</font>'
            '</font>',
            ParagraphStyle('colophon_sep', fontName=display_font,
                           fontSize=13, alignment=TA_CENTER, leading=18),
        ))
        story.append(Spacer(1, 0.8 * cm))

        story.append(Paragraph(
            'PARTAGER PLUME ASTRALE',
            ParagraphStyle('colophon_label', fontName=display_font,
                           fontSize=9, textColor=GOLD,
                           alignment=TA_CENTER, leading=12),
        ))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph(
            '<i>Ton code personnel offre à qui te lit<br/>'
            '<b><font color="#E8C766">–15%</font></b> sur son premier livre.</i>',
            ParagraphStyle('colophon_gift', fontName=body,
                           fontSize=11.5, textColor=CREAM,
                           alignment=TA_CENTER, leading=16),
        ))
        story.append(Spacer(1, 0.6 * cm))

        # ═══ QR code + code lisible côte à côte ═══
        qr_png = _generate_qr_bytes(referral_link, box_size=10)
        code_style = ParagraphStyle(
            'colophon_code', fontName=display_bold,
            fontSize=22, textColor=GOLD_LIGHT, alignment=TA_CENTER,
            leading=26, letterSpacing=4, spaceAfter=6,
        )
        url_style = ParagraphStyle(
            'colophon_url', fontName=body,
            fontSize=9, textColor=MUTED, alignment=TA_CENTER, leading=12,
        )

        if qr_png:
            try:
                qr_img = RLImage(BytesIO(qr_png), width=3.2 * cm, height=3.2 * cm, mask='auto')
                qr_img.hAlign = 'CENTER'
                # KeepTogether pour éviter que le QR se sépare du code au page-break
                block = [
                    qr_img,
                    Spacer(1, 0.35 * cm),
                    Paragraph(referral_code.upper(), code_style),
                    Paragraph(referral_link.replace('https://', ''), url_style),
                ]
                story.append(KeepTogether(block))
            except Exception as e:
                logger.warning(f'[pdf_colophon] QR image embed failed: {e}')
                story.append(Paragraph(referral_code.upper(), code_style))
                story.append(Paragraph(referral_link.replace('https://', ''), url_style))
        else:
            story.append(Paragraph(referral_code.upper(), code_style))
            story.append(Paragraph(referral_link.replace('https://', ''), url_style))

    # ═══ Kicker éditorial en pied ═══
    story.append(Spacer(1, 1.6 * cm))
    edition_style = ParagraphStyle(
        'colophon_edition', fontName=display_font,
        fontSize=8, textColor=MUTED, alignment=TA_CENTER, leading=11,
        letterSpacing=3,
    )
    year = datetime.now().year
    story.append(Paragraph(
        f'PLUME ASTRALE · {product_name.upper()} · ÉDITION NOCTURNE {year}',
        edition_style,
    ))
    story.append(Paragraph(
        f'<font size="7" color="#9089B5">Généré le {datetime.now().strftime("%d %B %Y").lower()} · pour {prenom or "toi"}</font>',
        edition_style,
    ))
