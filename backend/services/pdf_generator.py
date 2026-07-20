import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
import logging

from services import library_images as libimg

logger = logging.getLogger(__name__)

# Colors — alignés sur la charte Plume Astrale unifiée (services/pdf_theme.py)
from services.pdf_theme import (
    NIGHT as DARK_PURPLE,        # #111625 (remplace #0F0518)
    NIGHT_SOFT as LIGHT_PURPLE,   # #1A2035 (remplace #1A0B2E)
    GOLD,                          # #D4AF37 (remplace #C5A059)
    CREAM,                         # #F5EEE0 (remplace #F3E5AB)
    LAVENDER as LIGHT_TEXT,        # #E3D7FF (remplace #E0D9F6)
    register_fonts, font as _theme_font,
)

class ManuscritPDFGenerator:
    """Generate beautiful PDF manuscripts"""
    
    def __init__(self):
        self.width, self.height = A4
        self.margin = 2 * cm
        
    def _draw_starfield_background(self, c, page_num):
        """Draw a subtle starfield background"""
        import random
        random.seed(page_num * 42)  # Consistent stars per page
        
        # Dark gradient background
        c.setFillColor(DARK_PURPLE)
        c.rect(0, 0, self.width, self.height, fill=1)
        
        # Add subtle purple glow at top
        c.setFillColor(LIGHT_PURPLE)
        c.rect(0, self.height - 8*cm, self.width, 8*cm, fill=1)
        
        # Draw stars
        c.setFillColor(HexColor('#FFFFFF'))
        for _ in range(50):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            size = random.uniform(0.3, 1.2)
            alpha = random.uniform(0.2, 0.6)
            c.setFillAlpha(alpha)
            c.circle(x, y, size, fill=1)
        
        c.setFillAlpha(1.0)  # Reset alpha
    
    def _draw_decorative_border(self, c):
        """Draw elegant gold border"""
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.3)
        c.setLineWidth(0.5)
        
        # Outer border
        c.rect(1.5*cm, 1.5*cm, self.width - 3*cm, self.height - 3*cm)
        
        # Inner border
        c.rect(1.7*cm, 1.7*cm, self.width - 3.4*cm, self.height - 3.4*cm)
        
        c.setStrokeAlpha(1.0)
    
    def _draw_page_number(self, c, page_num, total_pages):
        """Draw page number at bottom"""
        c.setFillColor(GOLD)
        c.setFillAlpha(0.5)
        c.setFont("Helvetica", 10)
        c.drawCentredString(self.width / 2, 1.2*cm, f"— {page_num} —")
        c.setFillAlpha(1.0)
    
    def _draw_lib_image(self, c, path, cx, cy, size_cm=5.0):
        """Dessine une image de la bibliothèque centrée sur (cx, cy). Silencieux si path=None."""
        if not path:
            return
        try:
            w = h = size_cm * cm
            c.drawImage(path, cx - w/2, cy - h/2, w, h, mask='auto', preserveAspectRatio=True)
        except Exception as e:
            logger.debug(f'[pdf_generator] drawImage failed: {e}')

    def _draw_title_page(self, c, user_data, zodiac_french):
        """Draw the title page"""
        self._draw_starfield_background(c, 0)
        
        # Golden decorative lines
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        y_top = self.height - 6*cm
        c.line(3*cm, y_top, self.width - 3*cm, y_top)
        c.line(3*cm, y_top - 0.3*cm, self.width - 3*cm, y_top - 0.3*cm)
        
        # Subtitle
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 12)
        c.drawCentredString(self.width / 2, self.height - 7*cm, "✦  VOTRE MANUSCRIT CÉLESTE PERSONNEL  ✦")

        # Image signe solaire (centrée entre subtitle et titre) — 2048px pour impression HD
        self._draw_lib_image(c, libimg.sign(zodiac_french, size=2048),
                             self.width/2, self.height - 10*cm, size_cm=6.0)

        # Main title (descendu sous l'image)
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(self.width / 2, self.height - 14*cm, "Le Manuscrit")
        c.drawCentredString(self.width / 2, self.height - 15.2*cm, "de la Plume")
        
        # User name
        if user_data.get('prenom'):
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Oblique", 16)
            c.drawCentredString(self.width / 2, self.height - 17*cm, f"Créé pour {user_data['prenom']}")
        
        # Zodiac sign
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 13)
        c.drawCentredString(self.width / 2, self.height - 18.3*cm, f"Signe Solaire : {zodiac_french}")
        
        # Birth data
        c.setFont("Helvetica", 10)
        c.setFillAlpha(0.7)
        birth_text = f"Né(e) le {user_data.get('dateNaissance', '')} à {user_data.get('heureNaissance', '')}"
        c.drawCentredString(self.width / 2, self.height - 19.2*cm, birth_text)
        c.drawCentredString(self.width / 2, self.height - 19.8*cm, f"{user_data.get('ville', '')}, {user_data.get('pays', '')}")
        c.setFillAlpha(1.0)
        
        # Decorative element
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.line(6*cm, self.height - 20.8*cm, self.width - 6*cm, self.height - 20.8*cm)
        
        # Quote
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Oblique", 10)
        c.setFillAlpha(0.8)
        c.drawCentredString(self.width / 2, self.height - 22*cm, "« Les étoiles inclinent, mais ne déterminent pas. »")
        c.setFillAlpha(1.0)
        
        # Bottom decorative lines
        y_bottom = 4*cm
        c.setStrokeColor(GOLD)
        c.line(3*cm, y_bottom, self.width - 3*cm, y_bottom)
        c.line(3*cm, y_bottom - 0.3*cm, self.width - 3*cm, y_bottom - 0.3*cm)
        
        # Generation date
        c.setFillColor(GOLD)
        c.setFillAlpha(0.5)
        c.setFont("Helvetica", 9)
        c.drawCentredString(self.width / 2, 2.5*cm, f"Généré le {datetime.now().strftime('%d/%m/%Y')}")
        c.drawCentredString(self.width / 2, 2*cm, "Plume Astrale © 2026")
        c.setFillAlpha(1.0)
    
    def _draw_section_page(self, c, title, subtitle, content_blocks, page_num, planet_data=None, hero_image=None):
        """Draw a content section page. hero_image = chemin local (via library_images)."""
        self._draw_starfield_background(c, page_num)
        self._draw_decorative_border(c)
        
        y = self.height - 3*cm
        
        # Section title
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(self.width / 2, y, title)
        y -= 1*cm
        
        # Subtitle
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 12)
        c.drawCentredString(self.width / 2, y, subtitle)
        y -= 0.5*cm
        
        # Decorative line
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.5)
        c.setLineWidth(0.5)
        c.line(4*cm, y, self.width - 4*cm, y)
        c.setStrokeAlpha(1.0)
        y -= 0.8*cm

        # Hero image (planète/signe/maison) centrée juste sous le titre
        if hero_image:
            img_size = 4.5*cm
            try:
                c.drawImage(hero_image, self.width/2 - img_size/2, y - img_size,
                            img_size, img_size, mask='auto', preserveAspectRatio=True)
            except Exception as e:
                logger.debug(f'[pdf_generator] hero_image failed: {e}')
            y -= img_size + 0.4*cm
        
        # Planet data box if provided
        if planet_data:
            box_height = 1.5*cm
            c.setFillColor(LIGHT_PURPLE)
            c.setFillAlpha(0.5)
            c.roundRect(self.margin, y - box_height, self.width - 2*self.margin, box_height, 5, fill=1)
            c.setFillAlpha(1.0)
            
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(self.margin + 0.5*cm, y - 0.6*cm, f"{planet_data.get('sign', '')} • Maison {planet_data.get('house', '')}")
            
            c.setFillColor(LIGHT_TEXT)
            c.setFont("Helvetica", 10)
            c.drawRightString(self.width - self.margin - 0.5*cm, y - 0.6*cm, f"Position: {planet_data.get('degree', '')}°")
            
            y -= box_height + 0.8*cm
        
        # Content blocks
        c.setFillColor(LIGHT_TEXT)
        for block in content_blocks:
            if block.get('type') == 'heading':
                c.setFillColor(GOLD)
                c.setFont("Helvetica-Bold", 13)
                c.drawString(self.margin, y, f"✦ {block['text']}")
                c.setFillColor(LIGHT_TEXT)
                y -= 0.8*cm
            elif block.get('type') == 'paragraph':
                # Wrap text
                c.setFont("Helvetica", 11)
                text = block['text']
                words = text.split()
                lines = []
                current_line = ""
                max_width = self.width - 2*self.margin - 1*cm
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if c.stringWidth(test_line, "Helvetica", 11) < max_width:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                for line in lines:
                    if y < 3*cm:  # Page break needed
                        break
                    c.drawString(self.margin + 0.5*cm, y, line)
                    y -= 0.5*cm
                y -= 0.5*cm
            elif block.get('type') == 'quote':
                c.setFillColor(CREAM)
                c.setFont("Helvetica-Oblique", 11)
                c.drawCentredString(self.width / 2, y, f"« {block['text']} »")
                c.setFillColor(LIGHT_TEXT)
                y -= 1*cm
            elif block.get('type') == 'list_item':
                c.setFont("Helvetica", 11)
                c.setFillColor(GOLD)
                c.drawString(self.margin + 0.5*cm, y, "•")
                c.setFillColor(LIGHT_TEXT)
                c.drawString(self.margin + 1*cm, y, block['text'])
                y -= 0.6*cm
        
        self._draw_page_number(c, page_num, 10)
    
    def _draw_planets_overview_page(self, c, planets_data, page_num):
        """Draw a page with all planets overview"""
        self._draw_starfield_background(c, page_num)
        self._draw_decorative_border(c)
        
        y = self.height - 3*cm
        
        # Title
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(self.width / 2, y, "Vos Positions Planétaires")
        y -= 1.5*cm
        
        # Decorative line
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.line(4*cm, y, self.width - 4*cm, y)
        y -= 1.5*cm
        
        # Planet grid
        if planets_data:
            col_width = (self.width - 2*self.margin) / 2
            row_height = 1.8*cm
            
            for i, planet in enumerate(planets_data[:10]):  # Max 10 planets
                col = i % 2
                row = i // 2
                
                x = self.margin + col * col_width + 0.3*cm
                current_y = y - row * row_height
                
                if current_y < 3*cm:
                    break
                
                # Planet box
                c.setFillColor(LIGHT_PURPLE)
                c.setFillAlpha(0.5)
                c.roundRect(x, current_y - 1.4*cm, col_width - 0.6*cm, 1.4*cm, 5, fill=1)
                c.setFillAlpha(1.0)
                
                # Planet name
                c.setFillColor(CREAM)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x + 0.4*cm, current_y - 0.5*cm, planet.get('name', ''))
                
                # Sign and house
                c.setFillColor(GOLD)
                c.setFont("Helvetica", 10)
                sign = self._get_french_sign(planet.get('sign', ''))
                c.drawString(x + 0.4*cm, current_y - 1*cm, f"{sign} • Maison {planet.get('house', '')}")
                
                # Degree
                c.setFillColor(LIGHT_TEXT)
                c.setFillAlpha(0.7)
                c.setFont("Helvetica", 9)
                degree = planet.get('normDegree', 0)
                c.drawRightString(x + col_width - 1*cm, current_y - 0.7*cm, f"{degree:.1f}°")
                c.setFillAlpha(1.0)
        
        self._draw_page_number(c, page_num, 10)
    
    def _get_french_sign(self, sign):
        """Convert English sign to French"""
        signs = {
            'Aries': 'Bélier', 'Taurus': 'Taureau', 'Gemini': 'Gémeaux',
            'Cancer': 'Cancer', 'Leo': 'Lion', 'Virgo': 'Vierge',
            'Libra': 'Balance', 'Scorpio': 'Scorpion', 'Sagittarius': 'Sagittaire',
            'Capricorn': 'Capricorne', 'Aquarius': 'Verseau', 'Pisces': 'Poissons'
        }
        return signs.get(sign, sign)
    
    def _draw_final_page(self, c, user_data, page_num):
        """Draw the final blessing page"""
        self._draw_starfield_background(c, page_num)
        
        y = self.height - 8*cm
        
        # Golden ornament
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        c.line(5*cm, y + 1*cm, self.width - 5*cm, y + 1*cm)
        
        # Title
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.width / 2, y, "Message de la Plume Astrale")
        y -= 2*cm
        
        # Blessing text
        c.setFillColor(LIGHT_TEXT)
        c.setFont("Helvetica", 12)
        
        blessing_lines = [
            f"Cher(e) {user_data.get('prenom', 'voyageur céleste')},",
            "",
            "Ce manuscrit est un miroir de votre âme,",
            "un guide pour votre voyage sur Terre.",
            "",
            "Les étoiles qui brillaient à votre naissance",
            "continuent de vous accompagner chaque jour.",
            "",
            "Puisse ce document vous rappeler",
            "la magie qui réside en vous.",
        ]
        
        for line in blessing_lines:
            c.drawCentredString(self.width / 2, y, line)
            y -= 0.7*cm
        
        y -= 1*cm
        
        # Quote box
        c.setFillColor(LIGHT_PURPLE)
        c.setFillAlpha(0.5)
        c.roundRect(3*cm, y - 2*cm, self.width - 6*cm, 2*cm, 10, fill=1)
        c.setFillAlpha(1.0)
        
        c.setFillColor(CREAM)
        c.setFont("Helvetica-BoldOblique", 12)
        c.drawCentredString(self.width / 2, y - 0.8*cm, "« Que les étoiles vous guident,")
        c.drawCentredString(self.width / 2, y - 1.4*cm, "que la Plume vous éclaire. »")
        
        y -= 4*cm
        
        # Footer ornament
        c.setStrokeColor(GOLD)
        c.line(5*cm, y, self.width - 5*cm, y)
        
        # Signature
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(self.width / 2, y - 1*cm, "Plume Astrale")
        c.setFillAlpha(0.6)
        c.setFont("Helvetica", 9)
        c.drawCentredString(self.width / 2, y - 1.6*cm, "www.plume-astrale.fr")
        c.setFillAlpha(1.0)
        
        self._draw_page_number(c, page_num, page_num)
    
    def generate_pdf(self, user_data: dict, planets_data: list = None, horoscope_data: dict = None) -> bytes:
        """Generate the complete PDF manuscript"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Determine zodiac sign
        zodiac_french = "Taureau"  # Default
        if planets_data:
            sun = next((p for p in planets_data if p.get('name') == 'Sun'), None)
            if sun:
                zodiac_french = self._get_french_sign(sun.get('sign', 'Taurus'))
        else:
            # Fallback : calcul depuis la date de naissance
            birth_iso = user_data.get('dateNaissance') or user_data.get('birth_date') or ''
            slug = libimg.sun_slug_from_date(birth_iso)
            if slug:
                _EN_TO_FR = {
                    'aries': 'Bélier', 'taurus': 'Taureau', 'gemini': 'Gémeaux',
                    'cancer': 'Cancer', 'leo': 'Lion', 'virgo': 'Vierge',
                    'libra': 'Balance', 'scorpio': 'Scorpion', 'sagittarius': 'Sagittaire',
                    'capricorn': 'Capricorne', 'aquarius': 'Verseau', 'pisces': 'Poissons',
                }
                zodiac_french = _EN_TO_FR.get(slug, zodiac_french)
        
        # Page 1: Title
        self._draw_title_page(c, user_data, zodiac_french)
        c.showPage()
        
        # Page 2: Introduction / Identité Céleste
        sun_data = None
        if planets_data:
            sun = next((p for p in planets_data if p.get('name') == 'Sun'), None)
            if sun:
                sun_data = {
                    'sign': self._get_french_sign(sun.get('sign', '')),
                    'house': sun.get('house', ''),
                    'degree': sun.get('normDegree', 0)
                }
        
        content = [
            {'type': 'heading', 'text': 'Votre Essence Solaire'},
            {'type': 'paragraph', 'text': f"Votre Soleil représente votre identité fondamentale, votre essence la plus profonde. C'est la lumière que vous êtes venu(e) rayonner sur Terre. En {zodiac_french}, votre Soleil vous confère des qualités uniques qui colorent votre personnalité."},
            {'type': 'heading', 'text': 'Signification de la Maison'},
            {'type': 'paragraph', 'text': "La maison dans laquelle se trouve votre Soleil indique le domaine de vie où votre essence s'exprime le plus naturellement. C'est là que vous brillez de mille feux et où vous trouvez votre véritable accomplissement."},
        ]
        self._draw_section_page(c, "Votre Soleil", "L'essence de qui vous êtes", content, 2, sun_data,
                                hero_image=libimg.planet('sun'))
        c.showPage()
        
        # Page 3: Lune
        moon_data = None
        if planets_data:
            moon = next((p for p in planets_data if p.get('name') == 'Moon'), None)
            if moon:
                moon_data = {
                    'sign': self._get_french_sign(moon.get('sign', '')),
                    'house': moon.get('house', ''),
                    'degree': moon.get('normDegree', 0)
                }
        
        content = [
            {'type': 'heading', 'text': 'Votre Monde Émotionnel'},
            {'type': 'paragraph', 'text': "Votre Lune révèle votre moi intérieur, vos émotions profondes et vos besoins fondamentaux. Elle représente votre part inconsciente, votre intuition et la façon dont vous vous nourrissez émotionnellement."},
            {'type': 'heading', 'text': 'Besoins Émotionnels'},
            {'type': 'paragraph', 'text': "La position de votre Lune indique ce dont vous avez besoin pour vous sentir en sécurité et épanoui(e). Comprendre votre Lune, c'est comprendre ce qui nourrit véritablement votre âme."},
        ]
        self._draw_section_page(c, "Votre Lune", "Votre monde intérieur", content, 3, moon_data,
                                hero_image=libimg.planet('moon'))
        c.showPage()
        
        # Page 4: Ascendant
        asc_data = None
        if planets_data:
            asc = next((p for p in planets_data if p.get('name') == 'Ascendant'), None)
            if asc:
                asc_data = {
                    'sign': self._get_french_sign(asc.get('sign', '')),
                    'house': 1,
                    'degree': asc.get('normDegree', 0)
                }
        
        content = [
            {'type': 'heading', 'text': 'Votre Masque Social'},
            {'type': 'paragraph', 'text': "L'Ascendant est le signe qui se levait à l'horizon est au moment de votre naissance. Il représente votre personnalité apparente, la première impression que vous donnez aux autres et votre approche naturelle de la vie."},
            {'type': 'heading', 'text': 'Apparence et Style'},
            {'type': 'paragraph', 'text': "Votre Ascendant influence votre apparence physique et votre style personnel. C'est le filtre à travers lequel vous percevez le monde et interagissez avec lui."},
        ]
        # Ascendant hero = signe de l'ASC si dispo, sinon Maison 1
        asc_hero = None
        if asc_data and asc_data.get('sign'):
            asc_hero = libimg.sign(asc_data['sign'])
        if not asc_hero:
            asc_hero = libimg.house(1)
        self._draw_section_page(c, "Votre Ascendant", "Votre masque social", content, 4, asc_data,
                                hero_image=asc_hero)
        c.showPage()
        
        # Page 5: Planets overview
        self._draw_planets_overview_page(c, planets_data, 5)
        c.showPage()
        
        # Page 6: Vénus et Mars
        content = [
            {'type': 'heading', 'text': 'Vénus - L\'Amour et les Valeurs'},
            {'type': 'paragraph', 'text': "Vénus dans votre thème représente votre façon d'aimer et d'être aimé(e), vos valeurs esthétiques et ce qui vous procure du plaisir. Elle révèle votre style relationnel et ce que vous recherchez dans vos partenariats."},
            {'type': 'heading', 'text': 'Mars - L\'Action et la Passion'},
            {'type': 'paragraph', 'text': "Mars représente votre énergie vitale, votre façon d'agir et de vous affirmer. Il indique comment vous poursuivez vos désirs et gérez les conflits. C'est votre moteur d'action."},
        ]
        self._draw_section_page(c, "Cœur & Relations", "Vénus et Mars dans votre thème", content, 6,
                                hero_image=libimg.planet('venus'))
        c.showPage()
        
        # Page 7: Conseils
        content = [
            {'type': 'heading', 'text': 'Trois Clés pour 2026'},
            {'type': 'list_item', 'text': "Honorez votre essence unique et laissez-la rayonner sans retenue."},
            {'type': 'list_item', 'text': "Écoutez votre intuition lunaire, elle est votre guide intérieur."},
            {'type': 'list_item', 'text': "Transformez chaque défi en opportunité de croissance."},
            {'type': 'heading', 'text': 'Domaines d\'Attention'},
            {'type': 'paragraph', 'text': "Les périodes de Mars-Mai et Septembre-Novembre seront particulièrement favorables pour les nouveaux projets. Évitez les décisions impulsives en juin-juillet."},
            {'type': 'quote', 'text': "Votre thème est une carte, pas une prison. Utilisez-le comme guide."},
        ]
        self._draw_section_page(c, "Conseils de la Plume", "Guidance pour votre chemin", content, 7,
                                hero_image=libimg.planet('jupiter'))
        c.showPage()
        
        # Page 8: Final blessing
        self._draw_final_page(c, user_data, 8)
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()


# Create singleton instance
pdf_generator = ManuscritPDFGenerator()

def generate_manuscrit_pdf(user_data: dict, planets_data: list = None, horoscope_data: dict = None) -> bytes:
    """Generate a beautiful PDF manuscript"""
    return pdf_generator.generate_pdf(user_data, planets_data, horoscope_data)
