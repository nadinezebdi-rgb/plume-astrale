"""
Generateur PDF Manuscrit Complet V4
Version massivement enrichie avec contenu pedagogique, carte du ciel, aspects,
equilibre elementaire, retrogrades, Chiron, Lilith, Noeud Nord
"""
import io
import os
import math
import random
import httpx
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import ImageReader
import logging
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False

from services.astro_content import (
    SIGNES_DETAILS, PLANETES_DETAILS, MAISONS_DETAILS,
    CHEMINS_VIE, PREVISIONS_ANNEE_PERSONNELLE, ARCANES_MAJEURS
)
from services.astro_content_extended import (
    MERCURE_EN_SIGNE, VENUS_EN_SIGNE, MARS_EN_SIGNE,
    JUPITER_EN_SIGNE, SATURNE_EN_SIGNE,
    ASPECTS_TYPES, ASPECTS_PLANETES, get_aspect_interpretation,
    RETROGRADE_DESCRIPTIONS, ELEMENTS_DOMINANTS, MODALITES_DESCRIPTIONS,
    CHIRON_EN_SIGNE, LILITH_EN_SIGNE, NOEUD_NORD_EN_SIGNE,
    SIGNE_ELEMENT, SIGNE_MODALITE
)

logger = logging.getLogger(__name__)

GOLD = HexColor('#C5A059')
DARK_PURPLE = HexColor('#0F0518')
LIGHT_PURPLE = HexColor('#1A0B2E')
CREAM = HexColor('#F3E5AB')
LIGHT_TEXT = HexColor('#E0D9F6')
MEDIUM_PURPLE = HexColor('#2D1B4E')
SOFT_GOLD = HexColor('#D4AF37')
FIRE_COLOR = HexColor('#E84040')
EARTH_COLOR = HexColor('#6BAF6B')
AIR_COLOR = HexColor('#6BB5E8')
WATER_COLOR = HexColor('#4A78D0')

ASSETS_DIR = Path(__file__).parent.parent / "assets"
ZODIAC_IMG_DIR = ASSETS_DIR / "zodiac"
ILLUST_DIR = ASSETS_DIR / "images" / "illustrations"

ZODIAC_IMAGES = {
    "Aries": "aries.jpg", "Taurus": "taurus.jpg", "Gemini": "gemini.jpg",
    "Cancer": "cancer.jpg", "Leo": "leo.jpg", "Virgo": "virgo.jpg",
    "Libra": "libra.jpg", "Scorpio": "scorpio.jpg", "Sagittarius": "sagittarius.jpg",
    "Capricorn": "capricorn.jpg", "Aquarius": "aquarius.jpg", "Pisces": "pisces.jpg",
}

ILLUSTRATION_FILES = [
    "eso_priestess.jpg",
    "eso_birds.jpg",
    "eso_koi.jpg",
    "eso_landscape.jpg",
    "eso_lion_zodiac.jpg",
    "eso_crystal_bird.jpg",
    "eso_crystal_priestess.jpg",
    "eso_balance_desert.jpg",
    "eso_cosmic_balance.jpg",
]

INTRO_WHAT_IS = """Votre theme astral, aussi appele carte du ciel ou theme natal, est une photographie du ciel au moment exact de votre naissance. Il montre la position de chaque planete dans les douze signes du zodiaque et dans les douze maisons astrologiques. C'est une carte unique, aussi personnelle que vos empreintes digitales.

Imaginez le ciel comme un grand cadran divise en douze secteurs (les maisons) et parcouru par dix astres principaux (le Soleil, la Lune et huit planetes). Au moment ou vous avez pris votre premier souffle, chaque astre occupait un signe et une maison precis. Cette configuration celeste revele vos talents naturels, vos defis, votre facon d'aimer, de travailler, de communiquer et d'evoluer.

Ce document est concu comme un guide de decouverte de soi. Il ne predit pas un destin fige : les etoiles inclinent, mais ne determinent pas. Votre libre arbitre reste toujours le capitaine de votre navire. En revanche, connaitre votre theme astral vous offre une boussole precieuse pour naviguer avec plus de conscience et d'alignement."""

INTRO_HOW_TO_USE = """Ce manuscrit est divise en plusieurs chapitres, chacun eclairant une facette de votre personnalite :

Le Soleil represente votre essence fondamentale, ce que vous etes au plus profond. C'est votre identite, votre vitalite, votre raison d'etre.

La Lune revele votre monde emotionnel, vos besoins de securite, votre facon de reagir instinctivement. Elle est le miroir de votre ame.

L'Ascendant est la vitrine de votre personnalite, la premiere impression que vous donnez aux autres. C'est le masque social a travers lequel votre essence solaire s'exprime.

Les Planetes (Mercure, Venus, Mars, Jupiter, Saturne) ajoutent des nuances essentielles : votre facon de penser, d'aimer, d'agir, de vous expandre et de vous structurer.

Les Maisons representent les domaines concrets de votre vie : la famille, le travail, les relations, la spiritualite, etc.

Les Aspects sont les angles entre les planetes, revelant comment vos differentes facettes interagissent entre elles - en harmonie ou en tension creatrice.

Lisez chaque section avec curiosite et bienveillance. Certains passages vous parleront immediatement, d'autres prendront sens avec le temps. Revenez-y regulierement : un theme astral se revele tout au long d'une vie."""

SIGN_ORDER = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

PLANET_EN_SIGNE_MAP = {
    "Mercury": MERCURE_EN_SIGNE,
    "Venus": VENUS_EN_SIGNE,
    "Mars": MARS_EN_SIGNE,
    "Jupiter": JUPITER_EN_SIGNE,
    "Saturn": SATURNE_EN_SIGNE,
}


class ManuscritCompletGenerator:
    def __init__(self):
        self.width, self.height = A4
        self.margin = 2.2 * cm
        self.page_num = 0
        self._image_cache = {}

    def _get_french_sign(self, sign):
        return SIGNES_DETAILS.get(sign, {}).get('nom_fr', sign)

    def _get_zodiac_image(self, sign):
        if sign in self._image_cache:
            return self._image_cache[sign]
        filename = ZODIAC_IMAGES.get(sign)
        if filename:
            path = ZODIAC_IMG_DIR / filename
            if path.exists():
                self._image_cache[sign] = str(path)
                return str(path)
        self._image_cache[sign] = None
        return None

    def _get_illustration(self, index):
        if index < len(ILLUSTRATION_FILES):
            path = ILLUST_DIR / ILLUSTRATION_FILES[index]
            if path.exists():
                return str(path)
        return None

    def _draw_bg(self, c, variant=0):
        c.setFillColor(DARK_PURPLE)
        c.rect(0, 0, self.width, self.height, fill=1)
        c.setFillColor(LIGHT_PURPLE)
        c.setFillAlpha(0.3)
        for i in range(10):
            c.rect(0, self.height - (i+1)*cm, self.width, cm, fill=1)
        c.setFillAlpha(1.0)
        random.seed(self.page_num * 100 + variant)
        c.setFillColor(HexColor('#FFFFFF'))
        for _ in range(40):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            size = random.uniform(0.2, 1.0)
            c.setFillAlpha(random.uniform(0.1, 0.4))
            c.circle(x, y, size, fill=1)
        c.setFillAlpha(1.0)

    def _draw_border(self, c):
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.25)
        c.setLineWidth(0.5)
        c.rect(1.5*cm, 1.5*cm, self.width - 3*cm, self.height - 3*cm)
        c.setStrokeAlpha(1.0)

    def _draw_page_num(self, c):
        c.setFillColor(GOLD)
        c.setFillAlpha(0.5)
        c.setFont("Helvetica", 9)
        c.drawCentredString(self.width / 2, 1.2*cm, f"- {self.page_num} -")
        c.setFillAlpha(1.0)

    def _new_page(self, c):
        c.showPage()
        self.page_num += 1
        self._draw_bg(c)
        self._draw_border(c)
        self._draw_page_num(c)

    def _draw_separator(self, c, y):
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.4)
        c.setLineWidth(0.5)
        c.line(4*cm, y, self.width - 4*cm, y)
        c.setStrokeAlpha(1.0)
        return y - 0.6*cm

    def _chapter_header(self, c, title, subtitle="", y=None):
        if y is None:
            y = self.height - 4*cm
        self._draw_separator(c, y + 0.5*cm)
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.width / 2, y, title)
        if subtitle:
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Oblique", 11)
            c.drawCentredString(self.width / 2, y - 0.7*cm, subtitle)
            y -= 0.7*cm
        self._draw_separator(c, y - 0.4*cm)
        return y - 1.5*cm

    def _sub_header(self, c, text, y, size=14):
        if y < 3.5*cm:
            self._new_page(c)
            y = self.height - 3.5*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", size)
        c.drawCentredString(self.width / 2, y, text)
        return y - 0.8*cm

    def _wrap(self, c, text, font="Helvetica", size=11, max_w=None):
        if max_w is None:
            max_w = self.width - 2 * self.margin
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = cur + " " + w if cur else w
            if c.stringWidth(test, font, size) < max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def _draw_centered_block(self, c, text, y, font_size=11, color=LIGHT_TEXT, leading=1.45):
        c.setFillColor(color)
        c.setFont("Helvetica", font_size)
        paragraphs = text.strip().split('\n')
        lh = font_size * leading / 28.35
        for para in paragraphs:
            para = para.strip()
            if not para:
                y -= lh * cm * 0.5
                continue
            lines = self._wrap(c, para, "Helvetica", font_size)
            for line in lines:
                if y < 2.5*cm:
                    self._new_page(c)
                    y = self.height - 3.5*cm
                    c.setFillColor(color)
                    c.setFont("Helvetica", font_size)
                c.drawCentredString(self.width / 2, y, line)
                y -= lh * cm
            y -= lh * cm * 0.3
        return y

    def _draw_image_safe(self, c, path, y, w=7*cm, h=7*cm):
        x = (self.width - w) / 2
        try:
            c.saveState()
            c.setStrokeColor(GOLD)
            c.setStrokeAlpha(0.5)
            c.setLineWidth(1)
            c.roundRect(x - 2, y - h - 2, w + 4, h + 4, 8)
            c.setStrokeAlpha(1.0)
            c.drawImage(path, x, y - h, width=w, height=h, preserveAspectRatio=True, mask='auto')
            c.restoreState()
            return y - h - 0.8*cm
        except Exception as e:
            logger.warning(f"Image error: {e}")
            c.restoreState()
            return y - 0.5*cm

    def _draw_info_box(self, c, text, y, color=GOLD):
        """Draw text in a styled box"""
        if y < 3*cm:
            self._new_page(c)
            y = self.height - 3.5*cm
        c.setFillColor(MEDIUM_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(self.margin, y - 1*cm, self.width - 2*self.margin, 1*cm, 5, fill=1)
        c.setFillAlpha(1.0)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.width/2, y - 0.7*cm, text)
        return y - 1.8*cm

    def _draw_natal_chart(self, c, y, planets_data, zodiac_sign):
        """Draw a natal chart wheel with planet positions"""
        cx = self.width / 2
        cy = y - 6.5*cm
        r_outer = 5.5*cm
        r_inner = 3.8*cm
        r_planet = 3*cm

        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.6)
        c.setLineWidth(1.5)
        c.circle(cx, cy, r_outer)
        c.setLineWidth(0.8)
        c.circle(cx, cy, r_inner)
        c.setStrokeAlpha(1.0)

        for i in range(12):
            angle = math.radians(i * 30)
            x1 = cx + r_inner * math.cos(angle)
            y1 = cy + r_inner * math.sin(angle)
            x2 = cx + r_outer * math.cos(angle)
            y2 = cy + r_outer * math.sin(angle)
            c.setStrokeAlpha(0.3)
            c.line(x1, y1, x2, y2)
        c.setStrokeAlpha(1.0)

        for i, sign in enumerate(SIGN_ORDER):
            angle = math.radians(i * 30 + 15)
            sx = cx + (r_outer + r_inner) / 2 * math.cos(angle)
            sy = cy + (r_outer + r_inner) / 2 * math.sin(angle)
            info = SIGNES_DETAILS.get(sign, {})
            sym = info.get('symbole', '?')
            c.setFillColor(GOLD if sign == zodiac_sign else LIGHT_TEXT)
            c.setFillAlpha(0.9 if sign == zodiac_sign else 0.5)
            c.setFont("Helvetica", 10)
            c.drawCentredString(sx, sy - 3, sym)
        c.setFillAlpha(1.0)

        if planets_data:
            planet_syms = {
                'Sun': 'Sol', 'Moon': 'Lun', 'Mercury': 'Mer', 'Venus': 'Ven',
                'Mars': 'Mar', 'Jupiter': 'Jup', 'Saturn': 'Sat',
                'Uranus': 'Ura', 'Neptune': 'Nep', 'Pluto': 'Plu'
            }
            placed = 0
            for p in planets_data:
                name = p.get('name', '')
                if name in planet_syms:
                    sign = p.get('sign', '')
                    idx = SIGN_ORDER.index(sign) if sign in SIGN_ORDER else 0
                    deg = p.get('normDegree', p.get('norm_degree', 15))
                    total_angle = idx * 30 + deg
                    angle = math.radians(total_angle)
                    offset = 0.3*cm * (placed % 3)
                    px = cx + (r_planet - offset) * math.cos(angle)
                    py = cy + (r_planet - offset) * math.sin(angle)
                    is_retro = str(p.get('isRetro', p.get('is_retro', 'false'))).lower() == 'true'
                    c.setFillColor(CREAM if not is_retro else HexColor('#FF9999'))
                    c.setFont("Helvetica-Bold", 7)
                    label = planet_syms[name] + ("R" if is_retro else "")
                    c.drawCentredString(px, py, label)
                    placed += 1

        c.setFillColor(GOLD)
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(cx, cy - 0.3*cm, "Votre Carte du Ciel")

        return cy - r_outer - 1*cm

    # ============= PAGES =============

    def _page_cover(self, c, user_data, zodiac_sign):
        self.page_num = 0
        self._draw_bg(c, 0)
        prenom = user_data.get('prenom', 'Voyageur Celeste')
        signe_info = SIGNES_DETAILS.get(zodiac_sign, {})
        signe_fr = signe_info.get('nom_fr', zodiac_sign)
        symbole = signe_info.get('symbole', '')

        illust = self._get_illustration(3)
        if illust:
            self._draw_image_safe(c, illust, self.height - 1*cm, w=self.width, h=8*cm)

        y = self.height - 10*cm
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        c.line(3*cm, y, self.width - 3*cm, y)

        c.setFillColor(GOLD)
        c.setFont("Helvetica", 10)
        c.drawCentredString(self.width / 2, y - 1.2*cm, "VOTRE MANUSCRIT CELESTE PERSONNEL")

        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(self.width / 2, y - 3.5*cm, "Le Theme Astral")
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(self.width / 2, y - 5*cm, f"de {prenom}")

        c.setFillColor(GOLD)
        c.setFont("Helvetica-Oblique", 14)
        c.drawCentredString(self.width / 2, y - 7*cm, f"{symbole}  Signe Solaire : {signe_fr}  {symbole}")

        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 10)
        date_n = user_data.get('dateNaissance', '')
        heure = user_data.get('heureNaissance', '')
        ville = user_data.get('ville', '')
        c.drawCentredString(self.width / 2, y - 8*cm, f"Ne(e) le {date_n} a {heure} - {ville}")

        c.setFillColor(CREAM)
        c.setFillAlpha(0.7)
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(self.width / 2, y - 10*cm, "Les etoiles inclinent, mais ne determinent pas.")
        c.setFillAlpha(1.0)

        c.setStrokeColor(GOLD)
        c.line(3*cm, 4*cm, self.width - 3*cm, 4*cm)
        c.setFillColor(GOLD)
        c.setFillAlpha(0.5)
        c.setFont("Helvetica", 9)
        c.drawCentredString(self.width / 2, 2.5*cm, f"Genere le {datetime.now().strftime('%d/%m/%Y')} - Plume Astrale 2026")
        c.setFillAlpha(1.0)

    def _page_sommaire(self, c):
        self._new_page(c)
        y = self._chapter_header(c, "Sommaire", "Votre voyage a travers les etoiles")
        chapters = [
            ("I", "Qu'est-ce qu'un Theme Astral ?", "Introduction et guide de lecture"),
            ("II", "Votre Carte du Ciel", "La photographie celeste de votre naissance"),
            ("III", "Equilibre Elementaire", "Feu, Terre, Air, Eau dans votre theme"),
            ("IV", "Votre Soleil", "L'essence de qui vous etes"),
            ("V", "Votre Lune", "Votre monde emotionnel interieur"),
            ("VI", "Votre Ascendant", "Le masque social et la premiere impression"),
            ("VII", "Mercure - Votre Esprit", "Facon de penser et communiquer"),
            ("VIII", "Venus - Votre Coeur", "Facon d'aimer et de valoriser"),
            ("IX", "Mars - Votre Energie", "Force d'action et d'affirmation"),
            ("X", "Jupiter & Saturne", "Expansion et structure de vie"),
            ("XI", "Planetes Retrogrades", "Les energies interiorisees"),
            ("XII", "Les Aspects Planetaires", "L'alchimie entre vos planetes"),
            ("XIII", "Les Maisons Astrologiques", "Les 12 domaines de votre vie"),
            ("XIV", "Chiron & Noeud Nord", "Guerison et destinee karmique"),
            ("XV", "Votre Chemin de Vie", "Numerologie et mission d'ame"),
            ("XVI", "Previsions 2026", "Votre annee personnelle en detail"),
            ("XVII", "Vision sur 5 Ans", "2026-2030"),
            ("XVIII", "Le Tirage du Tarot", "Messages pour votre chemin"),
            ("XIX", "Conseils Personnalises", "Guidance pour votre evolution"),
        ]
        for num, title, sub in chapters:
            if y < 2.5*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            c.setFillColor(GOLD)
            c.setFont("Helvetica", 10)
            c.drawString(self.margin + 0.2*cm, y, num)
            c.setFillColor(CREAM)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(self.margin + 1.2*cm, y, title)
            c.setFillColor(LIGHT_TEXT)
            c.setFillAlpha(0.6)
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(self.margin + 1.2*cm, y - 0.35*cm, sub)
            c.setFillAlpha(1.0)
            y -= 1.05*cm

    def _page_introduction(self, c):
        self._new_page(c)
        y = self._chapter_header(c, "Qu'est-ce qu'un Theme Astral ?", "Comprendre votre carte celeste")
        y = self._draw_centered_block(c, INTRO_WHAT_IS, y, font_size=10.5, color=LIGHT_TEXT)

        illust = self._get_illustration(0)
        if illust:
            if y < 9*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            y = self._draw_image_safe(c, illust, y, w=8*cm, h=8*cm)

        self._new_page(c)
        y = self._chapter_header(c, "Comment lire ce manuscrit ?", "Un guide pas a pas")
        y = self._draw_centered_block(c, INTRO_HOW_TO_USE, y, font_size=10.5, color=LIGHT_TEXT)

    def _page_natal_chart(self, c, planets_data, zodiac_sign, horoscope_data, chart_svg_url=None):
        self._new_page(c)
        y = self._chapter_header(c, "Votre Carte du Ciel", "La photographie celeste de votre naissance")

        # Try to use the real SVG chart from AstrologyAPI
        used_real_chart = False
        if chart_svg_url and HAS_CAIROSVG:
            try:
                resp = httpx.get(chart_svg_url, timeout=15.0)
                if resp.status_code == 200:
                    png_data = cairosvg.svg2png(bytestring=resp.content, output_width=800, output_height=800)
                    img_reader = ImageReader(io.BytesIO(png_data))
                    chart_w = 11*cm
                    chart_h = 11*cm
                    x = (self.width - chart_w) / 2
                    c.saveState()
                    c.setStrokeColor(GOLD)
                    c.setStrokeAlpha(0.5)
                    c.setLineWidth(1)
                    c.roundRect(x - 3, y - chart_h - 3, chart_w + 6, chart_h + 6, 8)
                    c.setStrokeAlpha(1.0)
                    c.drawImage(img_reader, x, y - chart_h, width=chart_w, height=chart_h, preserveAspectRatio=True, mask='auto')
                    c.restoreState()
                    y = y - chart_h - 0.8*cm
                    c.setFillColor(GOLD)
                    c.setFillAlpha(0.6)
                    c.setFont("Helvetica-Oblique", 8)
                    c.drawCentredString(self.width / 2, y, "Carte du ciel generee par AstrologyAPI")
                    c.setFillAlpha(1.0)
                    y -= 0.6*cm
                    used_real_chart = True
            except Exception as e:
                logger.warning(f"Failed to render SVG chart: {e}")

        if not used_real_chart:
            intro = "Voici une representation de votre carte natale. Chaque abreviation dans le cercle interieur represente un astre, place dans le signe qu'il occupait a votre naissance. Les planetes en rouge (R) sont retrogrades."
            y = self._draw_centered_block(c, intro, y, font_size=10, color=LIGHT_TEXT)
            all_planets = self._get_all_planets(planets_data, horoscope_data)
            y = self._draw_natal_chart(c, y, all_planets, zodiac_sign)
        else:
            all_planets = self._get_all_planets(planets_data, horoscope_data)

        # Planet positions summary table
        self._new_page(c)
        y = self._sub_header(c, "Positions de vos Astres", self.height - 3.5*cm)

        all_to_show = ['Sun','Moon','Ascendant','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
        for p in (all_planets or []):
            name = p.get('name', '')
            if name not in all_to_show:
                continue
            if y < 3*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            info = PLANETES_DETAILS.get(name, {})
            nom_fr = info.get('nom_fr', name)
            sym = info.get('symbole', '')
            sign_fr = self._get_french_sign(p.get('sign', ''))
            house = p.get('house', '?')
            deg = p.get('normDegree', p.get('norm_degree', 0))
            is_retro = str(p.get('isRetro', p.get('is_retro', 'false'))).lower() == 'true'
            retro_txt = " (Retrograde)" if is_retro else ""

            c.setFillColor(CREAM)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(self.margin + 0.5*cm, y, f"{sym} {nom_fr}")
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 10)
            c.drawString(self.margin + 5.5*cm, y, f"en {sign_fr}")
            c.drawString(self.margin + 10*cm, y, f"Maison {house}")
            c.drawString(self.margin + 13*cm, y, f"{deg:.1f} deg{retro_txt}")
            y -= 0.55*cm

        # Houses table
        if horoscope_data and 'houses' in horoscope_data:
            y -= 0.8*cm
            y = self._sub_header(c, "Cuspides de vos Maisons", y, size=12)
            for h in horoscope_data['houses']:
                if y < 2.5*cm:
                    self._new_page(c)
                    y = self.height - 3.5*cm
                house_num = h.get('house', '?')
                sign_fr = self._get_french_sign(h.get('sign', ''))
                deg = h.get('degree', 0)
                maison_info = MAISONS_DETAILS.get(house_num, {})
                domaine = maison_info.get('domaine', '')

                c.setFillColor(GOLD)
                c.setFont("Helvetica-Bold", 9)
                c.drawString(self.margin + 0.3*cm, y, f"Maison {house_num}")
                c.setFillColor(CREAM)
                c.setFont("Helvetica", 9)
                c.drawString(self.margin + 3.5*cm, y, f"en {sign_fr}")
                c.setFillColor(LIGHT_TEXT)
                c.setFillAlpha(0.7)
                c.setFont("Helvetica-Oblique", 8)
                c.drawString(self.margin + 7*cm, y, domaine[:50])
                c.setFillAlpha(1.0)
                y -= 0.45*cm

    def _page_elements(self, c, planets_data, horoscope_data):
        """Elemental and modal balance analysis"""
        self._new_page(c)
        y = self._chapter_header(c, "Equilibre Elementaire", "La repartition des energies dans votre theme")

        all_planets = self._get_all_planets(planets_data, horoscope_data)
        if not all_planets:
            y = self._draw_centered_block(c, "Donnees planetaires non disponibles pour cette analyse.", y)
            return

        # Count elements and modalities
        elements = {"Feu": 0, "Terre": 0, "Air": 0, "Eau": 0}
        modalities = {"Cardinal": 0, "Fixe": 0, "Mutable": 0}
        personal_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Ascendant']

        for p in all_planets:
            if p.get('name') in personal_planets:
                sign = p.get('sign', '')
                elem = SIGNE_ELEMENT.get(sign)
                mod = SIGNE_MODALITE.get(sign)
                if elem:
                    elements[elem] += 1
                if mod:
                    modalities[mod] += 1

        # Draw element bars
        intro = "Chaque planete de votre theme se trouve dans un signe, et chaque signe appartient a un element (Feu, Terre, Air, Eau) et une modalite (Cardinal, Fixe, Mutable). La repartition de vos planetes revele l'equilibre energetique fondamental de votre personnalite."
        y = self._draw_centered_block(c, intro, y, font_size=10, color=LIGHT_TEXT)
        y -= 0.5*cm

        element_colors = {"Feu": FIRE_COLOR, "Terre": EARTH_COLOR, "Air": AIR_COLOR, "Eau": WATER_COLOR}
        element_emojis = {"Feu": "Feu", "Terre": "Terre", "Air": "Air", "Eau": "Eau"}
        total = max(sum(elements.values()), 1)
        bar_max_w = 8*cm

        for elem, count in elements.items():
            if y < 3*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            c.setFillColor(CREAM)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(self.margin + 0.5*cm, y, f"{element_emojis[elem]}")
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 10)
            c.drawString(self.margin + 3*cm, y, f"{count} planete(s)")

            # Draw bar
            bar_w = (count / total) * bar_max_w
            bar_x = self.margin + 7*cm
            c.setFillColor(element_colors[elem])
            c.setFillAlpha(0.7)
            c.roundRect(bar_x, y - 0.15*cm, bar_w, 0.5*cm, 3, fill=1)
            c.setFillAlpha(1.0)
            y -= 1*cm

        # Dominant element text
        dominant_elem = max(elements, key=elements.get)
        weak_elem = min(elements, key=elements.get)
        y -= 0.5*cm
        y = self._sub_header(c, f"Element Dominant : {dominant_elem}", y, size=12)
        dom_text = ELEMENTS_DOMINANTS.get(dominant_elem, {}).get('dominant', '')
        y = self._draw_centered_block(c, dom_text, y, font_size=10)

        if elements[weak_elem] <= 1:
            y = self._sub_header(c, f"Element a Cultiver : {weak_elem}", y, size=12)
            weak_text = ELEMENTS_DOMINANTS.get(weak_elem, {}).get('faible', '')
            y = self._draw_centered_block(c, weak_text, y, font_size=10)

        # Modalities
        y -= 0.5*cm
        y = self._sub_header(c, "Repartition des Modalites", y, size=12)
        dominant_mod = max(modalities, key=modalities.get)
        for mod, count in modalities.items():
            if y < 2.5*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            c.setFillColor(GOLD if mod == dominant_mod else LIGHT_TEXT)
            c.setFont("Helvetica-Bold" if mod == dominant_mod else "Helvetica", 10)
            c.drawCentredString(self.width / 2, y, f"{mod} : {count} planete(s)")
            y -= 0.5*cm

        y -= 0.3*cm
        mod_desc = MODALITES_DESCRIPTIONS.get(dominant_mod, '')
        y = self._draw_centered_block(c, f"Modalite dominante ({dominant_mod}) : {mod_desc}", y, font_size=10)

    def _page_sun(self, c, planets_data, zodiac_sign):
        self._new_page(c)
        signe = SIGNES_DETAILS.get(zodiac_sign, {})
        signe_fr = signe.get('nom_fr', zodiac_sign)
        symbole = signe.get('symbole', '')

        y = self._chapter_header(c, f"Votre Soleil en {signe_fr}", f"{symbole} L'essence de qui vous etes")

        sun_intro = "En astrologie, le Soleil represente votre identite profonde, votre vitalite et ce qui vous fait vibrer. C'est le noyau de votre personnalite, la lumiere que vous portez en vous et que vous etes appele(e) a partager avec le monde. Le signe dans lequel se trouve votre Soleil revele vos motivations fondamentales, vos aspirations et la maniere dont vous brillez le mieux."
        y = self._draw_centered_block(c, sun_intro, y, font_size=10, color=LIGHT_TEXT)

        img = self._get_zodiac_image(zodiac_sign)
        if img:
            y = self._draw_image_safe(c, img, y, w=6*cm, h=6*cm)

        sun_data = next((p for p in (planets_data or []) if p.get('name') == 'Sun'), None)
        if sun_data:
            y = self._draw_info_box(c, f"Soleil en {signe_fr} - Maison {sun_data.get('house','?')} - {sun_data.get('normDegree', sun_data.get('norm_degree',0)):.1f} deg", y)

        # Sun in sign specific interpretation
        sun_en_signe = PLANETES_DETAILS.get('Sun', {}).get('en_signe', {}).get(zodiac_sign, '')
        if sun_en_signe:
            y = self._draw_centered_block(c, sun_en_signe, y, font_size=10.5, color=CREAM)

        desc = signe.get('description_longue', '')
        y = self._draw_centered_block(c, desc, y, font_size=10.5, color=LIGHT_TEXT)

        # Forces & defis
        self._new_page(c)
        y = self.height - 4*cm
        y = self._sub_header(c, "Vos Forces Solaires", y)
        for f in signe.get('forces', []):
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 11)
            c.drawCentredString(self.width / 2, y, f"- {f}")
            y -= 0.5*cm

        y -= 0.5*cm
        y = self._sub_header(c, "Vos Defis a Transcender", y)
        for d in signe.get('defis', []):
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 11)
            c.drawCentredString(self.width / 2, y, f"- {d}")
            y -= 0.5*cm

        y -= 1*cm
        c.setFillColor(MEDIUM_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(3*cm, y - 1.5*cm, self.width - 6*cm, 1.5*cm, 10, fill=1)
        c.setFillAlpha(1.0)
        c.setFillColor(CREAM)
        c.setFont("Helvetica-BoldOblique", 11)
        c.drawCentredString(self.width / 2, y - 1*cm, f"Affirmation : {signe.get('affirmation','')}")

    def _page_moon(self, c, planets_data):
        self._new_page(c)
        moon_data = next((p for p in (planets_data or []) if p.get('name') == 'Moon'), None)
        moon_sign = moon_data.get('sign', 'Cancer') if moon_data else 'Cancer'
        moon_info = SIGNES_DETAILS.get(moon_sign, {})
        moon_fr = moon_info.get('nom_fr', moon_sign)

        y = self._chapter_header(c, f"Votre Lune en {moon_fr}", "Votre monde emotionnel interieur")

        moon_intro = "La Lune en astrologie represente votre monde interieur : vos emotions, vos instincts, vos besoins de securite. Si le Soleil est ce que vous montrez au monde, la Lune est ce que vous ressentez dans l'intimite. Elle revele la facon dont vous avez ete nourri(e) emotionnellement dans l'enfance et ce dont vous avez besoin pour vous sentir en securite aujourd'hui."
        y = self._draw_centered_block(c, moon_intro, y, font_size=10, color=LIGHT_TEXT)

        illust = self._get_illustration(6)
        if illust:
            y = self._draw_image_safe(c, illust, y, w=7*cm, h=7*cm)

        if moon_data:
            y = self._draw_info_box(c, f"Lune en {moon_fr} - Maison {moon_data.get('house','?')}", y)

        lune_info = PLANETES_DETAILS.get('Moon', {})
        en_signe = lune_info.get('en_signe', {}).get(moon_sign, '')
        if en_signe:
            y = self._draw_centered_block(c, en_signe, y, font_size=10.5, color=CREAM)

        element = moon_info.get('element', 'Terre')
        needs = {"Feu": "action et passion", "Terre": "securite et stabilite", "Air": "communication et echanges", "Eau": "connexion emotionnelle et intimite"}
        txt = f"Avec une Lune en signe de {element}, vos emotions ont besoin de {needs.get(element, 'harmonie')} pour s'epanouir. Vous percevez le monde a travers le filtre de cet element, ce qui influence profondement vos reactions instinctives et vos besoins fondamentaux."
        y = self._draw_centered_block(c, txt, y, font_size=10.5)

        # Moon house meaning
        if moon_data:
            house = moon_data.get('house', 1)
            h_info = MAISONS_DETAILS.get(house, {})
            if h_info:
                h_txt = f"Votre Lune en Maison {house} ({h_info.get('domaine', '')}) signifie que vos besoins emotionnels les plus profonds s'expriment dans le domaine de {h_info.get('domaine', '').lower()}. {h_info.get('description', '')}"
                y = self._draw_centered_block(c, h_txt, y, font_size=10)

    def _page_ascendant(self, c, planets_data):
        self._new_page(c)
        asc_data = next((p for p in (planets_data or []) if p.get('name') == 'Ascendant'), None)
        asc_sign = asc_data.get('sign', 'Leo') if asc_data else 'Leo'
        asc_info = SIGNES_DETAILS.get(asc_sign, {})
        asc_fr = asc_info.get('nom_fr', asc_sign)

        y = self._chapter_header(c, f"Ascendant {asc_fr}", "Votre masque social")

        asc_intro = "L'Ascendant est le signe qui se levait a l'horizon Est au moment precis de votre naissance. Il represente la premiere impression que vous donnez aux autres, votre apparence physique, et la maniere dont vous abordez spontanement les nouvelles situations. Si le Soleil est votre essence et la Lune votre vie interieure, l'Ascendant est la porte d'entree par laquelle le monde vous decouvre."
        y = self._draw_centered_block(c, asc_intro, y, font_size=10, color=LIGHT_TEXT)

        illust = self._get_illustration(1)
        if illust:
            y = self._draw_image_safe(c, illust, y, w=7*cm, h=7*cm)

        desc = f"Avec un Ascendant en {asc_fr}, vous degagez naturellement l'energie de ce signe. {asc_info.get('description_courte', '')} Les gens vous percoivent d'abord a travers cette lentille avant de decouvrir votre Soleil. L'element {asc_info.get('element', '')} colore votre approche de la vie quotidienne."
        y = self._draw_centered_block(c, desc, y, font_size=10.5)

        y -= 0.3*cm
        y = self._sub_header(c, "Traits visibles de votre Ascendant", y, size=12)
        for f in asc_info.get('forces', [])[:5]:
            if y < 2.5*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 10)
            c.drawCentredString(self.width / 2, y, f"- {f}")
            y -= 0.45*cm

    def _page_planet_detail(self, c, planet_name, planets_data, illust_idx=None):
        """Detailed page for a single planet"""
        self._new_page(c)
        planet_data = next((p for p in (planets_data or []) if p.get('name') == planet_name), None)
        if not planet_data:
            return

        pinfo = PLANETES_DETAILS.get(planet_name, {})
        pfr = pinfo.get('nom_fr', planet_name)
        sym = pinfo.get('symbole', '')
        sign = planet_data.get('sign', '')
        sign_fr = self._get_french_sign(sign)
        house = planet_data.get('house', '?')
        is_retro = str(planet_data.get('isRetro', planet_data.get('is_retro', 'false'))).lower() == 'true'

        titles = {
            "Mercury": ("Mercure - Votre Esprit", "Comment vous pensez et communiquez"),
            "Venus": ("Venus - Votre Coeur", "Comment vous aimez et ce que vous valorisez"),
            "Mars": ("Mars - Votre Energie", "Comment vous agissez et vous affirmez"),
        }
        title, subtitle = titles.get(planet_name, (f"{pfr}", pinfo.get('domaine', '')))
        y = self._chapter_header(c, title, subtitle)

        # General planet description
        y = self._draw_centered_block(c, pinfo.get('description', ''), y, font_size=10, color=LIGHT_TEXT)

        if illust_idx is not None:
            illust = self._get_illustration(illust_idx)
            if illust:
                y = self._draw_image_safe(c, illust, y, w=6*cm, h=6*cm)

        # Position info box
        retro_txt = " - Retrograde" if is_retro else ""
        y = self._draw_info_box(c, f"{sym} {pfr} en {sign_fr} - Maison {house}{retro_txt}", y)

        # Sign-specific interpretation
        en_signe_map = PLANET_EN_SIGNE_MAP.get(planet_name, {})
        en_signe = en_signe_map.get(sign, '')
        if en_signe:
            y = self._draw_centered_block(c, en_signe, y, font_size=10.5, color=CREAM)

        # House interpretation
        h_info = MAISONS_DETAILS.get(house if isinstance(house, int) else int(house) if str(house).isdigit() else 1, {})
        if h_info:
            h_txt = f"{pfr} en Maison {house} oriente cette energie vers le domaine de {h_info.get('domaine', '').lower()}. {h_info.get('description', '')}"
            y = self._draw_centered_block(c, h_txt, y, font_size=10)

        # Retrograde note
        if is_retro:
            retro_desc = RETROGRADE_DESCRIPTIONS.get(planet_name, '')
            if retro_desc:
                y -= 0.3*cm
                y = self._sub_header(c, f"{pfr} Retrograde dans votre Theme", y, size=12)
                y = self._draw_centered_block(c, retro_desc, y, font_size=10, color=HexColor('#FF9999'))

    def _page_jupiter_saturn(self, c, planets_data):
        """Combined Jupiter & Saturn page"""
        self._new_page(c)
        y = self._chapter_header(c, "Jupiter & Saturne", "Expansion et structure de votre vie")

        intro = "Jupiter et Saturne forment le couple cosmique qui structure votre rapport au monde. Jupiter est le Grand Benefique, indiquant ou vous trouvez la chance et l'expansion. Saturne est le Grand Maitre, revelant ou vous devez developper discipline et maturite. Ensemble, ils dessinent l'architecture de votre destin social."
        y = self._draw_centered_block(c, intro, y, font_size=10, color=LIGHT_TEXT)

        for pname in ['Jupiter', 'Saturn']:
            planet = next((p for p in (planets_data or []) if p.get('name') == pname), None)
            if not planet:
                continue
            if y < 5*cm:
                self._new_page(c)
                y = self.height - 3.5*cm

            pinfo = PLANETES_DETAILS.get(pname, {})
            pfr = pinfo.get('nom_fr', pname)
            sym = pinfo.get('symbole', '')
            sign = planet.get('sign', '')
            sign_fr = self._get_french_sign(sign)
            house = planet.get('house', '?')
            is_retro = str(planet.get('isRetro', planet.get('is_retro', 'false'))).lower() == 'true'

            y = self._sub_header(c, f"{sym} {pfr} en {sign_fr} - Maison {house}", y)

            y = self._draw_centered_block(c, pinfo.get('description', ''), y, font_size=10, color=LIGHT_TEXT)

            en_signe_map = PLANET_EN_SIGNE_MAP.get(pname, {})
            en_signe = en_signe_map.get(sign, '')
            if en_signe:
                y = self._draw_centered_block(c, en_signe, y, font_size=10, color=CREAM)

            if is_retro:
                retro = RETROGRADE_DESCRIPTIONS.get(pname, '')
                if retro:
                    y = self._draw_centered_block(c, f"[Retrograde] {retro}", y, font_size=9.5, color=HexColor('#FF9999'))
            y -= 0.5*cm

    def _page_retrogrades(self, c, planets_data, horoscope_data):
        """Page dedicated to retrograde planets"""
        all_planets = self._get_all_planets(planets_data, horoscope_data)
        retro_planets = [p for p in (all_planets or []) if str(p.get('isRetro', p.get('is_retro', 'false'))).lower() == 'true']

        if not retro_planets:
            return  # Skip if no retrogrades

        self._new_page(c)
        y = self._chapter_header(c, "Planetes Retrogrades", "Les energies interiorisees de votre theme")

        intro = f"Dans votre theme natal, {len(retro_planets)} planete(s) sont en mouvement retrograde apparent. Une planete retrograde n'est pas affaiblie : son energie est dirigee vers l'interieur plutot que vers l'exterieur. C'est une invitation a la reflexion, a la revision et a la maitrise interieure de cette energie."
        y = self._draw_centered_block(c, intro, y, font_size=10, color=LIGHT_TEXT)
        y -= 0.3*cm

        for p in retro_planets:
            name = p.get('name', '')
            if name in ['Node', 'Chiron', 'Part of Fortune', 'Lilith']:
                continue
            if y < 4*cm:
                self._new_page(c)
                y = self.height - 3.5*cm

            pinfo = PLANETES_DETAILS.get(name, {})
            pfr = pinfo.get('nom_fr', name)
            sym = pinfo.get('symbole', '')
            sign_fr = self._get_french_sign(p.get('sign', ''))

            y = self._sub_header(c, f"{sym} {pfr} Retrograde en {sign_fr}", y, size=12)
            desc = RETROGRADE_DESCRIPTIONS.get(name, '')
            if desc:
                y = self._draw_centered_block(c, desc, y, font_size=10)
            y -= 0.3*cm

    def _page_aspects(self, c, horoscope_data):
        """Major aspects between planets"""
        if not horoscope_data or 'aspects' not in horoscope_data:
            return

        self._new_page(c)
        y = self._chapter_header(c, "Les Aspects Planetaires", "L'alchimie entre vos planetes")

        intro = "Les aspects sont les angles que forment les planetes entre elles dans votre carte du ciel. Ils revelent comment les differentes facettes de votre personnalite interagissent. Les trigones et sextiles indiquent des talents naturels et des facilites. Les carres et oppositions signalent des tensions qui vous poussent a grandir. Les conjonctions fusionnent les energies."
        y = self._draw_centered_block(c, intro, y, font_size=10, color=LIGHT_TEXT)
        y -= 0.3*cm

        aspects = horoscope_data.get('aspects', [])
        # Filter to personal planet aspects
        personal = {'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'}

        # Group by harmonious vs challenging
        harmonious = []
        challenging = []
        for a in aspects:
            p1 = a.get('aspecting_planet', '')
            p2 = a.get('aspected_planet', '')
            if p1 not in personal or p2 not in personal:
                continue
            atype = a.get('type', '')
            if atype in ('Trine', 'Sextile'):
                harmonious.append(a)
            elif atype in ('Square', 'Opposition'):
                challenging.append(a)
            elif atype == 'Conjunction':
                harmonious.append(a)

        # Harmonious aspects
        if harmonious:
            y = self._sub_header(c, "Aspects Harmonieux - Vos Talents", y, size=13)
            for a in harmonious[:8]:
                if y < 4*cm:
                    self._new_page(c)
                    y = self.height - 3.5*cm

                p1 = a['aspecting_planet']
                p2 = a['aspected_planet']
                atype = a['type']
                orb = a.get('orb', 0)

                p1_fr = PLANETES_DETAILS.get(p1, {}).get('nom_fr', p1)
                p2_fr = PLANETES_DETAILS.get(p2, {}).get('nom_fr', p2)
                aspect_info = ASPECTS_TYPES.get(atype, {})
                aspect_fr = aspect_info.get('nom_fr', atype)

                c.setFillColor(GOLD)
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(self.width / 2, y, f"{p1_fr} {aspect_fr} {p2_fr} (orbe: {orb} deg)")
                y -= 0.6*cm

                interp = get_aspect_interpretation(p1, p2, atype)
                if interp:
                    y = self._draw_centered_block(c, interp, y, font_size=9.5, color=LIGHT_TEXT)
                else:
                    gen_desc = aspect_info.get('description', '')
                    if gen_desc:
                        y = self._draw_centered_block(c, gen_desc, y, font_size=9.5, color=LIGHT_TEXT)
                y -= 0.2*cm

        # Challenging aspects
        if challenging:
            if y < 5*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            y = self._sub_header(c, "Aspects de Croissance - Vos Defis", y, size=13)
            for a in challenging[:8]:
                if y < 4*cm:
                    self._new_page(c)
                    y = self.height - 3.5*cm

                p1 = a['aspecting_planet']
                p2 = a['aspected_planet']
                atype = a['type']
                orb = a.get('orb', 0)

                p1_fr = PLANETES_DETAILS.get(p1, {}).get('nom_fr', p1)
                p2_fr = PLANETES_DETAILS.get(p2, {}).get('nom_fr', p2)
                aspect_info = ASPECTS_TYPES.get(atype, {})
                aspect_fr = aspect_info.get('nom_fr', atype)

                c.setFillColor(HexColor('#FF9999'))
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(self.width / 2, y, f"{p1_fr} {aspect_fr} {p2_fr} (orbe: {orb} deg)")
                y -= 0.6*cm

                interp = get_aspect_interpretation(p1, p2, atype)
                if interp:
                    y = self._draw_centered_block(c, interp, y, font_size=9.5, color=LIGHT_TEXT)
                else:
                    gen_desc = aspect_info.get('description', '')
                    if gen_desc:
                        y = self._draw_centered_block(c, gen_desc, y, font_size=9.5, color=LIGHT_TEXT)
                y -= 0.2*cm

    def _page_houses(self, c, planets_data, horoscope_data):
        """Personalized houses with planets in each house"""
        self._new_page(c)
        y = self._chapter_header(c, "Les Maisons Astrologiques", "Les 12 domaines de votre vie")

        illust = self._get_illustration(2)
        if illust:
            y = self._draw_image_safe(c, illust, y, w=7*cm, h=7*cm)

        intro = "Les douze maisons representent les grands domaines de votre existence. Les planetes qui s'y trouvent colorent ces domaines de leur energie specifique."
        y = self._draw_centered_block(c, intro, y, font_size=10, color=LIGHT_TEXT)

        # Build planet-per-house map
        all_planets = self._get_all_planets(planets_data, horoscope_data)
        house_planets = {}
        for p in (all_planets or []):
            h = p.get('house', 0)
            if h and p.get('name') not in ('Ascendant', 'Part of Fortune'):
                if h not in house_planets:
                    house_planets[h] = []
                house_planets[h].append(p)

        for house_num in range(1, 13):
            if y < 4*cm:
                self._new_page(c)
                y = self.height - 3.5*cm

            m_info = MAISONS_DETAILS.get(house_num, {})
            m_name = m_info.get('nom', f'Maison {house_num}')

            # House sign from horoscope data
            house_sign = ""
            if horoscope_data and 'houses' in horoscope_data:
                h_data = next((h for h in horoscope_data['houses'] if h.get('house') == house_num), None)
                if h_data:
                    house_sign = f" en {self._get_french_sign(h_data.get('sign', ''))}"

            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(self.margin + 0.3*cm, y, f"{m_name}{house_sign}")

            # Planets in this house
            planets_in_house = house_planets.get(house_num, [])
            if planets_in_house:
                names = [PLANETES_DETAILS.get(p['name'], {}).get('nom_fr', p['name']) for p in planets_in_house]
                c.setFillColor(CREAM)
                c.setFont("Helvetica-Oblique", 9)
                c.drawString(self.margin + 0.3*cm, y - 0.4*cm, f"Planetes presentes : {', '.join(names)}")
                y -= 0.85*cm
            else:
                y -= 0.5*cm

            # Description
            desc = m_info.get('description', '')
            if desc:
                y = self._draw_centered_block(c, desc, y, font_size=9.5, color=LIGHT_TEXT)
            y -= 0.2*cm

    def _page_chiron_node(self, c, horoscope_data):
        """Chiron and North Node page"""
        if not horoscope_data:
            return

        planets = horoscope_data.get('planets', [])
        chiron = next((p for p in planets if p.get('name') == 'Chiron'), None)
        node = next((p for p in planets if p.get('name') == 'Node'), None)
        lilith = horoscope_data.get('lilith')

        if not chiron and not node:
            return

        self._new_page(c)
        y = self._chapter_header(c, "Chiron, Lilith & Noeud Nord", "Guerison, ombre et destinee karmique")

        intro = "Ces trois points celestes revelent des dimensions profondes de votre parcours d'ame : la blessure qui devient votre don de guerison (Chiron), l'ombre a integrer (Lilith), et la direction de votre evolution karmique (Noeud Nord)."
        y = self._draw_centered_block(c, intro, y, font_size=10, color=LIGHT_TEXT)

        # Chiron
        if chiron:
            sign = chiron.get('sign', '')
            sign_fr = self._get_french_sign(sign)
            house = chiron.get('house', '?')
            y = self._sub_header(c, f"Chiron en {sign_fr} - Maison {house}", y, size=13)
            chiron_intro = "Chiron est le Guerisseur Blesse, un asteroide qui revele votre blessure la plus profonde et, paradoxalement, votre plus grand pouvoir de guerison."
            y = self._draw_centered_block(c, chiron_intro, y, font_size=10, color=LIGHT_TEXT)
            chiron_desc = CHIRON_EN_SIGNE.get(sign, '')
            if chiron_desc:
                y = self._draw_centered_block(c, chiron_desc, y, font_size=10.5, color=CREAM)

        # Lilith
        if lilith and isinstance(lilith, dict):
            sign = lilith.get('sign', '')
            sign_fr = self._get_french_sign(sign)
            house = lilith.get('house', '?')
            if y < 5*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            y = self._sub_header(c, f"Lilith Noire en {sign_fr} - Maison {house}", y, size=13)
            lilith_intro = "Lilith Noire represente votre part d'ombre, votre pouvoir brut et non domestique, la partie de vous que la societe vous a appris a reprimer."
            y = self._draw_centered_block(c, lilith_intro, y, font_size=10, color=LIGHT_TEXT)
            lilith_desc = LILITH_EN_SIGNE.get(sign, '')
            if lilith_desc:
                y = self._draw_centered_block(c, lilith_desc, y, font_size=10.5, color=CREAM)

        # North Node
        if node:
            sign = node.get('sign', '')
            sign_fr = self._get_french_sign(sign)
            house = node.get('house', '?')
            if y < 5*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            y = self._sub_header(c, f"Noeud Nord en {sign_fr} - Maison {house}", y, size=13)
            node_intro = "Le Noeud Nord indique la direction de votre evolution karmique, les qualites que votre ame est venue developper dans cette vie."
            y = self._draw_centered_block(c, node_intro, y, font_size=10, color=LIGHT_TEXT)
            node_desc = NOEUD_NORD_EN_SIGNE.get(sign, '')
            if node_desc:
                y = self._draw_centered_block(c, node_desc, y, font_size=10.5, color=CREAM)

    def _page_life_path(self, c, chemin_vie, annee_perso):
        self._new_page(c)
        chemin_info = CHEMINS_VIE.get(chemin_vie, CHEMINS_VIE.get(9, {}))

        y = self._chapter_header(c, f"Chemin de Vie {chemin_vie}", f"{chemin_info.get('titre', 'Le Voyageur')}")

        illust = self._get_illustration(7)
        if illust:
            y = self._draw_image_safe(c, illust, y, w=8*cm, h=5*cm)

        path_intro = f"En numerologie, votre Chemin de Vie est le nombre le plus important de votre profil. Il se calcule a partir de votre date de naissance complete et revele la grande direction de votre existence. Votre Chemin de Vie {chemin_vie} indique que votre mission d'ame est centree sur le theme suivant :"
        y = self._draw_centered_block(c, path_intro, y, font_size=10.5, color=LIGHT_TEXT)

        c.setFillColor(MEDIUM_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(3*cm, y - 1.2*cm, self.width - 6*cm, 1.2*cm, 10, fill=1)
        c.setFillAlpha(1.0)
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.width / 2, y - 0.8*cm, f"Mot-cle : {chemin_info.get('mot_cle', 'Evolution')}")
        y -= 2.2*cm

        y = self._sub_header(c, "Votre Mission d'Ame", y, size=13)
        mission = chemin_info.get('mission', '')
        y = self._draw_centered_block(c, mission, y, font_size=10.5)

        y = self._sub_header(c, "Vos Dons Naturels", y, size=13)
        for f in chemin_info.get('forces', []):
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 11)
            c.drawCentredString(self.width / 2, y, f"- {f}")
            y -= 0.5*cm

        y -= 0.3*cm
        y = self._sub_header(c, "Defis a Transcender", y, size=13)
        for d in chemin_info.get('defis', []):
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 11)
            c.drawCentredString(self.width / 2, y, f"- {d}")
            y -= 0.5*cm

        # Concrete advice page
        self._new_page(c)
        y = self._chapter_header(c, "Conseils Concrets", f"Pour votre Chemin de Vie {chemin_vie} et votre Annee {annee_perso}")

        annee_info = PREVISIONS_ANNEE_PERSONNELLE.get(annee_perso, PREVISIONS_ANNEE_PERSONNELLE.get(1, {}))
        conseil_chemin = chemin_info.get('conseil', '')
        theme_annee = annee_info.get('theme', 'Evolution')

        real_advice = f"""Votre Chemin de Vie {chemin_vie} vous invite a incarner pleinement le theme de {chemin_info.get('mot_cle', 'evolution').lower()}. Concretement, cela signifie que les situations qui vous font le plus grandir sont celles ou vous exercez cette qualite.

Conseil pour votre chemin : {conseil_chemin}

Votre annee personnelle 2026 est une annee {annee_perso}, dont le theme est : {theme_annee}. L'energie dominante de cette annee vous pousse vers ce domaine.

Voici des actions concretes pour honorer cette double influence :

1. Chaque matin, prenez 5 minutes pour vous aligner avec l'intention de votre chemin de vie. Demandez-vous : comment puis-je exprimer mon don de {chemin_info.get('mot_cle', 'evolution').lower()} aujourd'hui ?

2. Cette annee, concentrez-vous sur le domaine de {theme_annee.lower()}. C'est la ou l'univers place ses ressources pour vous.

3. Notez dans un journal les synchronicites et les signes que vous recevez. Votre chemin de vie {chemin_vie} est particulierement receptif aux messages subtils de l'univers.

4. Si vous ressentez de la resistance, c'est souvent le signe que vous approchez d'une percee importante.

5. Entourez-vous de personnes qui resonent avec vos valeurs profondes."""

        y = self._draw_centered_block(c, real_advice, y, font_size=10, color=LIGHT_TEXT)

        if y > 3*cm:
            y -= 0.5*cm
            c.setFillColor(GOLD)
            c.setFont("Helvetica", 10)
            c.drawCentredString(self.width / 2, y, f"Couleurs : {chemin_info.get('couleur', 'Or')} | Pierres : {chemin_info.get('pierre', 'Cristal')}")

    def _page_previsions(self, c, annee_perso):
        self._new_page(c)
        annee_info = PREVISIONS_ANNEE_PERSONNELLE.get(annee_perso, PREVISIONS_ANNEE_PERSONNELLE.get(1, {}))

        y = self._chapter_header(c, f"Previsions 2026", f"Annee Personnelle {annee_perso} : {annee_info.get('theme', 'Evolution')}")

        illust = self._get_illustration(8)
        if illust:
            y = self._draw_image_safe(c, illust, y, w=7*cm, h=7*cm)

        resume = annee_info.get('resume', '')
        y = self._draw_centered_block(c, resume, y, font_size=11, color=CREAM)

        domaines = annee_info.get('domaines', {})
        labels = {'carriere': 'Carriere & Travail', 'amour': 'Amour & Relations', 'sante': 'Sante & Bien-etre', 'finances': 'Finances', 'spirituel': 'Spiritualite'}
        for dom, txt in domaines.items():
            if y < 4*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            y = self._sub_header(c, labels.get(dom, dom), y, size=12)
            y = self._draw_centered_block(c, txt, y, font_size=10)

        self._new_page(c)
        y = self.height - 4*cm
        y = self._sub_header(c, "Conseil Cle pour 2026", y)
        conseil = annee_info.get('conseil_cle', '')
        y = self._draw_centered_block(c, conseil, y, font_size=11, color=CREAM)

        mois = ['Janvier','Fevrier','Mars','Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Decembre']
        mois_forts = annee_info.get('mois_forts', [])
        y -= 0.5*cm
        y = self._sub_header(c, "Mois les plus favorables :", y, size=12)
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 11)
        c.drawCentredString(self.width / 2, y, ", ".join([mois[m-1] for m in mois_forts if m <= 12]))

    def _page_5_year(self, c, annee_perso_base):
        self._new_page(c)
        y = self._chapter_header(c, "Vision sur 5 Ans", "2026 - 2030 : Votre trajectoire cosmique")

        intro = "Les cinq prochaines annees forment un chapitre important de votre vie. Chaque annee apporte ses propres energies et opportunites, suivant le cycle naturel de la numerologie."
        y = self._draw_centered_block(c, intro, y, font_size=10.5)
        y -= 0.3*cm

        for off in range(5):
            if y < 4*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            year = 2026 + off
            ap = ((annee_perso_base - 1 + off) % 9) + 1
            ai = PREVISIONS_ANNEE_PERSONNELLE.get(ap, {})
            y = self._sub_header(c, f"{year} - Annee {ap} : {ai.get('theme', 'Evolution')}", y, size=12)
            resume = ai.get('resume', '')[:200] + "..."
            y = self._draw_centered_block(c, resume, y, font_size=10)
            y -= 0.3*cm

    def _page_tarot(self, c):
        self._new_page(c)
        y = self._chapter_header(c, "Le Tirage du Tarot", "Messages pour votre chemin")

        intro = "Le Tarot est un miroir de l'ame, revelant les energies qui vous entourent et les potentiels qui s'offrent a vous. Trois cartes ont ete tirees specialement pour vous, representant les influences de votre passe, les energies de votre present et les potentiels de votre futur."
        y = self._draw_centered_block(c, intro, y, font_size=10.5)
        y -= 0.5*cm

        random.seed(42)
        selected = random.sample(list(ARCANES_MAJEURS.keys()), 3)
        positions = ["Passe", "Present", "Futur"]

        for pos, card_num in zip(positions, selected):
            if y < 4*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            card = ARCANES_MAJEURS.get(card_num, {})
            y = self._sub_header(c, f"{pos} : {card.get('nom', '')}", y, size=12)
            c.setFillColor(CREAM)
            c.setFont("Helvetica-Oblique", 10)
            c.drawCentredString(self.width / 2, y, f"Mot-cle : {card.get('mot_cle', '')}")
            y -= 0.6*cm
            message = card.get('message', '')
            y = self._draw_centered_block(c, message, y, font_size=10, color=LIGHT_TEXT)
            y -= 0.3*cm

    def _page_conseils(self, c, zodiac_sign, chemin_vie):
        self._new_page(c)
        signe = SIGNES_DETAILS.get(zodiac_sign, {})
        chemin = CHEMINS_VIE.get(chemin_vie, {})

        y = self._chapter_header(c, "Conseils Personnalises", "Guidance pour votre evolution")

        y = self._sub_header(c, f"Pour votre signe {signe.get('nom_fr', '')} :", y, size=12)
        y = self._draw_centered_block(c, signe.get('conseil_annee', ''), y, font_size=10.5)

        y = self._sub_header(c, f"Pour votre Chemin de Vie {chemin_vie} :", y, size=12)
        y = self._draw_centered_block(c, chemin.get('conseil', ''), y, font_size=10.5)

        y -= 0.5*cm
        y = self._sub_header(c, "Trois Cles pour Votre Evolution :", y, size=12)
        cles = [
            "Honorez votre unicite. Votre combinaison astrologique est unique dans tout l'univers. Cessez de vous comparer aux autres et embrassez pleinement ce qui fait votre singularite.",
            "Ecoutez votre intuition. Votre Lune vous parle constamment a travers vos emotions et vos reves. Faites-lui confiance, meme quand la logique dit le contraire.",
            "Agissez avec conscience. Utilisez les informations de ce manuscrit comme un guide, pas comme un destin fige. Vous restez toujours le createur de votre realite."
        ]
        for cle in cles:
            y = self._draw_centered_block(c, cle, y, font_size=10, color=LIGHT_TEXT)

    def _page_final(self, c, user_data):
        self._new_page(c)

        illust = self._get_illustration(3)
        if illust:
            self._draw_image_safe(c, illust, self.height - 1*cm, w=self.width, h=7*cm)

        y = self.height - 9*cm
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        c.line(4*cm, y + 0.5*cm, self.width - 4*cm, y + 0.5*cm)

        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.width / 2, y, "Message de la Plume Astrale")
        y -= 1.5*cm

        prenom = user_data.get('prenom', 'Cher voyageur')
        lines = [
            f"Cher(e) {prenom},",
            "",
            "Ce manuscrit est un miroir de votre ame,",
            "un guide pour votre voyage sur Terre.",
            "",
            "Les etoiles qui brillaient a votre naissance",
            "continuent de vous accompagner chaque jour.",
            "",
            "Vous etes unique dans tout l'univers.",
            "Personne d'autre n'a votre exact theme celeste.",
            "",
            "Puisse ce document vous rappeler",
            "la magie qui reside en vous,",
            "et vous guider vers votre plus haute expression.",
        ]
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 12)
        for line in lines:
            c.drawCentredString(self.width / 2, y, line)
            y -= 0.55*cm

        y -= 1*cm
        c.setFillColor(MEDIUM_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(3*cm, y - 1.5*cm, self.width - 6*cm, 1.5*cm, 10, fill=1)
        c.setFillAlpha(1.0)
        c.setFillColor(CREAM)
        c.setFont("Helvetica-BoldOblique", 12)
        c.drawCentredString(self.width / 2, y - 0.7*cm, "Que les etoiles vous guident,")
        c.drawCentredString(self.width / 2, y - 1.2*cm, "que la Plume vous eclaire.")

        y -= 3*cm
        c.setStrokeColor(GOLD)
        c.line(5*cm, y, self.width - 5*cm, y)
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(self.width / 2, y - 0.8*cm, "Plume Astrale")
        c.setFillAlpha(0.6)
        c.setFont("Helvetica", 9)
        c.drawCentredString(self.width / 2, y - 1.4*cm, "www.plume-astrale.fr")
        c.setFillAlpha(1.0)

    # ============= HELPERS =============

    def _get_all_planets(self, planets_data, horoscope_data):
        """Get the best available planet data, preferring horoscope_data"""
        if horoscope_data and 'planets' in horoscope_data:
            return horoscope_data['planets']
        return planets_data

    def _calc_life_path(self, date_str):
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            t = d.day + d.month + d.year
            while t > 9 and t not in [11, 22, 33]:
                t = sum(int(x) for x in str(t))
            return t
        except:
            return 1

    def _calc_personal_year(self, date_str, year):
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            t = d.day + d.month + year
            while t > 9:
                t = sum(int(x) for x in str(t))
            return t
        except:
            return 1

    # ============= MAIN =============

    def generate(self, user_data, planets_data=None, horoscope_data=None, chart_svg_url=None):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        zodiac_sign = 'Taurus'
        if planets_data:
            sun = next((p for p in planets_data if p.get('name') == 'Sun'), None)
            if sun:
                zodiac_sign = sun.get('sign', 'Taurus')

        date_str = user_data.get('dateNaissance', '1990-01-01')
        chemin_vie = self._calc_life_path(date_str)
        annee_perso = self._calc_personal_year(date_str, 2026)

        # Build all pages
        self._page_cover(c, user_data, zodiac_sign)
        self._page_sommaire(c)
        self._page_introduction(c)
        self._page_natal_chart(c, planets_data, zodiac_sign, horoscope_data, chart_svg_url=chart_svg_url)
        self._page_elements(c, planets_data, horoscope_data)
        self._page_sun(c, planets_data, zodiac_sign)
        self._page_moon(c, planets_data)
        self._page_ascendant(c, planets_data)
        self._page_planet_detail(c, 'Mercury', planets_data, illust_idx=5)
        self._page_planet_detail(c, 'Venus', planets_data)
        self._page_planet_detail(c, 'Mars', planets_data)
        self._page_jupiter_saturn(c, planets_data)
        self._page_retrogrades(c, planets_data, horoscope_data)
        self._page_aspects(c, horoscope_data)
        self._page_houses(c, planets_data, horoscope_data)
        self._page_chiron_node(c, horoscope_data)
        self._page_life_path(c, chemin_vie, annee_perso)
        self._page_previsions(c, annee_perso)
        self._page_5_year(c, annee_perso)
        self._page_tarot(c)
        self._page_conseils(c, zodiac_sign, chemin_vie)
        self._page_final(c, user_data)

        c.save()
        buffer.seek(0)
        return buffer.getvalue()


def generate_manuscrit_complet(user_data, planets_data=None, horoscope_data=None, chart_svg_url=None):
    gen = ManuscritCompletGenerator()
    return gen.generate(user_data, planets_data, horoscope_data, chart_svg_url=chart_svg_url)
