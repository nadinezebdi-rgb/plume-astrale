"""
Générateur PDF Manuscrit Complet
Version enrichie avec contenu astrologique détaillé
"""
import io
import os
import random
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import logging

from services.astro_content import (
    SIGNES_DETAILS, PLANETES_DETAILS, MAISONS_DETAILS,
    CHEMINS_VIE, PREVISIONS_ANNEE_PERSONNELLE, ARCANES_MAJEURS
)

logger = logging.getLogger(__name__)

# Colors
GOLD = HexColor('#C5A059')
DARK_PURPLE = HexColor('#0F0518')
LIGHT_PURPLE = HexColor('#1A0B2E')
CREAM = HexColor('#F3E5AB')
LIGHT_TEXT = HexColor('#E0D9F6')
MEDIUM_PURPLE = HexColor('#2D1B4E')

class ManuscritCompletGenerator:
    """Generate complete PDF manuscripts with rich astrological content"""
    
    def __init__(self):
        self.width, self.height = A4
        self.margin = 2 * cm
        self.page_num = 0
        
    def _get_french_sign(self, sign):
        """Convert English sign to French"""
        return SIGNES_DETAILS.get(sign, {}).get('nom_fr', sign)
    
    def _draw_background(self, c, variant=0):
        """Draw mystical background with stars"""
        c.setFillColor(DARK_PURPLE)
        c.rect(0, 0, self.width, self.height, fill=1)
        
        # Subtle gradient effect at top
        c.setFillColor(LIGHT_PURPLE)
        c.setFillAlpha(0.3)
        for i in range(10):
            c.rect(0, self.height - (i+1)*cm, self.width, cm, fill=1)
        c.setFillAlpha(1.0)
        
        # Stars
        random.seed(self.page_num * 100 + variant)
        c.setFillColor(HexColor('#FFFFFF'))
        for _ in range(40):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            size = random.uniform(0.2, 1.0)
            alpha = random.uniform(0.1, 0.4)
            c.setFillAlpha(alpha)
            c.circle(x, y, size, fill=1)
        c.setFillAlpha(1.0)
    
    def _draw_border(self, c):
        """Draw decorative border"""
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.3)
        c.setLineWidth(0.5)
        c.rect(1.5*cm, 1.5*cm, self.width - 3*cm, self.height - 3*cm)
        c.setStrokeAlpha(1.0)
    
    def _draw_page_number(self, c):
        """Draw page number"""
        c.setFillColor(GOLD)
        c.setFillAlpha(0.5)
        c.setFont("Helvetica", 10)
        c.drawCentredString(self.width / 2, 1.2*cm, f"— {self.page_num} —")
        c.setFillAlpha(1.0)
    
    def _draw_chapter_header(self, c, title, subtitle="", y=None):
        """Draw chapter header"""
        if y is None:
            y = self.height - 4*cm
        
        # Decorative line above
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.line(4*cm, y + 0.5*cm, self.width - 4*cm, y + 0.5*cm)
        
        # Title
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(self.width / 2, y, title)
        
        if subtitle:
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Oblique", 12)
            c.drawCentredString(self.width / 2, y - 0.8*cm, subtitle)
            y -= 0.8*cm
        
        # Decorative line below
        c.line(4*cm, y - 0.5*cm, self.width - 4*cm, y - 0.5*cm)
        
        return y - 1.5*cm
    
    def _wrap_text(self, c, text, max_width, font_name="Helvetica", font_size=11):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, font_name, font_size) < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _draw_text_block(self, c, text, y, font_size=11, color=LIGHT_TEXT, indent=0):
        """Draw wrapped text block"""
        c.setFillColor(color)
        c.setFont("Helvetica", font_size)
        
        max_width = self.width - 2*self.margin - indent
        lines = self._wrap_text(c, text, max_width, "Helvetica", font_size)
        
        line_height = font_size * 1.4 / 28.35  # Convert points to cm
        
        for line in lines:
            if y < 3*cm:
                break
            c.drawString(self.margin + indent, y, line)
            y -= line_height * cm
        
        return y - 0.3*cm
    
    def _draw_image_placeholder(self, c, y, width, height, label=""):
        """Draw placeholder for future image"""
        x = (self.width - width) / 2
        
        c.setFillColor(MEDIUM_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(x, y - height, width, height, 10, fill=1)
        c.setFillAlpha(1.0)
        
        # Border
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.3)
        c.roundRect(x, y - height, width, height, 10)
        c.setStrokeAlpha(1.0)
        
        # Label
        if label:
            c.setFillColor(GOLD)
            c.setFillAlpha(0.5)
            c.setFont("Helvetica-Oblique", 10)
            c.drawCentredString(self.width / 2, y - height/2, label)
            c.setFillAlpha(1.0)
        
        return y - height - 1*cm
    
    def _new_page(self, c):
        """Start a new page"""
        c.showPage()
        self.page_num += 1
        self._draw_background(c)
        self._draw_border(c)
        self._draw_page_number(c)
    
    # ============= PAGE GENERATORS =============
    
    def _page_title(self, c, user_data, zodiac_sign):
        """Page 1: Title page"""
        self.page_num = 1
        self._draw_background(c, 0)
        
        # Decorative elements
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        y_top = self.height - 5*cm
        c.line(3*cm, y_top, self.width - 3*cm, y_top)
        
        # Subtitle
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 11)
        c.drawCentredString(self.width / 2, self.height - 6*cm, "✦  VOTRE MANUSCRIT CÉLESTE PERSONNEL  ✦")
        
        # Main title
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 42)
        c.drawCentredString(self.width / 2, self.height - 9*cm, "Le Manuscrit")
        c.setFont("Helvetica-Bold", 38)
        c.drawCentredString(self.width / 2, self.height - 10.8*cm, "de la Plume")
        
        # User name
        prenom = user_data.get('prenom', 'Voyageur Céleste')
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Oblique", 20)
        c.drawCentredString(self.width / 2, self.height - 13.5*cm, f"Créé pour {prenom}")
        
        # Zodiac info box
        signe_info = SIGNES_DETAILS.get(zodiac_sign, {})
        signe_fr = signe_info.get('nom_fr', zodiac_sign)
        symbole = signe_info.get('symbole', '★')
        
        c.setFillColor(MEDIUM_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(4*cm, self.height - 17.5*cm, self.width - 8*cm, 2.5*cm, 10, fill=1)
        c.setFillAlpha(1.0)
        
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(self.width / 2, self.height - 15.8*cm, f"{symbole}  Signe Solaire : {signe_fr}  {symbole}")
        
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 11)
        date_naissance = user_data.get('dateNaissance', '')
        heure = user_data.get('heureNaissance', '')
        ville = user_data.get('ville', '')
        c.drawCentredString(self.width / 2, self.height - 16.8*cm, f"Né(e) le {date_naissance} à {heure} • {ville}")
        
        # Quote
        c.setFillColor(CREAM)
        c.setFillAlpha(0.8)
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(self.width / 2, self.height - 20*cm, "« Les étoiles inclinent, mais ne déterminent pas. »")
        c.setFillAlpha(1.0)
        
        # Bottom decorative line
        c.setStrokeColor(GOLD)
        c.line(3*cm, 4*cm, self.width - 3*cm, 4*cm)
        
        # Footer
        c.setFillColor(GOLD)
        c.setFillAlpha(0.5)
        c.setFont("Helvetica", 9)
        c.drawCentredString(self.width / 2, 2.5*cm, f"Généré le {datetime.now().strftime('%d/%m/%Y')} • Plume Astrale © 2026")
        c.setFillAlpha(1.0)
    
    def _page_sommaire(self, c):
        """Page 2: Table of contents"""
        self._new_page(c)
        
        y = self._draw_chapter_header(c, "Sommaire", "Votre voyage à travers les étoiles")
        y -= 1*cm
        
        chapters = [
            ("I", "Votre Identité Céleste", "Soleil, Lune & Ascendant"),
            ("II", "Les Planètes de Votre Thème", "Positions & Influences"),
            ("III", "Votre Chemin d'Âme", "Numérologie & Mission de Vie"),
            ("IV", "Prévisions 2026", "Votre Année Personnelle"),
            ("V", "Vision sur 5 Ans", "2026-2030"),
            ("VI", "Le Tirage du Tarot", "Messages pour votre chemin"),
            ("VII", "Conseils de la Plume", "Guidance personnalisée"),
        ]
        
        c.setFont("Helvetica", 12)
        for num, title, subtitle in chapters:
            c.setFillColor(GOLD)
            c.drawString(self.margin + 0.5*cm, y, num)
            
            c.setFillColor(CREAM)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(self.margin + 1.5*cm, y, title)
            
            c.setFillColor(LIGHT_TEXT)
            c.setFillAlpha(0.7)
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(self.margin + 1.5*cm, y - 0.5*cm, subtitle)
            c.setFillAlpha(1.0)
            
            y -= 1.5*cm
        
        # Decorative note at bottom
        y -= 1*cm
        c.setFillColor(GOLD)
        c.setFillAlpha(0.5)
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(self.width / 2, y, "✦ Ce manuscrit a été créé spécialement pour vous ✦")
        c.setFillAlpha(1.0)
    
    def _page_soleil(self, c, planets_data, zodiac_sign):
        """Pages 3-4: Sun section"""
        self._new_page(c)
        
        signe_info = SIGNES_DETAILS.get(zodiac_sign, {})
        signe_fr = signe_info.get('nom_fr', zodiac_sign)
        symbole = signe_info.get('symbole', '☉')
        
        y = self._draw_chapter_header(c, f"Votre Soleil en {signe_fr}", f"{symbole} L'essence de qui vous êtes")
        y -= 0.5*cm
        
        # Planet data box
        sun_data = next((p for p in planets_data if p.get('name') == 'Sun'), None) if planets_data else None
        if sun_data:
            c.setFillColor(MEDIUM_PURPLE)
            c.setFillAlpha(0.5)
            c.roundRect(self.margin, y - 1.2*cm, self.width - 2*self.margin, 1.2*cm, 5, fill=1)
            c.setFillAlpha(1.0)
            
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(self.margin + 0.5*cm, y - 0.8*cm, f"Position : {signe_fr} • Maison {sun_data.get('house', 'N/A')}")
            
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 10)
            c.drawRightString(self.width - self.margin - 0.5*cm, y - 0.8*cm, f"Degré : {sun_data.get('normDegree', 0):.1f}°")
            
            y -= 2*cm
        
        # Image placeholder for zodiac sign
        y = self._draw_image_placeholder(c, y, 6*cm, 6*cm, f"Illustration {signe_fr}")
        
        # Description
        y -= 0.5*cm
        description = signe_info.get('description_longue', '')
        y = self._draw_text_block(c, description, y)
        
        # Continue on next page if needed
        self._new_page(c)
        y = self.height - 4*cm
        
        # Forces et défis
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, y, "✦ Vos Forces Solaires")
        y -= 0.8*cm
        
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 11)
        forces = signe_info.get('forces', [])
        for force in forces:
            c.drawString(self.margin + 0.5*cm, y, f"• {force}")
            y -= 0.5*cm
        
        y -= 0.5*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, y, "✦ Vos Défis à Transcender")
        y -= 0.8*cm
        
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 11)
        defis = signe_info.get('defis', [])
        for defi in defis:
            c.drawString(self.margin + 0.5*cm, y, f"• {defi}")
            y -= 0.5*cm
        
        # Affirmation
        y -= 1*cm
        c.setFillColor(MEDIUM_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(self.margin, y - 2*cm, self.width - 2*self.margin, 2*cm, 10, fill=1)
        c.setFillAlpha(1.0)
        
        c.setFillColor(CREAM)
        c.setFont("Helvetica-BoldOblique", 12)
        affirmation = signe_info.get('affirmation', '')
        c.drawCentredString(self.width / 2, y - 1.2*cm, f"« {affirmation} »")
    
    def _page_lune(self, c, planets_data):
        """Page 5: Moon section"""
        self._new_page(c)
        
        moon_data = next((p for p in planets_data if p.get('name') == 'Moon'), None) if planets_data else None
        moon_sign = moon_data.get('sign', 'Cancer') if moon_data else 'Cancer'
        moon_info = SIGNES_DETAILS.get(moon_sign, {})
        moon_fr = moon_info.get('nom_fr', moon_sign)
        
        y = self._draw_chapter_header(c, f"Votre Lune en {moon_fr}", "☽ Votre monde émotionnel")
        y -= 0.5*cm
        
        # Planet data box
        if moon_data:
            c.setFillColor(MEDIUM_PURPLE)
            c.setFillAlpha(0.5)
            c.roundRect(self.margin, y - 1.2*cm, self.width - 2*self.margin, 1.2*cm, 5, fill=1)
            c.setFillAlpha(1.0)
            
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(self.margin + 0.5*cm, y - 0.8*cm, f"Position : {moon_fr} • Maison {moon_data.get('house', 'N/A')}")
            
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 10)
            c.drawRightString(self.width - self.margin - 0.5*cm, y - 0.8*cm, f"Degré : {moon_data.get('normDegree', 0):.1f}°")
            
            y -= 2*cm
        
        # Description from PLANETES_DETAILS
        lune_info = PLANETES_DETAILS.get('Moon', {})
        description = lune_info.get('description', '')
        y = self._draw_text_block(c, description, y)
        
        y -= 0.5*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, y, f"✦ La Lune en {moon_fr}")
        y -= 0.8*cm
        
        # Sign-specific interpretation
        en_signe = lune_info.get('en_signe', {}).get(moon_sign, '')
        if en_signe:
            y = self._draw_text_block(c, en_signe, y)
        
        # Emotional needs
        y -= 0.5*cm
        element = moon_info.get('element', 'Terre')
        emotional_text = f"Avec une Lune en signe de {element}, vos émotions ont besoin de {self._get_element_need(element)} pour s'épanouir. Vous percevez le monde à travers le filtre de cet élément, ce qui influence profondément vos réactions instinctives et vos besoins fondamentaux."
        y = self._draw_text_block(c, emotional_text, y)
    
    def _get_element_need(self, element):
        """Get emotional need based on element"""
        needs = {
            "Feu": "action et passion",
            "Terre": "sécurité et stabilité",
            "Air": "communication et échanges",
            "Eau": "connexion émotionnelle et intimité"
        }
        return needs.get(element, "harmonie")
    
    def _page_ascendant(self, c, planets_data):
        """Page 6: Ascendant section"""
        self._new_page(c)
        
        asc_data = next((p for p in planets_data if p.get('name') == 'Ascendant'), None) if planets_data else None
        asc_sign = asc_data.get('sign', 'Leo') if asc_data else 'Leo'
        asc_info = SIGNES_DETAILS.get(asc_sign, {})
        asc_fr = asc_info.get('nom_fr', asc_sign)
        
        y = self._draw_chapter_header(c, f"Ascendant {asc_fr}", "★ Votre masque social")
        y -= 0.5*cm
        
        if asc_data:
            c.setFillColor(MEDIUM_PURPLE)
            c.setFillAlpha(0.5)
            c.roundRect(self.margin, y - 1.2*cm, self.width - 2*self.margin, 1.2*cm, 5, fill=1)
            c.setFillAlpha(1.0)
            
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 11)
            element = asc_info.get('element', 'Feu')
            c.drawString(self.margin + 0.5*cm, y - 0.8*cm, f"Élément : {element} • Maison I")
            
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 10)
            c.drawRightString(self.width - self.margin - 0.5*cm, y - 0.8*cm, f"Degré : {asc_data.get('normDegree', 0):.1f}°")
            
            y -= 2*cm
        
        # Ascendant description
        asc_text = f"""Votre Ascendant en {asc_fr} est la façon dont le monde vous perçoit au premier abord. 
C'est votre masque social, votre personnalité apparente, et la manière dont vous abordez naturellement les nouvelles situations.

{asc_info.get('description_courte', '')}

L'Ascendant colore toute votre personnalité visible. Même si votre Soleil représente votre essence profonde, 
c'est à travers le filtre de l'Ascendant que cette essence s'exprime dans le monde."""
        
        y = self._draw_text_block(c, asc_text, y)
        
        # Traits
        y -= 0.5*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(self.margin, y, "✦ Traits caractéristiques")
        y -= 0.8*cm
        
        forces = asc_info.get('forces', [])[:4]
        for force in forces:
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 11)
            c.drawString(self.margin + 0.5*cm, y, f"• {force}")
            y -= 0.5*cm
    
    def _page_planetes(self, c, planets_data):
        """Pages 7-8: All planets overview"""
        self._new_page(c)
        
        y = self._draw_chapter_header(c, "Les Planètes de Votre Thème", "Positions & Influences")
        y -= 0.5*cm
        
        if not planets_data:
            y = self._draw_text_block(c, "Les positions planétaires n'ont pas pu être calculées.", y)
            return
        
        # Filter main planets
        main_planets = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        
        for planet_name in main_planets:
            planet = next((p for p in planets_data if p.get('name') == planet_name), None)
            if not planet:
                continue
            
            if y < 5*cm:
                self._new_page(c)
                y = self.height - 4*cm
            
            planet_info = PLANETES_DETAILS.get(planet_name, {})
            planet_fr = planet_info.get('nom_fr', planet_name)
            symbole = planet_info.get('symbole', '★')
            sign = planet.get('sign', '')
            sign_fr = self._get_french_sign(sign)
            house = planet.get('house', '')
            
            # Planet header
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(self.margin, y, f"{symbole} {planet_fr} en {sign_fr}")
            
            c.setFillColor(LIGHT_TEXT)
            c.setFillAlpha(0.7)
            c.setFont("Helvetica", 10)
            c.drawRightString(self.width - self.margin, y, f"Maison {house}")
            c.setFillAlpha(1.0)
            
            y -= 0.6*cm
            
            # Planet description
            description = planet_info.get('description', '')
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 10)
            lines = self._wrap_text(c, description, self.width - 2*self.margin - 1*cm, "Helvetica", 10)
            for line in lines[:2]:
                c.drawString(self.margin + 0.3*cm, y, line)
                y -= 0.4*cm
            
            y -= 0.8*cm
    
    def _page_chemin_ame(self, c, chemin_vie, annee_perso):
        """Pages 9-10: Soul path / Life path"""
        self._new_page(c)
        
        chemin_info = CHEMINS_VIE.get(chemin_vie, CHEMINS_VIE.get(9, {}))
        
        y = self._draw_chapter_header(c, f"Chemin de Vie {chemin_vie}", f"✦ {chemin_info.get('titre', 'Le Voyageur')}")
        y -= 0.5*cm
        
        # Keyword box
        c.setFillColor(MEDIUM_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(self.margin, y - 1.5*cm, self.width - 2*self.margin, 1.5*cm, 10, fill=1)
        c.setFillAlpha(1.0)
        
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.width / 2, y - 1*cm, f"Mot-clé : {chemin_info.get('mot_cle', 'Évolution')}")
        y -= 2.5*cm
        
        # Mission
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(self.margin, y, "✦ Votre Mission d'Âme")
        y -= 0.8*cm
        
        mission = chemin_info.get('mission', '')
        y = self._draw_text_block(c, mission, y)
        
        # Forces
        y -= 0.5*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(self.margin, y, "✦ Vos Dons Naturels")
        y -= 0.8*cm
        
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 11)
        forces = chemin_info.get('forces', [])
        for force in forces:
            c.drawString(self.margin + 0.5*cm, y, f"• {force}")
            y -= 0.5*cm
        
        # Challenges
        y -= 0.5*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(self.margin, y, "✦ Défis à Transcender")
        y -= 0.8*cm
        
        c.setFillColor(LIGHT_TEXT)
        defis = chemin_info.get('defis', [])
        for defi in defis:
            c.drawString(self.margin + 0.5*cm, y, f"• {defi}")
            y -= 0.5*cm
        
        # Conseil
        y -= 0.5*cm
        conseil = chemin_info.get('conseil', '')
        c.setFillColor(CREAM)
        c.setFont("Helvetica-BoldOblique", 11)
        c.drawCentredString(self.width / 2, y, f"Conseil : « {conseil} »")
        
        # Colors and stones
        y -= 1.5*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, y, f"Couleurs : {chemin_info.get('couleur', 'Or')}")
        c.drawRightString(self.width - self.margin, y, f"Pierres : {chemin_info.get('pierre', 'Cristal')}")
    
    def _page_previsions_annee(self, c, annee_perso):
        """Pages 11-12: Year predictions"""
        self._new_page(c)
        
        annee_info = PREVISIONS_ANNEE_PERSONNELLE.get(annee_perso, PREVISIONS_ANNEE_PERSONNELLE.get(1, {}))
        
        y = self._draw_chapter_header(c, f"Année Personnelle {annee_perso}", f"2026 : {annee_info.get('theme', 'Évolution')}")
        y -= 0.5*cm
        
        # Summary
        resume = annee_info.get('resume', '')
        y = self._draw_text_block(c, resume, y, font_size=12, color=CREAM)
        
        y -= 0.5*cm
        
        # Domains
        domaines = annee_info.get('domaines', {})
        for domaine, texte in domaines.items():
            if y < 4*cm:
                self._new_page(c)
                y = self.height - 4*cm
            
            domaine_titre = {
                'carriere': '💼 Carrière & Travail',
                'amour': '❤️ Amour & Relations',
                'sante': '🌿 Santé & Bien-être',
                'finances': '💰 Finances',
                'spirituel': '✨ Spiritualité'
            }.get(domaine, domaine)
            
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(self.margin, y, domaine_titre)
            y -= 0.7*cm
            
            y = self._draw_text_block(c, texte, y, font_size=10)
            y -= 0.3*cm
        
        # Key advice
        self._new_page(c)
        y = self.height - 4*cm
        
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.width / 2, y, "✦ Conseil Clé pour 2026 ✦")
        y -= 1.5*cm
        
        conseil = annee_info.get('conseil_cle', '')
        c.setFillColor(CREAM)
        c.setFont("Helvetica-BoldOblique", 13)
        lines = self._wrap_text(c, conseil, self.width - 4*self.margin, "Helvetica-BoldOblique", 13)
        for line in lines:
            c.drawCentredString(self.width / 2, y, line)
            y -= 0.6*cm
        
        # Strong months
        y -= 1*cm
        mois_forts = annee_info.get('mois_forts', [])
        mois_noms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(self.width / 2, y, "Mois les plus favorables :")
        y -= 0.8*cm
        
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 11)
        mois_texte = ", ".join([mois_noms[m-1] for m in mois_forts if m <= 12])
        c.drawCentredString(self.width / 2, y, mois_texte)
    
    def _page_previsions_5_ans(self, c, annee_perso_base):
        """Pages 13-14: 5 year predictions"""
        self._new_page(c)
        
        y = self._draw_chapter_header(c, "Vision sur 5 Ans", "2026 - 2030 : Votre trajectoire cosmique")
        y -= 0.5*cm
        
        intro = """Les cinq prochaines années forment un chapitre important de votre vie. 
Chaque année apporte ses propres énergies et opportunités, suivant le cycle naturel de la numérologie. 
Voici un aperçu de ce qui vous attend."""
        y = self._draw_text_block(c, intro, y)
        y -= 0.5*cm
        
        for year_offset in range(5):
            if y < 4*cm:
                self._new_page(c)
                y = self.height - 4*cm
            
            year = 2026 + year_offset
            annee_perso = ((annee_perso_base - 1 + year_offset) % 9) + 1
            annee_info = PREVISIONS_ANNEE_PERSONNELLE.get(annee_perso, {})
            
            # Year header
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(self.margin, y, f"✦ {year} - Année {annee_perso} : {annee_info.get('theme', 'Évolution')}")
            y -= 0.7*cm
            
            # Short description
            resume = annee_info.get('resume', '')[:150] + "..."
            y = self._draw_text_block(c, resume, y, font_size=10)
            y -= 0.5*cm
    
    def _page_tarot(self, c):
        """Pages 15-16: Tarot reading"""
        self._new_page(c)
        
        y = self._draw_chapter_header(c, "Le Tirage du Tarot", "✦ Messages pour votre chemin ✦")
        y -= 0.5*cm
        
        intro = """Le Tarot est un miroir de l'âme, révélant les énergies qui vous entourent 
et les potentiels qui s'offrent à vous. Voici trois cartes tirées spécialement pour vous."""
        y = self._draw_text_block(c, intro, y)
        y -= 1*cm
        
        # Draw 3 card placeholders
        card_width = 4*cm
        card_height = 6*cm
        spacing = 1.5*cm
        total_width = 3 * card_width + 2 * spacing
        start_x = (self.width - total_width) / 2
        
        positions = ["Passé", "Présent", "Futur"]
        random.seed(42)  # For consistent cards
        selected_cards = random.sample(list(ARCANES_MAJEURS.keys()), 3)
        
        for i, (pos, card_num) in enumerate(zip(positions, selected_cards)):
            x = start_x + i * (card_width + spacing)
            
            # Card placeholder
            c.setFillColor(MEDIUM_PURPLE)
            c.setFillAlpha(0.5)
            c.roundRect(x, y - card_height, card_width, card_height, 5, fill=1)
            c.setFillAlpha(1.0)
            
            c.setStrokeColor(GOLD)
            c.setStrokeAlpha(0.5)
            c.roundRect(x, y - card_height, card_width, card_height, 5)
            c.setStrokeAlpha(1.0)
            
            # Card name
            card = ARCANES_MAJEURS.get(card_num, {})
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(x + card_width/2, y - card_height/2 - 0.3*cm, card.get('nom', ''))
            
            # Position label
            c.setFillColor(CREAM)
            c.setFont("Helvetica", 10)
            c.drawCentredString(x + card_width/2, y - card_height - 0.5*cm, pos)
        
        y -= card_height + 2*cm
        
        # Card interpretations
        self._new_page(c)
        y = self.height - 4*cm
        
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.width / 2, y, "Interprétation de votre tirage")
        y -= 1.5*cm
        
        for i, (pos, card_num) in enumerate(zip(positions, selected_cards)):
            card = ARCANES_MAJEURS.get(card_num, {})
            
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(self.margin, y, f"✦ {pos} : {card.get('nom', '')}")
            y -= 0.7*cm
            
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 10)
            c.drawString(self.margin + 0.5*cm, y, f"Mot-clé : {card.get('mot_cle', '')}")
            y -= 0.5*cm
            
            message = card.get('message', '')
            y = self._draw_text_block(c, message, y, font_size=10, indent=0.5*cm)
            y -= 0.8*cm
    
    def _page_conseils(self, c, zodiac_sign, chemin_vie):
        """Page 17: Personalized advice"""
        self._new_page(c)
        
        signe_info = SIGNES_DETAILS.get(zodiac_sign, {})
        chemin_info = CHEMINS_VIE.get(chemin_vie, {})
        
        y = self._draw_chapter_header(c, "Conseils de la Plume", "Guidance personnalisée pour votre chemin")
        y -= 0.5*cm
        
        # Sign advice
        conseil_signe = signe_info.get('conseil_annee', '')
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin, y, f"✦ Pour votre signe {signe_info.get('nom_fr', '')} :")
        y -= 0.7*cm
        y = self._draw_text_block(c, conseil_signe, y)
        
        # Path advice
        y -= 0.5*cm
        conseil_chemin = chemin_info.get('conseil', '')
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin, y, f"✦ Pour votre Chemin de Vie {chemin_vie} :")
        y -= 0.7*cm
        y = self._draw_text_block(c, conseil_chemin, y)
        
        # General guidance
        y -= 1*cm
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin, y, "✦ Trois Clés pour Votre Évolution :")
        y -= 0.8*cm
        
        cles = [
            "Honorez votre unicité - Votre combinaison astrologique est unique. Ne cherchez pas à être quelqu'un d'autre.",
            "Écoutez votre intuition - Votre Lune vous parle constamment. Faites-lui confiance.",
            "Agissez avec conscience - Utilisez les informations de ce manuscrit comme guide, pas comme destin figé."
        ]
        
        for cle in cles:
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 10)
            lines = self._wrap_text(c, f"• {cle}", self.width - 2*self.margin - 1*cm, "Helvetica", 10)
            for line in lines:
                c.drawString(self.margin + 0.5*cm, y, line)
                y -= 0.4*cm
            y -= 0.3*cm
    
    def _page_final(self, c, user_data):
        """Final page: Blessing"""
        self._new_page(c)
        
        y = self.height - 6*cm
        
        # Golden ornament
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        c.line(4*cm, y + 1*cm, self.width - 4*cm, y + 1*cm)
        
        # Title
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(self.width / 2, y, "Message de la Plume Astrale")
        y -= 2*cm
        
        # Blessing
        prenom = user_data.get('prenom', 'Cher voyageur')
        
        blessing_lines = [
            f"Cher(e) {prenom},",
            "",
            "Ce manuscrit est un miroir de votre âme,",
            "un guide pour votre voyage sur Terre.",
            "",
            "Les étoiles qui brillaient à votre naissance",
            "continuent de vous accompagner chaque jour.",
            "",
            "Vous êtes unique dans tout l'univers.",
            "Personne d'autre n'a votre exact thème céleste.",
            "",
            "Puisse ce document vous rappeler",
            "la magie qui réside en vous,",
            "et vous guider vers votre plus haute expression.",
        ]
        
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 12)
        for line in blessing_lines:
            c.drawCentredString(self.width / 2, y, line)
            y -= 0.6*cm
        
        # Quote box
        y -= 1*cm
        c.setFillColor(MEDIUM_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(3*cm, y - 2*cm, self.width - 6*cm, 2*cm, 10, fill=1)
        c.setFillAlpha(1.0)
        
        c.setFillColor(CREAM)
        c.setFont("Helvetica-BoldOblique", 13)
        c.drawCentredString(self.width / 2, y - 0.8*cm, "« Que les étoiles vous guident,")
        c.drawCentredString(self.width / 2, y - 1.4*cm, "que la Plume vous éclaire. »")
        
        # Signature
        y -= 4*cm
        c.setStrokeColor(GOLD)
        c.line(5*cm, y, self.width - 5*cm, y)
        
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Oblique", 12)
        c.drawCentredString(self.width / 2, y - 1*cm, "Plume Astrale")
        c.setFillAlpha(0.6)
        c.setFont("Helvetica", 10)
        c.drawCentredString(self.width / 2, y - 1.6*cm, "www.plume-astrale.fr")
    
    # ============= MAIN GENERATOR =============
    
    def generate(self, user_data: dict, planets_data: list = None, horoscope_data: dict = None) -> bytes:
        """Generate complete manuscript PDF"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Determine zodiac sign from planets or calculation
        zodiac_sign = 'Taurus'
        if planets_data:
            sun = next((p for p in planets_data if p.get('name') == 'Sun'), None)
            if sun:
                zodiac_sign = sun.get('sign', 'Taurus')
        
        # Calculate numerology
        date_str = user_data.get('dateNaissance', '1990-01-01')
        chemin_vie = self._calculate_life_path(date_str)
        annee_perso = self._calculate_personal_year(date_str, 2026)
        
        # Generate all pages
        self._page_title(c, user_data, zodiac_sign)
        self._page_sommaire(c)
        self._page_soleil(c, planets_data, zodiac_sign)
        self._page_lune(c, planets_data)
        self._page_ascendant(c, planets_data)
        self._page_planetes(c, planets_data)
        self._page_chemin_ame(c, chemin_vie, annee_perso)
        self._page_previsions_annee(c, annee_perso)
        self._page_previsions_5_ans(c, annee_perso)
        self._page_tarot(c)
        self._page_conseils(c, zodiac_sign, chemin_vie)
        self._page_final(c, user_data)
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _calculate_life_path(self, date_str):
        """Calculate life path number"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            total = date.day + date.month + date.year
            while total > 9 and total not in [11, 22, 33]:
                total = sum(int(d) for d in str(total))
            return total
        except:
            return 1
    
    def _calculate_personal_year(self, date_str, year):
        """Calculate personal year number"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            total = date.day + date.month + year
            while total > 9:
                total = sum(int(d) for d in str(total))
            return total
        except:
            return 1


# Factory function
def generate_manuscrit_complet(user_data: dict, planets_data: list = None, horoscope_data: dict = None) -> bytes:
    """Generate complete manuscript PDF"""
    generator = ManuscritCompletGenerator()
    return generator.generate(user_data, planets_data, horoscope_data)
