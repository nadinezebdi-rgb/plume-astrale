"""
Générateur PDF Tarologie Symbolique
PDF complet avec tirage 7 cartes + lecture symbolique
"""
import io
import random
from typing import Dict
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

GOLD = HexColor('#C5A059')
DARK_PURPLE = HexColor('#0F0518')
LIGHT_PURPLE = HexColor('#1A0B2E')
CREAM = HexColor('#F3E5AB')
LIGHT_TEXT = HexColor('#E0D9F6')
MEDIUM_PURPLE = HexColor('#2D1B4E')


class MediumnitePDFGenerator:
    def __init__(self):
        self.width, self.height = A4
        self.margin = 2 * cm
        self.page_num = 0

    def _draw_bg(self, c, seed=0):
        c.setFillColor(DARK_PURPLE)
        c.rect(0, 0, self.width, self.height, fill=1)
        c.setFillColor(LIGHT_PURPLE)
        c.setFillAlpha(0.3)
        for i in range(8):
            c.rect(0, self.height - (i+1)*cm, self.width, cm, fill=1)
        c.setFillAlpha(1.0)
        random.seed(self.page_num * 50 + seed)
        c.setFillColor(HexColor('#FFFFFF'))
        for _ in range(40):
            x, y = random.uniform(0, self.width), random.uniform(0, self.height)
            c.setFillAlpha(random.uniform(0.1, 0.4))
            c.circle(x, y, random.uniform(0.3, 1.0), fill=1)
        c.setFillAlpha(1.0)

    def _new_page(self, c):
        if self.page_num > 0:
            c.showPage()
        self.page_num += 1
        self._draw_bg(c, self.page_num)
        # Footer
        c.setFillColor(GOLD)
        c.setFillAlpha(0.4)
        c.setFont("Helvetica", 8)
        c.drawCentredString(self.width / 2, 1.2 * cm, f"— {self.page_num} —")
        c.setFillAlpha(1.0)

    def _wrap_text(self, text, font_name, font_size, max_width):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        words = text.split()
        lines, current = [], ""
        for word in words:
            test = f"{current} {word}".strip()
            if stringWidth(test, font_name, font_size) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _draw_text(self, c, text, y, font="Helvetica", size=11, color=LIGHT_TEXT, leading=16):
        max_w = self.width - 2 * self.margin
        lines = self._wrap_text(text, font, size, max_w)
        for line in lines:
            if y < 3 * cm:
                self._new_page(c)
                y = self.height - 3 * cm
            c.setFillColor(color)
            c.setFont(font, size)
            c.drawString(self.margin, y, line)
            y -= leading
        return y

    def generate(self, tirage_data: dict) -> bytes:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        self.page_num = 0

        prenom = tirage_data.get("prenom", "Voyageur")

        # === PAGE TITRE ===
        self._new_page(c)
        y = self.height - 6 * cm

        # Decorative line
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.6)
        c.setLineWidth(0.5)
        c.line(self.width * 0.2, y + 2 * cm, self.width * 0.8, y + 2 * cm)
        c.setStrokeAlpha(1.0)

        c.setFillColor(GOLD)
        c.setFont("Helvetica", 12)
        c.drawCentredString(self.width / 2, y + 1 * cm, "LECTURE SACREE")

        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(self.width / 2, y, "Tarologie & Lecture Symbolique")

        c.setFillColor(GOLD)
        c.setFont("Helvetica", 14)
        c.drawCentredString(self.width / 2, y - 1.5 * cm, f"Pour {prenom}")

        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.6)
        c.line(self.width * 0.2, y - 2.5 * cm, self.width * 0.8, y - 2.5 * cm)
        c.setStrokeAlpha(1.0)

        c.setFillColor(LIGHT_TEXT)
        c.setFillAlpha(0.6)
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(self.width / 2, y - 4 * cm, "Un voyage au coeur de votre ame")
        c.drawCentredString(self.width / 2, y - 5 * cm, "a travers les Arcanes et la lecture symbolique")
        c.setFillAlpha(1.0)

        c.setFillColor(GOLD)
        c.setFont("Helvetica", 10)
        c.drawCentredString(self.width / 2, 4 * cm, f"Date du tirage : {tirage_data.get('date', '')[:10]}")

        # === TIRAGE EN CROIX ===
        tirage = tirage_data.get("tirage", [])
        is_croix = tirage_data.get("type") == "croix"
        
        self._new_page(c)
        y = self.height - 3 * cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 20)
        title = "Le Tirage en Croix" if is_croix else "Le Tirage des 7 Arcanes"
        c.drawCentredString(self.width / 2, y, title)
        y -= 0.8 * cm
        c.setFillColor(LIGHT_TEXT)
        c.setFillAlpha(0.6)
        c.setFont("Helvetica-Oblique", 10)
        subtitle = "Cinq arcanes pour eclairer votre situation" if is_croix else "Sept cles pour deverrouiller les mysteres de votre destinee"
        c.drawCentredString(self.width / 2, y, subtitle)
        c.setFillAlpha(1.0)
        y -= 1.5 * cm

        for i, item in enumerate(tirage):
            carte = item.get("carte", {})
            position = item.get("position_nom", item.get("position", ""))
            message = item.get("interpretation", item.get("message", ""))
            description = carte.get("description_arcane", "")
            mots_cles = carte.get("mots_cles", carte.get("energie", ""))

            # Calculate box height based on content
            msg_lines = self._wrap_text(message, "Helvetica", 10, self.width - 2 * self.margin - 1 * cm)
            desc_lines = self._wrap_text(description, "Helvetica-Oblique", 9, self.width - 2 * self.margin - 1 * cm) if description else []
            content_h = max(4.5 * cm, 2.5 * cm + len(msg_lines) * 0.35 * cm + len(desc_lines) * 0.32 * cm)

            if y - content_h < 3 * cm:
                self._new_page(c)
                y = self.height - 3 * cm

            box_w = self.width - 2 * self.margin

            # Card box background
            c.setFillColor(MEDIUM_PURPLE)
            c.setFillAlpha(0.5)
            c.roundRect(self.margin, y - content_h, box_w, content_h, 8, fill=1)
            c.setFillAlpha(1.0)

            c.setStrokeColor(GOLD)
            c.setStrokeAlpha(0.4)
            c.roundRect(self.margin, y - content_h, box_w, content_h, 8)
            c.setStrokeAlpha(1.0)

            # Position label
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(self.margin + 0.5 * cm, y - 0.7 * cm, f"Position {i+1} : {position}")

            # Card name
            c.setFillColor(CREAM)
            c.setFont("Helvetica-Bold", 13)
            nom = carte.get("nom", "Inconnue")
            c.drawString(self.margin + 0.5 * cm, y - 1.4 * cm, f"Arcane : {nom}")

            # Mots-cles
            c.setFillColor(GOLD)
            c.setFillAlpha(0.7)
            c.setFont("Helvetica-Oblique", 9)
            c.drawRightString(self.width - self.margin - 0.5 * cm, y - 0.7 * cm, mots_cles)
            c.setFillAlpha(1.0)

            # Description of the arcane (if available)
            msg_y = y - 2.1 * cm
            if desc_lines:
                c.setFillColor(GOLD)
                c.setFillAlpha(0.7)
                for line in desc_lines:
                    c.setFont("Helvetica-Oblique", 9)
                    c.drawString(self.margin + 0.5 * cm, msg_y, line)
                    msg_y -= 12
                c.setFillAlpha(1.0)
                msg_y -= 4

            # Interpretation message
            for line in msg_lines:
                c.setFillColor(LIGHT_TEXT)
                c.setFont("Helvetica", 10)
                c.drawString(self.margin + 0.5 * cm, msg_y, line)
                msg_y -= 13

            y -= content_h + 0.6 * cm

        # === LECTURE SYMBOLIQUE ===
        self._new_page(c)
        y = self.height - 3 * cm

        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.width / 2, y, "Lecture Symbolique")
        y -= 0.8 * cm
        c.setFillColor(LIGHT_TEXT)
        c.setFillAlpha(0.6)
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(self.width / 2, y, "Ce que revele votre tirage")
        c.setFillAlpha(1.0)
        y -= 2 * cm

        lecture = tirage_data.get("lecture_mediumnique", {})
        sections = [
            ("Empreinte du Passe", lecture.get("passe", "")),
            ("Energies du Present", lecture.get("present", "")),
            ("Visions du Futur", lecture.get("futur", "")),
            ("Un Conseil pour Vous", lecture.get("conseil_ame", "")),
        ]

        for titre, texte in sections:
            if y < 5 * cm:
                self._new_page(c)
                y = self.height - 3 * cm

            # Section separator
            c.setStrokeColor(GOLD)
            c.setStrokeAlpha(0.3)
            c.line(self.margin, y, self.width - self.margin, y)
            c.setStrokeAlpha(1.0)
            y -= 0.8 * cm

            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(self.margin, y, titre)
            y -= 1 * cm

            y = self._draw_text(c, texte, y)
            y -= 1 * cm

        # === PAGE FINALE ===
        self._new_page(c)
        y = self.height / 2 + 2 * cm

        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.4)
        c.line(self.width * 0.3, y + 1 * cm, self.width * 0.7, y + 1 * cm)
        c.setStrokeAlpha(1.0)

        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(self.width / 2, y, "Message Final")
        y -= 1.5 * cm

        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica-Oblique", 12)
        msg_final = (
            f"Cher(e) {prenom}, cette lecture est un cadeau de l'univers. "
            "Les cartes et les messages de ce tirage vous eclairent mais ne vous enferment pas. "
            "Vous restez le maitre de votre destinee. Utilisez ces revelations comme des phares "
            "pour eclairer votre chemin, et rappelez-vous : votre lumiere interieure est votre "
            "plus grande force."
        )
        y = self._draw_text(c, msg_final, y, "Helvetica-Oblique", 12, LIGHT_TEXT, 18)

        y -= 1.5 * cm
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.4)
        c.line(self.width * 0.3, y, self.width * 0.7, y)
        c.setStrokeAlpha(1.0)

        y -= 1 * cm
        c.setFillColor(GOLD)
        c.setFillAlpha(0.5)
        c.setFont("Helvetica", 9)
        c.drawCentredString(self.width / 2, y, "Plume Astrale - Tarologie & Lecture Symbolique")
        c.setFillAlpha(1.0)

        c.save()
        return buffer.getvalue()


def generate_mediumnite_pdf(tirage_data: dict) -> bytes:
    gen = MediumnitePDFGenerator()
    return gen.generate(tirage_data)


def _build_ai_enrichment_pdf(prenom: str, birth_date_iso: str,
                              ai_sections: Dict[str, str],
                              report_type: str = 'mediumnite') -> bytes:
    """Construit un PDF SimpleDocTemplate contenant uniquement les sections IA.
    Utilisé pour être concaténé à un PDF canvas existant via pypdf.
    """
    from io import BytesIO as _BIO
    from reportlab.platypus import (SimpleDocTemplate as _SDT, Paragraph as _Par,
                                     Spacer as _Sp, PageBreak as _PB)
    from reportlab.lib.pagesizes import A4 as _A4
    from reportlab.lib.styles import getSampleStyleSheet as _gss, ParagraphStyle as _PS
    from reportlab.lib.enums import TA_JUSTIFY as _TAJ, TA_CENTER as _TAC
    from reportlab.lib.units import cm as _cm

    buf = _BIO()
    doc = _SDT(buf, pagesize=_A4,
               leftMargin=2.2 * _cm, rightMargin=2.2 * _cm,
               topMargin=2 * _cm, bottomMargin=2 * _cm,
               title='Enrichissement personnel — Plume Astrale',
               author='Solena')
    base = _gss()
    styles = {
        'h2': _PS('h2', parent=base['Heading2'], fontName='Helvetica-Bold',
                  fontSize=15, textColor='#c9a24b', spaceAfter=10, alignment=_TAC),
        'body': _PS('body', parent=base['BodyText'], fontName='Helvetica',
                    fontSize=11, textColor='#3a3450', leading=17, alignment=_TAJ,
                    spaceAfter=8),
    }
    from services.kabbale_pdf import _append_ai_sections as _append
    story: list = []
    story.append(_Par(f'✦ Enrichissement personnel de {prenom} ✦', styles['h2']))
    story.append(_Sp(0, 0.5 * _cm))
    _append(story, styles, ai_sections, report_type=report_type)
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


async def generate_mediumnite_pdf_ai(tirage_data: dict, prenom: str,
                                      birth_date_iso: str) -> bytes:
    """Génère le tirage Symbolique + concatène des pages narratives IA en tête."""
    base_pdf = generate_mediumnite_pdf(tirage_data)
    try:
        from services.report_ai_enrichment import enrich_report
        # enrich_report gère lui-même le toggle admin :
        # - IA ON  → appel LLM
        # - IA OFF → fallback statique riche (pages étoffées pré-rédigées)
        ai_sections = await enrich_report(
            report_type='mediumnite',
            prenom=prenom or 'Voyageur',
            birth_date_iso=birth_date_iso or '',
            context={'tirage': tirage_data},
        )
    except Exception:
        return base_pdf
    if not ai_sections:
        return base_pdf
    try:
        enrichment_pdf = _build_ai_enrichment_pdf(prenom, birth_date_iso, ai_sections)
        from io import BytesIO as _BIO2
        from pypdf import PdfWriter, PdfReader
        writer = PdfWriter()
        for src in (base_pdf, enrichment_pdf):
            reader = PdfReader(_BIO2(src))
            for p in reader.pages:
                writer.add_page(p)
        out = _BIO2()
        writer.write(out)
        return out.getvalue()
    except Exception:
        return base_pdf
