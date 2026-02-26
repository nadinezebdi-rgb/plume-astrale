"""
Generateur PDF Manuscrit Complet V3
Version enrichie avec contenu pedagogique, illustrations, carte du ciel et texte centre
"""
import io
import os
import math
import random
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import ImageReader
import logging

from services.astro_content import (
    SIGNES_DETAILS, PLANETES_DETAILS, MAISONS_DETAILS,
    CHEMINS_VIE, PREVISIONS_ANNEE_PERSONNELLE, ARCANES_MAJEURS
)

logger = logging.getLogger(__name__)

GOLD = HexColor('#C5A059')
DARK_PURPLE = HexColor('#0F0518')
LIGHT_PURPLE = HexColor('#1A0B2E')
CREAM = HexColor('#F3E5AB')
LIGHT_TEXT = HexColor('#E0D9F6')
MEDIUM_PURPLE = HexColor('#2D1B4E')
SOFT_GOLD = HexColor('#D4AF37')

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
    "eso_priestess.jpg",       # 0: intro
    "eso_birds.jpg",           # 1: ascendant
    "eso_koi.jpg",             # 2: maisons
    "eso_landscape.jpg",       # 3: cover + final
    "eso_lion_zodiac.jpg",     # 4: carte du ciel / soleil
    "eso_crystal_bird.jpg",    # 5: planetes
    "eso_crystal_priestess.jpg", # 6: lune
    "eso_balance_desert.jpg",  # 7: chemin de vie
    "eso_cosmic_balance.jpg",  # 8: previsions
]

# Pedagogical texts
INTRO_WHAT_IS = """Votre theme astral, aussi appele carte du ciel ou theme natal, est une photographie du ciel au moment exact de votre naissance. Il montre la position de chaque planete dans les douze signes du zodiaque et dans les douze maisons astrologiques. C'est une carte unique, aussi personnelle que vos empreintes digitales.

Imaginez le ciel comme un grand cadran divise en douze secteurs (les maisons) et parcouru par dix astres principaux (le Soleil, la Lune et huit planetes). Au moment ou vous avez pris votre premier souffle, chaque astre occupait un signe et une maison precis. Cette configuration celeste revele vos talents naturels, vos defis, votre facon d'aimer, de travailler, de communiquer et d'evoluer.

Ce document est concu comme un guide de decouverte de soi. Il ne predit pas un destin fige : les etoiles inclinent, mais ne determinent pas. Votre libre arbitre reste toujours le capitaine de votre navire. En revanche, connaitre votre theme astral vous offre une boussole precieuse pour naviguer avec plus de conscience et d'alignement."""

INTRO_HOW_TO_USE = """Ce manuscrit est divise en plusieurs chapitres, chacun eclairant une facette de votre personnalite :

Le Soleil represente votre essence fondamentale, ce que vous etes au plus profond. C'est votre identite, votre vitalite, votre raison d'etre.

La Lune revele votre monde emotionnel, vos besoins de securite, votre facon de reagir instinctivement. Elle est le miroir de votre ame.

L'Ascendant est la vitrine de votre personnalite, la premiere impression que vous donnez aux autres. C'est le masque social a travers lequel votre essence solaire s'exprime.

Les Planetes (Mercure, Venus, Mars, Jupiter, Saturne) ajoutent des nuances essentielles : votre facon de penser, d'aimer, d'agir, de vous expandre et de vous structurer.

Les Maisons representent les domaines concrets de votre vie : la famille, le travail, les relations, la spiritualite, etc.

Lisez chaque section avec curiosite et bienveillance. Certains passages vous parleront immediatement, d'autres prendront sens avec le temps. Revenez-y regulierement : un theme astral se revele tout au long d'une vie."""

WHAT_ARE_HOUSES = """En astrologie, les douze maisons representent les douze grands domaines de l'experience humaine. Si les signes du zodiaque decrivent comment les energies s'expriment, les maisons revelent ou elles se manifestent dans votre vie quotidienne.

Chaque maison est associee a un domaine precis. Lorsqu'une planete se trouve dans une maison, elle colore ce domaine de son energie. Par exemple, Venus (amour, beaute) en Maison 10 (carriere) pourrait indiquer une personne qui s'epanouit dans un metier artistique ou qui charme naturellement dans sa vie professionnelle.

Voici les douze maisons et leurs significations :

Maison 1 - L'Identite : C'est vous, votre apparence, votre temperament, la premiere impression que vous donnez. C'est la maison de l'Ascendant.

Maison 2 - Les Ressources : Vos talents, votre rapport a l'argent, vos valeurs materielles et la facon dont vous gagnez votre vie.

Maison 3 - La Communication : Votre facon de penser, de parler, vos relations avec les freres et soeurs, les courts voyages et l'apprentissage au quotidien.

Maison 4 - Les Racines : Votre famille, votre foyer, vos origines, votre monde interieur et votre besoin de securite emotionnelle.

Maison 5 - La Creation : La joie de vivre, les loisirs, les enfants, les histoires d'amour, l'expression creative et artistique.

Maison 6 - Le Quotidien : Le travail au jour le jour, la sante, les routines, le service aux autres et la gestion des details pratiques.

Maison 7 - Les Relations : Le couple, les associations, les contrats. C'est le miroir de la Maison 1 : l'autre vous revele a vous-meme.

Maison 8 - La Transformation : Les crises, les heritages, la sexualite profonde, la mort symbolique et la renaissance. C'est la maison des metamorphoses.

Maison 9 - L'Expansion : Les voyages lointains, les etudes superieures, la philosophie, la spiritualite et la quete de sens.

Maison 10 - La Vocation : Votre carriere, votre reputation, votre contribution au monde. C'est le sommet de votre carte du ciel.

Maison 11 - Les Ideaux : Les amis, les projets collectifs, les espoirs, les reves pour l'avenir et votre role dans la communaute.

Maison 12 - L'Invisible : L'inconscient, les secrets, la solitude creatrice, la spiritualite profonde et les epreuves qui menent a la sagesse."""

SIGN_ORDER = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]


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

    def _draw_left_block(self, c, text, y, font_size=11, color=LIGHT_TEXT, indent=0, leading=1.45):
        c.setFillColor(color)
        c.setFont("Helvetica", font_size)
        paragraphs = text.strip().split('\n')
        lh = font_size * leading / 28.35
        for para in paragraphs:
            para = para.strip()
            if not para:
                y -= lh * cm * 0.5
                continue
            lines = self._wrap(c, para, "Helvetica", font_size, self.width - 2*self.margin - indent)
            for line in lines:
                if y < 2.5*cm:
                    self._new_page(c)
                    y = self.height - 3.5*cm
                    c.setFillColor(color)
                    c.setFont("Helvetica", font_size)
                c.drawString(self.margin + indent, y, line)
                y -= lh * cm
            y -= lh * cm * 0.2
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

    def _draw_natal_chart(self, c, y, planets_data, zodiac_sign):
        """Draw a simple natal chart wheel"""
        cx = self.width / 2
        cy = y - 7*cm
        r_outer = 6*cm
        r_inner = 4*cm
        r_planet = 3*cm

        # Outer circle
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.6)
        c.setLineWidth(1.5)
        c.circle(cx, cy, r_outer)
        c.setLineWidth(0.8)
        c.circle(cx, cy, r_inner)
        c.setStrokeAlpha(1.0)

        # Draw 12 house lines
        for i in range(12):
            angle = math.radians(i * 30)
            x1 = cx + r_inner * math.cos(angle)
            y1 = cy + r_inner * math.sin(angle)
            x2 = cx + r_outer * math.cos(angle)
            y2 = cy + r_outer * math.sin(angle)
            c.setStrokeAlpha(0.3)
            c.line(x1, y1, x2, y2)
        c.setStrokeAlpha(1.0)

        # Sign symbols in outer ring
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

        # Place planets if available
        if planets_data:
            planet_syms = {'Sun': 'Sol', 'Moon': 'Lun', 'Mercury': 'Mer', 'Venus': 'Ven',
                           'Mars': 'Mar', 'Jupiter': 'Jup', 'Saturn': 'Sat'}
            placed = 0
            for p in planets_data:
                name = p.get('name', '')
                if name in planet_syms and placed < 7:
                    sign = p.get('sign', '')
                    idx = SIGN_ORDER.index(sign) if sign in SIGN_ORDER else 0
                    deg = p.get('normDegree', 15)
                    total_angle = idx * 30 + deg
                    angle = math.radians(total_angle)
                    px = cx + r_planet * math.cos(angle)
                    py = cy + r_planet * math.sin(angle)
                    c.setFillColor(CREAM)
                    c.setFont("Helvetica-Bold", 7)
                    c.drawCentredString(px, py, planet_syms[name])
                    placed += 1

        # Center label
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(cx, cy - 0.3*cm, "Votre Carte du Ciel")

        return cy - r_outer - 1.5*cm

    # ============= PAGES =============

    def _page_cover(self, c, user_data, zodiac_sign):
        self.page_num = 0
        self._draw_bg(c, 0)
        prenom = user_data.get('prenom', 'Voyageur Celeste')
        signe_info = SIGNES_DETAILS.get(zodiac_sign, {})
        signe_fr = signe_info.get('nom_fr', zodiac_sign)
        symbole = signe_info.get('symbole', '')

        # Illustration at top
        illust = self._get_illustration(3)  # landscape
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
            ("II", "Votre Carte du Ciel", "La photographie du ciel a votre naissance"),
            ("III", "Votre Soleil", "L'essence de qui vous etes"),
            ("IV", "Votre Lune", "Votre monde emotionnel interieur"),
            ("V", "Votre Ascendant", "Le masque social et la premiere impression"),
            ("VI", "Les Planetes de Votre Theme", "Mercure, Venus, Mars, Jupiter, Saturne"),
            ("VII", "Les Maisons Astrologiques", "Les 12 domaines de votre vie"),
            ("VIII", "Votre Chemin de Vie", "Numerologie et mission d'ame"),
            ("IX", "Previsions 2026", "Votre annee personnelle en detail"),
            ("X", "Vision sur 5 Ans", "2026-2030"),
            ("XI", "Le Tirage du Tarot", "Messages pour votre chemin"),
            ("XII", "Conseils Personnalises", "Guidance pour votre evolution"),
        ]
        for num, title, sub in chapters:
            c.setFillColor(GOLD)
            c.setFont("Helvetica", 11)
            c.drawString(self.margin + 0.3*cm, y, num)
            c.setFillColor(CREAM)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(self.margin + 1.3*cm, y, title)
            c.setFillColor(LIGHT_TEXT)
            c.setFillAlpha(0.6)
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(self.margin + 1.3*cm, y - 0.4*cm, sub)
            c.setFillAlpha(1.0)
            y -= 1.2*cm

    def _page_introduction(self, c):
        self._new_page(c)
        y = self._chapter_header(c, "Qu'est-ce qu'un Theme Astral ?", "Comprendre votre carte celeste")
        y = self._draw_centered_block(c, INTRO_WHAT_IS, y, font_size=10.5, color=LIGHT_TEXT)

        # Illustration
        illust = self._get_illustration(0)  # priestess
        if illust:
            if y < 9*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            y = self._draw_image_safe(c, illust, y, w=8*cm, h=8*cm)

        self._new_page(c)
        y = self._chapter_header(c, "Comment lire ce manuscrit ?", "Un guide pas a pas")
        y = self._draw_centered_block(c, INTRO_HOW_TO_USE, y, font_size=10.5, color=LIGHT_TEXT)

    def _page_natal_chart(self, c, planets_data, zodiac_sign):
        self._new_page(c)
        y = self._chapter_header(c, "Votre Carte du Ciel", "La photographie celeste de votre naissance")
        intro = "Voici une representation simplifiee de votre carte natale. Chaque symbole dans le cercle interieur represente un astre, place dans le signe qu'il occupait a votre naissance. Les douze sections du cercle exterieur representent les douze signes du zodiaque."
        y = self._draw_centered_block(c, intro, y, font_size=10, color=LIGHT_TEXT)

        # Use the lion zodiac wheel illustration instead of drawn chart
        illust = self._get_illustration(4)  # lion zodiac wheel
        if illust:
            y = self._draw_image_safe(c, illust, y, w=10*cm, h=10*cm)

        # Planet positions summary
        if planets_data:
            if y < 6*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(self.width / 2, y, "Positions de vos astres")
            y -= 0.8*cm
            for p in planets_data:
                name = p.get('name', '')
                if name in ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Ascendant']:
                    info = PLANETES_DETAILS.get(name, {})
                    nom_fr = info.get('nom_fr', name)
                    sign_fr = self._get_french_sign(p.get('sign', ''))
                    house = p.get('house', '?')
                    c.setFillColor(CREAM)
                    c.setFont("Helvetica", 10)
                    c.drawCentredString(self.width / 2, y, f"{nom_fr} en {sign_fr} - Maison {house}")
                    y -= 0.45*cm

    def _page_sun(self, c, planets_data, zodiac_sign):
        self._new_page(c)
        signe = SIGNES_DETAILS.get(zodiac_sign, {})
        signe_fr = signe.get('nom_fr', zodiac_sign)
        symbole = signe.get('symbole', '')

        y = self._chapter_header(c, f"Votre Soleil en {signe_fr}", f"{symbole} L'essence de qui vous etes")

        # Pedagogical intro to what the Sun represents
        sun_intro = "En astrologie, le Soleil represente votre identite profonde, votre vitalite et ce qui vous fait vibrer. C'est le noyau de votre personnalite, la lumiere que vous portez en vous et que vous etes appele(e) a partager avec le monde. Le signe dans lequel se trouve votre Soleil revele vos motivations fondamentales, vos aspirations et la maniere dont vous brillez le mieux."
        y = self._draw_centered_block(c, sun_intro, y, font_size=10, color=LIGHT_TEXT)

        # Zodiac image
        img = self._get_zodiac_image(zodiac_sign)
        if img:
            y = self._draw_image_safe(c, img, y, w=6*cm, h=6*cm)

        # Sun data
        sun_data = next((p for p in planets_data if p.get('name') == 'Sun'), None) if planets_data else None
        if sun_data:
            c.setFillColor(MEDIUM_PURPLE)
            c.setFillAlpha(0.5)
            c.roundRect(self.margin, y - 1*cm, self.width - 2*self.margin, 1*cm, 5, fill=1)
            c.setFillAlpha(1.0)
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(self.width/2, y - 0.7*cm, f"Soleil en {signe_fr} - Maison {sun_data.get('house','?')} - Degre {sun_data.get('normDegree',0):.1f}")
            y -= 1.8*cm

        # Long description
        desc = signe.get('description_longue', '')
        y = self._draw_centered_block(c, desc, y, font_size=10.5, color=LIGHT_TEXT)

        # Forces
        self._new_page(c)
        y = self.height - 4*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.width / 2, y, "Vos Forces Solaires")
        y -= 1*cm
        for f in signe.get('forces', []):
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 11)
            c.drawCentredString(self.width / 2, y, f"- {f}")
            y -= 0.5*cm

        y -= 0.5*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.width / 2, y, "Vos Defis a Transcender")
        y -= 1*cm
        for d in signe.get('defis', []):
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 11)
            c.drawCentredString(self.width / 2, y, f"- {d}")
            y -= 0.5*cm

        # Affirmation
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
        moon_data = next((p for p in planets_data if p.get('name') == 'Moon'), None) if planets_data else None
        moon_sign = moon_data.get('sign', 'Cancer') if moon_data else 'Cancer'
        moon_info = SIGNES_DETAILS.get(moon_sign, {})
        moon_fr = moon_info.get('nom_fr', moon_sign)

        y = self._chapter_header(c, f"Votre Lune en {moon_fr}", "Votre monde emotionnel interieur")

        moon_intro = "La Lune en astrologie represente votre monde interieur : vos emotions, vos instincts, vos besoins de securite. Si le Soleil est ce que vous montrez au monde, la Lune est ce que vous ressentez dans l'intimite. Elle revele la facon dont vous avez ete nourri(e) emotionnellement dans l'enfance et ce dont vous avez besoin pour vous sentir en securite aujourd'hui. Comprendre votre Lune, c'est comprendre les racines de vos reactions emotionnelles."
        y = self._draw_centered_block(c, moon_intro, y, font_size=10, color=LIGHT_TEXT)

        # Crystal priestess illustration for Moon
        illust = self._get_illustration(6)  # crystal priestess
        if illust:
            y = self._draw_image_safe(c, illust, y, w=7*cm, h=7*cm)

        img = self._get_zodiac_image(moon_sign)
        if img:
            y = self._draw_image_safe(c, img, y, w=5*cm, h=5*cm)

        if moon_data:
            c.setFillColor(MEDIUM_PURPLE)
            c.setFillAlpha(0.5)
            c.roundRect(self.margin, y - 1*cm, self.width - 2*self.margin, 1*cm, 5, fill=1)
            c.setFillAlpha(1.0)
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(self.width/2, y - 0.7*cm, f"Lune en {moon_fr} - Maison {moon_data.get('house','?')}")
            y -= 1.8*cm

        lune_info = PLANETES_DETAILS.get('Moon', {})
        en_signe = lune_info.get('en_signe', {}).get(moon_sign, '')
        if en_signe:
            y = self._draw_centered_block(c, en_signe, y, font_size=10.5, color=LIGHT_TEXT)

        element = moon_info.get('element', 'Terre')
        needs = {"Feu": "action et passion", "Terre": "securite et stabilite", "Air": "communication et echanges", "Eau": "connexion emotionnelle et intimite"}
        txt = f"Avec une Lune en signe de {element}, vos emotions ont besoin de {needs.get(element, 'harmonie')} pour s'epanouir. Vous percevez le monde a travers le filtre de cet element, ce qui influence profondement vos reactions instinctives et vos besoins fondamentaux."
        y = self._draw_centered_block(c, txt, y, font_size=10.5)

    def _page_ascendant(self, c, planets_data):
        self._new_page(c)
        asc_data = next((p for p in planets_data if p.get('name') == 'Ascendant'), None) if planets_data else None
        asc_sign = asc_data.get('sign', 'Leo') if asc_data else 'Leo'
        asc_info = SIGNES_DETAILS.get(asc_sign, {})
        asc_fr = asc_info.get('nom_fr', asc_sign)

        y = self._chapter_header(c, f"Ascendant {asc_fr}", "Votre masque social")

        asc_intro = "L'Ascendant est le signe qui se levait a l'horizon Est au moment precis de votre naissance. Il represente la premiere impression que vous donnez aux autres, votre apparence physique, et la maniere dont vous abordez spontanement les nouvelles situations. Si le Soleil est votre essence et la Lune votre vie interieure, l'Ascendant est la porte d'entree par laquelle le monde vous decouvre."
        y = self._draw_centered_block(c, asc_intro, y, font_size=10, color=LIGHT_TEXT)

        # Illustration
        illust = self._get_illustration(1)  # birds
        if illust:
            y = self._draw_image_safe(c, illust, y, w=7*cm, h=7*cm)

        desc = f"Avec un Ascendant en {asc_fr}, vous degagez naturellement l'energie de ce signe. {asc_info.get('description_courte', '')} Les gens vous percoivent d'abord a travers cette lentille avant de decouvrir votre Soleil. L'element {asc_info.get('element', '')} colore votre approche de la vie quotidienne."
        y = self._draw_centered_block(c, desc, y, font_size=10.5)

        # Traits
        y -= 0.3*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(self.width / 2, y, "Traits visibles de votre Ascendant")
        y -= 0.8*cm
        for f in asc_info.get('forces', [])[:5]:
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 10)
            c.drawCentredString(self.width / 2, y, f"- {f}")
            y -= 0.45*cm

    def _page_planets(self, c, planets_data):
        self._new_page(c)
        y = self._chapter_header(c, "Les Planetes de Votre Theme", "Les forces qui vous animent")

        planet_intro = "Chaque planete de votre theme natal represente une facette de votre personnalite. Mercure gouverne votre intellect, Venus votre facon d'aimer, Mars votre energie d'action, Jupiter votre expansion et Saturne votre structure. Voici ce que revelent leurs positions dans votre carte du ciel."
        y = self._draw_centered_block(c, planet_intro, y, font_size=10, color=LIGHT_TEXT)
        y -= 0.3*cm

        main_planets = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        for pname in main_planets:
            planet = next((p for p in planets_data if p.get('name') == pname), None) if planets_data else None
            if not planet:
                continue
            if y < 5*cm:
                self._new_page(c)
                y = self.height - 3.5*cm

            pinfo = PLANETES_DETAILS.get(pname, {})
            pfr = pinfo.get('nom_fr', pname)
            sym = pinfo.get('symbole', '')
            sign_fr = self._get_french_sign(planet.get('sign', ''))
            house = planet.get('house', '?')

            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(self.width / 2, y, f"{sym} {pfr} en {sign_fr} - Maison {house}")
            y -= 0.7*cm

            desc = pinfo.get('description', '')
            y = self._draw_centered_block(c, desc, y, font_size=10, color=LIGHT_TEXT)
            y -= 0.3*cm

    def _page_houses(self, c):
        self._new_page(c)
        y = self._chapter_header(c, "Les Maisons Astrologiques", "Les 12 domaines de votre vie")

        # Illustration
        illust = self._get_illustration(2)  # koi
        if illust:
            y = self._draw_image_safe(c, illust, y, w=7*cm, h=7*cm)

        y = self._draw_centered_block(c, WHAT_ARE_HOUSES, y, font_size=10, color=LIGHT_TEXT)

    def _page_life_path(self, c, chemin_vie, annee_perso):
        self._new_page(c)
        chemin_info = CHEMINS_VIE.get(chemin_vie, CHEMINS_VIE.get(9, {}))

        y = self._chapter_header(c, f"Chemin de Vie {chemin_vie}", f"{chemin_info.get('titre', 'Le Voyageur')}")

        path_intro = f"En numerologie, votre Chemin de Vie est le nombre le plus important de votre profil. Il se calcule a partir de votre date de naissance complete et revele la grande direction de votre existence. Votre Chemin de Vie {chemin_vie} indique que votre mission d'ame est centree sur le theme suivant :"
        y = self._draw_centered_block(c, path_intro, y, font_size=10.5, color=LIGHT_TEXT)

        # Keyword box
        c.setFillColor(MEDIUM_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(3*cm, y - 1.2*cm, self.width - 6*cm, 1.2*cm, 10, fill=1)
        c.setFillAlpha(1.0)
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.width / 2, y - 0.8*cm, f"Mot-cle : {chemin_info.get('mot_cle', 'Evolution')}")
        y -= 2.2*cm

        # Mission
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(self.width / 2, y, "Votre Mission d'Ame")
        y -= 0.8*cm
        mission = chemin_info.get('mission', '')
        y = self._draw_centered_block(c, mission, y, font_size=10.5)

        # Forces
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(self.width / 2, y, "Vos Dons Naturels")
        y -= 0.8*cm
        for f in chemin_info.get('forces', []):
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 11)
            c.drawCentredString(self.width / 2, y, f"- {f}")
            y -= 0.5*cm

        y -= 0.5*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(self.width / 2, y, "Defis a Transcender")
        y -= 0.8*cm
        for d in chemin_info.get('defis', []):
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 11)
            c.drawCentredString(self.width / 2, y, f"- {d}")
            y -= 0.5*cm

        # REAL concrete advice page
        self._new_page(c)
        y = self._chapter_header(c, "Conseils Concrets", f"Pour votre Chemin de Vie {chemin_vie} et votre Annee {annee_perso}")

        annee_info = PREVISIONS_ANNEE_PERSONNELLE.get(annee_perso, PREVISIONS_ANNEE_PERSONNELLE.get(1, {}))

        conseil_chemin = chemin_info.get('conseil', '')
        conseil_annee = annee_info.get('conseil_cle', '')
        theme_annee = annee_info.get('theme', 'Evolution')

        real_advice = f"""Votre Chemin de Vie {chemin_vie} vous invite a incarner pleinement le theme de {chemin_info.get('mot_cle', 'evolution').lower()}. Concretement, cela signifie que les situations qui vous font le plus grandir sont celles ou vous exercez cette qualite. Ne fuyez pas ces occasions : ce sont vos rendez-vous avec votre destinee.

Conseil pour votre chemin : {conseil_chemin}

Votre annee personnelle 2026 est une annee {annee_perso}, dont le theme est : {theme_annee}. Cela signifie que l'energie dominante de cette annee vous pousse vers ce domaine. Combiner votre chemin de vie avec votre annee personnelle donne une orientation tres precise :

{conseil_annee}

Voici des actions concretes pour honorer cette double influence :

1. Chaque matin, prenez 5 minutes pour vous aligner avec l'intention de votre chemin de vie. Demandez-vous : comment puis-je exprimer mon don de {chemin_info.get('mot_cle', 'evolution').lower()} aujourd'hui ?

2. Cette annee, concentrez-vous particulierement sur le domaine de {theme_annee.lower()}. C'est la ou l'univers place ses ressources pour vous.

3. Notez dans un journal les synchronicites et les signes que vous recevez. Votre chemin de vie {chemin_vie} est particulierement receptif aux messages subtils de l'univers.

4. Si vous ressentez de la resistance, c'est souvent le signe que vous approchez d'une percee importante. Vos defis sont vos meilleurs professeurs.

5. Entourez-vous de personnes qui resonent avec vos valeurs profondes. La qualite de vos relations amplifie ou diminue l'energie de votre chemin."""

        y = self._draw_centered_block(c, real_advice, y, font_size=10, color=LIGHT_TEXT)

        # Colors and stones
        if y > 3*cm:
            y -= 0.5*cm
            c.setFillColor(GOLD)
            c.setFont("Helvetica", 10)
            c.drawCentredString(self.width / 2, y, f"Couleurs : {chemin_info.get('couleur', 'Or')} | Pierres : {chemin_info.get('pierre', 'Cristal')}")

    def _page_previsions(self, c, annee_perso):
        self._new_page(c)
        annee_info = PREVISIONS_ANNEE_PERSONNELLE.get(annee_perso, PREVISIONS_ANNEE_PERSONNELLE.get(1, {}))

        y = self._chapter_header(c, f"Previsions 2026", f"Annee Personnelle {annee_perso} : {annee_info.get('theme', 'Evolution')}")

        resume = annee_info.get('resume', '')
        y = self._draw_centered_block(c, resume, y, font_size=11, color=CREAM)

        # Domains
        domaines = annee_info.get('domaines', {})
        labels = {'carriere': 'Carriere & Travail', 'amour': 'Amour & Relations', 'sante': 'Sante & Bien-etre', 'finances': 'Finances', 'spirituel': 'Spiritualite'}
        for dom, txt in domaines.items():
            if y < 4*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(self.width / 2, y, labels.get(dom, dom))
            y -= 0.7*cm
            y = self._draw_centered_block(c, txt, y, font_size=10)

        # Strong months
        self._new_page(c)
        y = self.height - 4*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.width / 2, y, "Conseil Cle pour 2026")
        y -= 1.2*cm
        conseil = annee_info.get('conseil_cle', '')
        y = self._draw_centered_block(c, conseil, y, font_size=11, color=CREAM)

        mois = ['Janvier','Fevrier','Mars','Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Decembre']
        mois_forts = annee_info.get('mois_forts', [])
        y -= 0.5*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(self.width / 2, y, "Mois les plus favorables :")
        y -= 0.7*cm
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 11)
        c.drawCentredString(self.width / 2, y, ", ".join([mois[m-1] for m in mois_forts if m <= 12]))

    def _page_5_year(self, c, annee_perso_base):
        self._new_page(c)
        y = self._chapter_header(c, "Vision sur 5 Ans", "2026 - 2030 : Votre trajectoire cosmique")

        intro = "Les cinq prochaines annees forment un chapitre important de votre vie. Chaque annee apporte ses propres energies et opportunites, suivant le cycle naturel de la numerologie. Voici un apercu de ce qui vous attend."
        y = self._draw_centered_block(c, intro, y, font_size=10.5)
        y -= 0.3*cm

        for off in range(5):
            if y < 4*cm:
                self._new_page(c)
                y = self.height - 3.5*cm
            year = 2026 + off
            ap = ((annee_perso_base - 1 + off) % 9) + 1
            ai = PREVISIONS_ANNEE_PERSONNELLE.get(ap, {})
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(self.width / 2, y, f"{year} - Annee {ap} : {ai.get('theme', 'Evolution')}")
            y -= 0.7*cm
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
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(self.width / 2, y, f"{pos} : {card.get('nom', '')}")
            y -= 0.5*cm
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

        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(self.width / 2, y, f"Pour votre signe {signe.get('nom_fr', '')} :")
        y -= 0.7*cm
        y = self._draw_centered_block(c, signe.get('conseil_annee', ''), y, font_size=10.5)

        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(self.width / 2, y, f"Pour votre Chemin de Vie {chemin_vie} :")
        y -= 0.7*cm
        y = self._draw_centered_block(c, chemin.get('conseil', ''), y, font_size=10.5)

        y -= 0.5*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(self.width / 2, y, "Trois Cles pour Votre Evolution :")
        y -= 0.8*cm
        cles = [
            "Honorez votre unicite. Votre combinaison astrologique est unique dans tout l'univers. Cessez de vous comparer aux autres et embrassez pleinement ce qui fait votre singularite.",
            "Ecoutez votre intuition. Votre Lune vous parle constamment a travers vos emotions et vos reves. Faites-lui confiance, meme quand la logique dit le contraire.",
            "Agissez avec conscience. Utilisez les informations de ce manuscrit comme un guide, pas comme un destin fige. Vous restez toujours le createur de votre realite."
        ]
        for cle in cles:
            y = self._draw_centered_block(c, cle, y, font_size=10, color=LIGHT_TEXT)

    def _page_final(self, c, user_data):
        self._new_page(c)

        illust = self._get_illustration(3)  # landscape
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

    # ============= MAIN =============

    def generate(self, user_data, planets_data=None, horoscope_data=None):
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

        self._page_cover(c, user_data, zodiac_sign)
        self._page_sommaire(c)
        self._page_introduction(c)
        self._page_natal_chart(c, planets_data, zodiac_sign)
        self._page_sun(c, planets_data, zodiac_sign)
        self._page_moon(c, planets_data)
        self._page_ascendant(c, planets_data)
        self._page_planets(c, planets_data)
        self._page_houses(c)
        self._page_life_path(c, chemin_vie, annee_perso)
        self._page_previsions(c, annee_perso)
        self._page_5_year(c, annee_perso)
        self._page_tarot(c)
        self._page_conseils(c, zodiac_sign, chemin_vie)
        self._page_final(c, user_data)

        c.save()
        buffer.seek(0)
        return buffer.getvalue()

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


def generate_manuscrit_complet(user_data, planets_data=None, horoscope_data=None):
    gen = ManuscritCompletGenerator()
    return gen.generate(user_data, planets_data, horoscope_data)
