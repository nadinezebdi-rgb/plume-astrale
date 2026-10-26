"""natal_ex_libris — Page Ex-Libris bibliophile pour le Thème Natal.

Lot 3 du refactor PDF (demande user 2026-02-27, affinée 2026-02-28) :
Page de signature bibliophilique à insérer après la dédicace. Le visuel
principal est une illustration pleine page d'une bibliothèque enchantée
sous le ciel étoilé avec reliures dorées (générée via Nano Banana et
stockée en asset local). Le texte s'intègre dans le cartouche du haut et
dans un bandeau parchemin discret en bas.

Composition :
  - Fond pleine page : illustration bibliothèque (navy + or)
  - Cartouche haut (zone claire native de l'image) :
      · « EX LIBRIS »
      · « Ce livre appartient à <Prénom> »
  - Mini-frise astro (Soleil ☉ · Lune ☽ · Ascendant ⇑) sur le ciel étoilé
  - Bandeau parchemin bas (semi-opaque crème) :
      · citation courte
      · « Composé sous le ciel du <date FR> »
      · Numéro de copie unique (P-ASTRAL-00000)
      · « Plume Astrale · Atelier d'édition astrale »
"""
from __future__ import annotations

import hashlib
import math
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Flowable, PageBreak

from services.pdf_theme import font, register_fonts


# Asset illustration (généré via tools/generate_ex_libris_library_asset.py)
_LIBRARY_ASSET = Path(__file__).resolve().parents[1] / 'assets' / 'library' / 'ex_libris_bibliotheque.png'

# Palette alignée sur l'illustration
NAVY_DEEP   = HexColor('#0A1026')  # fond nuit (fallback / bandes letterbox)
GOLD_DEEP   = HexColor('#B8870F')
GOLD_LIGHT  = HexColor('#D4AF37')
INK_SEPIA   = HexColor('#2B1A08')
INK_SOFT    = HexColor('#5B4524')
PARCHMENT   = HexColor('#F3E7CB')   # bandeau crème semi-opaque
PARCHMENT_SHADOW = HexColor('#C9B98A')


def generate_copy_number(prenom: str, birth_date: str) -> str:
    """Génère un numéro de copie unique et déterministe (format P-ASTRAL-XXXXX)."""
    seed = f'{(prenom or "").lower().strip()}|{birth_date or ""}'
    h = int(hashlib.sha256(seed.encode()).hexdigest()[:6], 16) % 100000
    return f'P-ASTRAL-{h:05d}'


class _ExLibrisFlowable(Flowable):
    """Flowable pleine page : illustration bibliothèque + overlays typographiques."""

    def __init__(self,
                 prenom: str,
                 sun_sign: str,
                 moon_sign: str,
                 asc_sign: Optional[str],
                 edition_date_fr: str,
                 copy_number: str,
                 citation: str,
                 no_birth_time: bool = False,
                 birth_time_fr: Optional[str] = None,
                 birth_place: Optional[str] = None):
        super().__init__()
        self.prenom = (prenom or 'Lecteur').strip() or 'Lecteur'
        self.sun_sign = sun_sign or ''
        self.moon_sign = moon_sign or ''
        self.asc_sign = asc_sign or ''
        self.edition_date_fr = edition_date_fr
        self.copy_number = copy_number
        self.citation = citation
        self.no_birth_time = no_birth_time
        self.birth_time_fr = (birth_time_fr or '').strip() or None
        self.birth_place = (birth_place or '').strip() or None

    def wrap(self, availWidth, availHeight):
        self._avail_w = availWidth
        self._avail_h = availHeight
        return (availWidth, availHeight)

    def draw(self):
        c = self.canv
        w, h = A4
        # Annule la translation Platypus pour dessiner en coordonnées A4 absolues.
        # Marges du doc natal (cf. natal_pdf_v2.py) : left=2.2cm, bottom=2cm.
        c.saveState()
        c.translate(-2.2 * cm, -2.0 * cm)

        # ─── 1. Fond pleine page : illustration bibliothèque ───
        # Fallback fond navy si l'asset est absent (environnement de dev sans génération).
        c.setFillColor(NAVY_DEEP)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        if _LIBRARY_ASSET.exists():
            try:
                c.drawImage(
                    str(_LIBRARY_ASSET), 0, 0,
                    width=w, height=h,
                    preserveAspectRatio=False,
                    mask='auto',
                )
            except Exception:
                # En cas d'image corrompue, garder le fond navy et logger silencieusement.
                pass

        # Chargement polices
        display_font = font('Cinzel', 'Helvetica')
        display_bold = font('Cinzel-Bold', 'Helvetica-Bold')
        italic_font  = font('Cormorant-Italic', 'Helvetica-Oblique')
        serif_font   = font('Cormorant', 'Helvetica')
        glyph_font   = font('OrnamentSerif', 'Helvetica')

        # ─── 2. Texte dans le cartouche du haut (zone claire native) ───
        # Cartouche image ≈ x[35%..64%], y_top[4%..28%]  →  A4 : x[208..380], y[608..807]
        # On centre horizontalement et compose à l'intérieur.
        cx = w / 2
        y_card_top = h - 2.4 * cm       # ~ y 807
        y_card_bot = h - 6.5 * cm       # ~ y 608

        # Étoile de tête
        c.setFillColor(GOLD_DEEP)
        c.setFont(glyph_font, 11)
        c.drawCentredString(cx, y_card_top - 0.1 * cm, '✦')

        # « EX LIBRIS »
        c.setFillColor(INK_SEPIA)
        c.setFont(display_bold, 18)
        c.drawCentredString(cx, y_card_top - 1.0 * cm, 'E X   L I B R I S')

        # Filet or sous le titre
        c.setStrokeColor(GOLD_DEEP)
        c.setLineWidth(0.5)
        c.line(cx - 1.8 * cm, y_card_top - 1.3 * cm, cx + 1.8 * cm, y_card_top - 1.3 * cm)

        # « Ce livre appartient à »
        c.setFillColor(INK_SOFT)
        c.setFont(italic_font, 10)
        c.drawCentredString(cx, y_card_top - 1.9 * cm, 'Ce livre appartient à')

        # Prénom (grande italique sépia) — adapte la taille si prénom long
        prenom_size = 24 if len(self.prenom) <= 12 else 20 if len(self.prenom) <= 18 else 16
        c.setFillColor(INK_SEPIA)
        c.setFont(italic_font, prenom_size)
        c.drawCentredString(cx, y_card_top - 3.1 * cm, self.prenom)

        # Filet or de clôture
        c.setStrokeColor(GOLD_DEEP)
        c.setLineWidth(0.4)
        c.line(cx - 1.0 * cm, y_card_bot + 0.4 * cm, cx + 1.0 * cm, y_card_bot + 0.4 * cm)

        # ─── 3. Mini-frise astro Soleil · Lune · (Ascendant) ───
        # Placée sur le ciel étoilé, sous le cartouche.
        self._draw_astro_frieze(c, cx, h - 8.6 * cm,
                                display_font, italic_font, glyph_font)

        # ─── 4. Bandeau parchemin en bas pour la méta-info ───
        self._draw_parchment_band(c, w, h,
                                  display_font, display_bold,
                                  italic_font, serif_font, glyph_font)

        c.restoreState()

    # ───────────────────────── helpers ─────────────────────────

    def _draw_astro_frieze(self, c, cx, cy, display_font, italic_font, glyph_font):
        """Mini-frise horizontale : Soleil · Lune · (Ascendant) sur fond ciel."""
        glyphs = [('☉', self.sun_sign), ('☽', self.moon_sign)]
        if self.asc_sign and not self.no_birth_time:
            glyphs.append(('⇑', self.asc_sign))

        n = len(glyphs)
        spacing = 3.2 * cm
        total_w = spacing * (n - 1)
        start_x = cx - total_w / 2

        for i, (glyph, sign) in enumerate(glyphs):
            gx = start_x + i * spacing

            # Petit médaillon rond doré en arrière-plan (translucide via trait seul)
            c.setFillColor(HexColor('#0A1026'))
            c.setStrokeColor(GOLD_LIGHT)
            c.setLineWidth(0.6)
            c.circle(gx, cy, 0.75 * cm, fill=1, stroke=1)

            # Glyphe astrologique en or
            c.setFillColor(GOLD_LIGHT)
            c.setFont(glyph_font, 16)
            c.drawCentredString(gx, cy - 5, glyph)

            # Mini-nom du signe en italique crème sous le médaillon
            if sign:
                c.setFillColor(HexColor('#F3E7CB'))
                c.setFont(italic_font, 8)
                c.drawCentredString(gx, cy - 1.1 * cm, sign)

        # Petits séparateurs ✦ entre médaillons
        for i in range(n - 1):
            sep_x = start_x + (i + 0.5) * spacing
            c.setFillColor(GOLD_LIGHT)
            c.setFont(glyph_font, 8)
            c.drawCentredString(sep_x, cy - 3, '✦')

    def _draw_parchment_band(self, c, w, h,
                             display_font, display_bold,
                             italic_font, serif_font, glyph_font):
        """Bandeau crème semi-opaque en bas : citation + copy # + date + signature."""
        band_h = 4.8 * cm
        band_y = 1.4 * cm
        band_margin_x = 1.6 * cm

        # Ombre portée (fine bande plus sombre juste sous le bandeau)
        c.setFillColor(HexColor('#2B1A08'))
        c.setStrokeColor(HexColor('#2B1A08'))
        c.setLineWidth(0)
        c.rect(band_margin_x + 0.08 * cm, band_y - 0.1 * cm,
               w - 2 * band_margin_x, band_h, fill=1, stroke=0)

        # Bandeau parchemin principal
        c.setFillColor(PARCHMENT)
        c.setStrokeColor(GOLD_DEEP)
        c.setLineWidth(0.8)
        c.rect(band_margin_x, band_y, w - 2 * band_margin_x, band_h,
               fill=1, stroke=1)
        # Filet interne doré
        c.setLineWidth(0.3)
        c.rect(band_margin_x + 0.2 * cm, band_y + 0.2 * cm,
               w - 2 * (band_margin_x + 0.2 * cm), band_h - 0.4 * cm,
               fill=0, stroke=1)

        cx = w / 2

        # Citation (centrée, italique sépia, max 3 lignes)
        c.setFillColor(INK_SEPIA)
        c.setFont(italic_font, 11)
        quote_lines = self._wrap_quote(self.citation, max_width_cm=14)
        y_quote = band_y + band_h - 0.9 * cm
        for line in quote_lines:
            c.drawCentredString(cx, y_quote, line)
            y_quote -= 0.45 * cm

        # Petit séparateur ornemental
        c.setFillColor(GOLD_DEEP)
        c.setFont(glyph_font, 10)
        c.drawCentredString(cx, band_y + 1.75 * cm, '✦')
        c.setStrokeColor(GOLD_DEEP)
        c.setLineWidth(0.4)
        c.line(cx - 2.0 * cm, band_y + 1.65 * cm, cx - 0.5 * cm, band_y + 1.65 * cm)
        c.line(cx + 0.5 * cm, band_y + 1.65 * cm, cx + 2.0 * cm, band_y + 1.65 * cm)

        # « Composé sous le ciel du … [, à Xh YY], [à <lieu>] »
        c.setFillColor(INK_SOFT)
        c.setFont(serif_font, 10)
        composed_line = f'Composé sous le ciel du {self.edition_date_fr}'
        if self.birth_time_fr:
            composed_line += f', à {self.birth_time_fr}'
        if self.birth_place:
            composed_line += f', à {self.birth_place}'
        c.drawCentredString(cx, band_y + 1.15 * cm, composed_line)

        # Numéro de copie
        c.setFillColor(GOLD_DEEP)
        c.setFont(display_font, 9)
        c.drawCentredString(cx, band_y + 0.75 * cm,
                            f'Exemplaire — {self.copy_number}')

        # Pied Plume Astrale
        c.setFillColor(INK_SEPIA)
        c.setFont(display_bold, 9)
        c.drawCentredString(cx, band_y + 0.35 * cm,
                            "P L U M E   A S T R A L E   ·   Atelier d'édition astrale")

    def _wrap_quote(self, text: str, max_width_cm: float) -> list:
        """Découpe une citation en lignes (approx char-based)."""
        if not text:
            return []
        max_chars = int(max_width_cm * 5.5)
        words = text.split()
        lines, current = [], ''
        for word in words:
            if len(current) + 1 + len(word) <= max_chars:
                current = f'{current} {word}'.strip()
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines[:3]


def ex_libris_page(story: list,
                   prenom: str,
                   birth_date: str,
                   sun_sign: str,
                   moon_sign: str,
                   asc_sign: Optional[str] = None,
                   edition_date_fr: Optional[str] = None,
                   no_birth_time: bool = False,
                   citation: Optional[str] = None,
                   birth_time_fr: Optional[str] = None,
                   birth_place: Optional[str] = None) -> None:
    """Insère une page ex-libris pleine après la dédicace, avant la TOC.

    `birth_time_fr` (ex. "14h30") et `birth_place` (ex. "Paris") sont ajoutés
    sur la ligne « Composé sous le ciel du … » pour enrichir le caractère
    pièce-unique (spec Feb 2026, §4).
    """
    register_fonts()

    if not edition_date_fr:
        _MOIS_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                    'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        _now = datetime.now()
        edition_date_fr = f'{_now.day} {_MOIS_FR[_now.month - 1]} {_now.year}'

    if not citation:
        citation = (
            'Ce livre est un miroir : il ne décide pas, il éclaire. '
            'Que ta lecture y trouve, à chaque retour, une phrase nouvelle.'
        )

    copy_number = generate_copy_number(prenom, birth_date)

    story.append(_ExLibrisFlowable(
        prenom=prenom,
        sun_sign=sun_sign,
        moon_sign=moon_sign,
        asc_sign=asc_sign,
        edition_date_fr=edition_date_fr,
        copy_number=copy_number,
        citation=citation,
        no_birth_time=no_birth_time,
        birth_time_fr=birth_time_fr,
        birth_place=birth_place,
    ))
    story.append(PageBreak())


__all__ = ['ex_libris_page', 'generate_copy_number']
