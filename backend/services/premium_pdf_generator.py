"""
Generateur PDF Premium — Experience guidee en 5 etapes
Design violet/dore coherent avec l'identite Plume Astrale
"""
import io
import random
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
import logging

logger = logging.getLogger(__name__)

GOLD = HexColor('#C5A059')
DARK_PURPLE = HexColor('#0F0518')
LIGHT_PURPLE = HexColor('#1A0B2E')
CREAM = HexColor('#F0E6D3')
BODY_TEXT = HexColor('#B8B0C8')
MUTED = HexColor('#8A7FA0')
SOFT_GOLD = HexColor('#D4AF37')

STEP_ICONS = {
    "step_1_fondement": "I",
    "step_2_chemin_ame": "II",
    "step_3_cycle": "III",
    "step_4_schemas": "IV",
    "step_5_projection": "V",
}


class PremiumPDFGenerator:
    def __init__(self):
        self.width, self.height = A4
        self.margin = 2.5 * cm
        self.page_num = 0

    def _draw_bg(self, c):
        c.setFillColor(DARK_PURPLE)
        c.rect(0, 0, self.width, self.height, fill=1)
        c.setFillColor(LIGHT_PURPLE)
        c.setFillAlpha(0.25)
        for i in range(8):
            c.rect(0, self.height - (i + 1) * cm, self.width, cm, fill=1)
        c.setFillAlpha(1.0)
        random.seed(self.page_num * 77)
        c.setFillColor(HexColor('#FFFFFF'))
        for _ in range(30):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            size = random.uniform(0.2, 0.8)
            c.setFillAlpha(random.uniform(0.08, 0.3))
            c.circle(x, y, size, fill=1)
        c.setFillAlpha(1.0)

    def _draw_border(self, c):
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.2)
        c.setLineWidth(0.5)
        c.rect(1.5 * cm, 1.5 * cm, self.width - 3 * cm, self.height - 3 * cm)
        c.setStrokeAlpha(1.0)

    def _draw_page_num(self, c):
        c.setFillColor(GOLD)
        c.setFillAlpha(0.4)
        c.setFont("Helvetica", 8)
        c.drawCentredString(self.width / 2, 1.2 * cm, f"- {self.page_num} -")
        c.setFillAlpha(1.0)

    def _new_page(self, c):
        c.showPage()
        self.page_num += 1
        self._draw_bg(c)
        self._draw_border(c)
        self._draw_page_num(c)

    def _draw_separator(self, c, y):
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.35)
        c.setLineWidth(0.5)
        cx = self.width / 2
        c.line(cx - 3 * cm, y, cx + 3 * cm, y)
        c.setStrokeAlpha(1.0)
        return y - 0.5 * cm

    def _wrap_text(self, c, text, x, y, max_width, font="Helvetica", size=10, color=BODY_TEXT, leading=14):
        c.setFillColor(color)
        c.setFont(font, size)
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = f"{current_line} {word}".strip()
            if c.stringWidth(test, font, size) <= max_width:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        for line in lines:
            if y < 3 * cm:
                self._new_page(c)
                y = self.height - 3.5 * cm
                c.setFillColor(color)
                c.setFont(font, size)
            c.drawString(x, y, line)
            y -= leading
        return y

    def _draw_cover(self, c, prenom, signe, date_naissance):
        self._draw_bg(c)
        self._draw_border(c)
        cx = self.width / 2
        # Decorative line top
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.3)
        c.setLineWidth(0.5)
        c.line(cx - 4 * cm, self.height - 8 * cm, cx + 4 * cm, self.height - 8 * cm)
        c.setStrokeAlpha(1.0)
        # Title
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 11)
        c.drawCentredString(cx, self.height - 9 * cm, "PLUME ASTRALE")
        c.setFont("Helvetica", 8)
        c.setFillColor(MUTED)
        c.drawCentredString(cx, self.height - 9.6 * cm, "EXPERIENCE PREMIUM")
        # Main title
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 26)
        c.drawCentredString(cx, self.height - 12 * cm, "Votre Cartographie")
        c.setFont("Helvetica-Bold", 26)
        c.drawCentredString(cx, self.height - 13 * cm, "Celeste Complete")
        # Separator
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.4)
        c.line(cx - 3 * cm, self.height - 14 * cm, cx + 3 * cm, self.height - 14 * cm)
        c.setStrokeAlpha(1.0)
        # User info
        c.setFillColor(CREAM)
        c.setFont("Helvetica", 14)
        c.drawCentredString(cx, self.height - 15.5 * cm, prenom)
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 10)
        c.drawCentredString(cx, self.height - 16.3 * cm, f"{signe}  |  Ne(e) le {date_naissance}")
        # Bottom
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawCentredString(cx, 3 * cm, f"Genere le {datetime.now().strftime('%d/%m/%Y')}")
        c.drawCentredString(cx, 2.4 * cm, "Document personnel et confidentiel")

    def _draw_chapter(self, c, step_key, step_data):
        self._new_page(c)
        cx = self.width / 2
        y = self.height - 4 * cm
        # Chapter number
        roman = STEP_ICONS.get(step_key, "")
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 28)
        c.drawCentredString(cx, y, roman)
        y -= 1.2 * cm
        # Title
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(cx, y, step_data.get("title", ""))
        y -= 0.7 * cm
        # Subtitle
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(cx, y, step_data.get("subtitle", ""))
        y -= 1 * cm
        y = self._draw_separator(c, y)
        y -= 0.5 * cm
        # Key data points
        left = self.margin + 0.5 * cm
        max_w = self.width - 2 * self.margin - 1 * cm
        data_fields = [
            ("signe", "Signe solaire"),
            ("element", "Element"),
            ("modalite", "Modalite"),
            ("chemin_de_vie", "Chemin de vie"),
            ("titre_chemin", "Archetype"),
            ("nombre_expression", "Nombre d'expression"),
            ("nombre_ame", "Nombre d'ame"),
            ("annee_personnelle", "Annee personnelle"),
            ("periode", "Periode"),
        ]
        for field, label in data_fields:
            val = step_data.get(field)
            if val is not None:
                c.setFillColor(MUTED)
                c.setFont("Helvetica", 9)
                c.drawString(left, y, f"{label}:")
                c.setFillColor(CREAM)
                c.setFont("Helvetica-Bold", 9)
                c.drawString(left + 5 * cm, y, str(val))
                y -= 0.5 * cm
        # Forces / Tensions
        forces = step_data.get("forces")
        tensions = step_data.get("tensions")
        if forces:
            y -= 0.3 * cm
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left, y, "Forces")
            y -= 0.45 * cm
            for f in forces:
                c.setFillColor(CREAM)
                c.setFont("Helvetica", 9)
                c.drawString(left + 0.5 * cm, y, f"- {f}")
                y -= 0.4 * cm
        if tensions:
            y -= 0.2 * cm
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left, y, "Tensions")
            y -= 0.45 * cm
            for t in tensions:
                c.setFillColor(BODY_TEXT)
                c.setFont("Helvetica", 9)
                c.drawString(left + 0.5 * cm, y, f"- {t}")
                y -= 0.4 * cm
        # Interpretation
        interpretation = step_data.get("interpretation", "")
        if interpretation:
            y -= 0.5 * cm
            y = self._draw_separator(c, y)
            y -= 0.4 * cm
            paragraphs = interpretation.split('\n')
            for para in paragraphs:
                para = para.strip()
                if not para:
                    y -= 0.3 * cm
                    continue
                y = self._wrap_text(c, para, left, y, max_w, "Helvetica", 9.5, BODY_TEXT, 13)
                y -= 0.3 * cm
        # Reflection
        reflection = step_data.get("reflection", "")
        if reflection:
            y -= 0.4 * cm
            if y < 5 * cm:
                self._new_page(c)
                y = self.height - 4 * cm
            y = self._draw_separator(c, y)
            y -= 0.3 * cm
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Oblique", 9)
            c.drawCentredString(cx, y, f'"{reflection}"')

    def _draw_closing(self, c, prenom):
        self._new_page(c)
        cx = self.width / 2
        y = self.height - 6 * cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 10)
        c.drawCentredString(cx, y, "~")
        y -= 1.5 * cm
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(cx, y, "Merci pour votre confiance")
        y -= 1 * cm
        c.setFillColor(BODY_TEXT)
        c.setFont("Helvetica", 10)
        lines = [
            f"Cher(e) {prenom},",
            "",
            "Ce document est le fruit d'une lecture croisee de votre theme natal,",
            "de votre numerologie et des cycles en cours.",
            "",
            "Il ne predit pas votre avenir. Il eclaire des dynamiques.",
            "Il vous offre des reperes pour naviguer avec plus de conscience.",
            "",
            "Revenez a ces pages aussi souvent que necessaire.",
            "Les symboles se revelent au fil du temps.",
            "",
            "Avec bienveillance,",
            "Plume Astrale"
        ]
        for line in lines:
            if not line:
                y -= 0.4 * cm
                continue
            c.drawCentredString(cx, y, line)
            y -= 0.5 * cm

    def generate(self, premium_data: dict) -> bytes:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        self.page_num = 0
        prenom = premium_data.get("prenom", "Voyageur")
        signe = premium_data.get("signe", "")
        date_naissance = premium_data.get("date_naissance", "")
        steps = premium_data.get("steps", {})
        # Cover
        self._draw_cover(c, prenom, signe, date_naissance)
        # Chapters
        step_order = [
            "step_1_fondement",
            "step_2_chemin_ame",
            "step_3_cycle",
            "step_4_schemas",
            "step_5_projection"
        ]
        for step_key in step_order:
            step_data = steps.get(step_key)
            if step_data:
                self._draw_chapter(c, step_key, step_data)
        # Closing
        self._draw_closing(c, prenom)
        c.save()
        return buffer.getvalue()


def generate_premium_pdf(premium_data: dict) -> bytes:
    gen = PremiumPDFGenerator()
    return gen.generate(premium_data)
