"""
Générateur PDF "Ton Code Numérologique" — 12 pages, images + texte FR.
Basé sur les données de /numerology/name, /numerology/personal-year, /numerology/forecast.
Palette Plume Astrale avec images géométriques.
"""
from __future__ import annotations
from io import BytesIO
from typing import Any, Dict, List, Optional
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image as RLImage, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Circle, Rect, Line, Polygon
from reportlab.graphics import renderPDF

# Palette Plume Astrale
NIGHT       = colors.HexColor('#111625')
NIGHT_SOFT  = colors.HexColor('#1A2035')
GOLD        = colors.HexColor('#D4AF37')
GOLD_LIGHT  = colors.HexColor('#E8C766')
LAVENDER    = colors.HexColor('#E3D7FF')
CREAM       = colors.HexColor('#F5EEE0')
MUTED       = colors.HexColor('#9089B5')

# Traductions français
NOMBRES_FR = {
    '1': ('Unité', 'Leadership, Création, Indépendance'),
    '2': ('Dualité', 'Harmonie, Partenariat, Intuition'),
    '3': ('Créativité', 'Expression, Communication, Joie'),
    '4': ('Stabilité', 'Construction, Ordre, Dévouement'),
    '5': ('Liberté', 'Changement, Aventure, Adaptabilité'),
    '6': ('Harmonie', 'Famille, Responsabilité, Amour'),
    '7': ('Spiritualité', 'Introspection, Sagesse, Mystère'),
    '8': ('Pouvoir', 'Réussite, Matérialité, Abondance'),
    '9': ('Sagesse', 'Humanité, Complétude, Pardon'),
    '11': ('Maître 11', 'Intuition élevée, Idéalisme, Illumination'),
    '22': ('Maître 22', 'Manifestation globale, Maître Bâtisseur'),
    '33': ('Maître 33', 'Compassion universelle, Guérison'),
}

def _create_number_circle(number: str, size: int = 3) -> Drawing:
    """Crée un cercle numérologique avec chiffre et couronne or."""
    d = Drawing(size * cm, size * cm)
    # Cercle extérieur (gold)
    c1 = Circle(size * cm / 2, size * cm / 2, size * cm / 2 - 0.1 * cm, fillColor=None, strokeColor=GOLD, strokeWidth=2)
    d.add(c1)
    # Cercle intérieur (dark)
    c2 = Circle(size * cm / 2, size * cm / 2, size * cm / 2 - 0.5 * cm, fillColor=NIGHT_SOFT, strokeColor=GOLD_LIGHT, strokeWidth=1)
    d.add(c2)
    return d


class NumerologiePDFGenerator:
    """Générateur PDF complet pour profil numérologique (12 pages)."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configure styles personnalisés."""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=GOLD,
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=LAVENDER,
            spaceAfter=8,
            spaceBefore=12,
            alignment=TA_CENTER,
        )
        self.body_style = ParagraphStyle(
            'CustomBody',
            fontName='Helvetica',
            fontSize=11,
            textColor=CREAM,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            leading=16,
        )
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            fontName='Helvetica-Oblique',
            fontSize=13,
            textColor=GOLD_LIGHT,
            spaceAfter=12,
            alignment=TA_CENTER,
        )
    
    def generate(
        self,
        first_name: str,
        birth_date_iso: str,
        numerology_data: Dict[str, Any],
        personal_year_data: Optional[Dict[str, Any]] = None,
        forecast_data: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """Génère le PDF complet (12 pages)."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
        )
        
        story = []
        
        # Page 1: Couverture
        story.extend(self._page_cover(first_name))
        story.append(PageBreak())
        
        # Page 2: Introduction
        story.extend(self._page_intro())
        story.append(PageBreak())
        
        # Pages 3-5: Nombres clés
        story.extend(self._pages_nombres_cles(numerology_data, first_name))
        story.append(PageBreak())
        
        # Pages 6-8: Année personnelle
        if personal_year_data:
            story.extend(self._pages_annee_personnelle(personal_year_data))
            story.append(PageBreak())
        
        # Pages 9-11: Prévisions
        if forecast_data:
            story.extend(self._pages_forecast(forecast_data))
            story.append(PageBreak())
        
        # Page 12: Rituels + signature
        story.extend(self._page_rituels_finaux(first_name))
        
        doc.build(story)
        return buffer.getvalue()
    
    def _page_cover(self, name: str) -> List:
        """Couverture dorée et mystique."""
        return [
            Spacer(0, 3 * cm),
            Paragraph('✦ TON CODE NUMÉROLOGIQUE ✦', self.title_style),
            Spacer(0, 0.5 * cm),
            Paragraph(f'Destinée, Cycles & Vibrations de {name}', self.subtitle_style),
            Spacer(0, 2 * cm),
            Paragraph(
                'Chaque nombre vibre avec une essence cosmique.<br/>Ta date de naissance révèle tes cycles karmiques.',
                self.body_style,
            ),
            Spacer(0, 3 * cm),
            Paragraph('par Solena — La voix de Plume Astrale', ParagraphStyle(
                'Footer', fontName='Helvetica-Oblique', fontSize=10, textColor=GOLD_LIGHT, alignment=TA_CENTER
            )),
        ]
    
    def _page_intro(self) -> List:
        """Introduction à la numérologie sacrée."""
        return [
            Paragraph('Bienvenue dans ton Univers Numéral', self.heading_style),
            Spacer(0, 0.3 * cm),
            Paragraph(
                'La numérologie est l\'art ancestral de déchiffrer les messages cachés '
                'dans les nombres. Chaque chiffre de ta date de naissance résonne avec '
                'une fréquence unique, révélant tes talents innés, tes défis de vie, '
                'et les cycles qui te guident.',
                self.body_style,
            ),
            Spacer(0, 0.5 * cm),
            Paragraph(
                '<b>Les Trois Nombres Clés :</b><br/>'
                '• <b>Nombre de Destin</b> : Ton chemin de vie et ta mission<br/>'
                '• <b>Nombre d\'Expression</b> : Tes talents naturels<br/>'
                '• <b>Nombre de Cœur</b> : Tes désirs profonds et aspirations',
                self.body_style,
            ),
        ]
    
    def _pages_nombres_cles(self, data: Dict[str, Any], name: str) -> List:
        """Détail des 3 nombres principaux."""
        story = []
        story.append(Paragraph('Tes Nombres Clés', self.heading_style))
        
        # Extrait données (peut varier selon format API)
        destiny_num = data.get('destiny_number', 1)
        expression_num = data.get('expression_number', 1)
        heart_num = data.get('heart_number', 1)
        
        for i, (title, num) in enumerate([
            ('Nombre de Destin', str(destiny_num)),
            ('Nombre d\'Expression', str(expression_num)),
            ('Nombre de Cœur', str(heart_num)),
        ]):
            if i > 0:
                story.append(Spacer(0, 0.8 * cm))
            
            num_clean = num.split('/')[0] if '/' in num else num  # Gère '11/2' format
            label, description = NOMBRES_FR.get(num_clean, ('Inconnu', 'Vibration secrète'))
            
            story.append(Paragraph(f'<b>{title}</b> : {label}', self.heading_style))
            story.append(Paragraph(description, self.body_style))
            story.append(Paragraph(
                f'La vibration du <b>{num}</b> te pousse vers une destinée '
                'unique. Explore cette énergie pour manifester ton potentiel.',
                self.body_style,
            ))
        
        return story
    
    def _pages_annee_personnelle(self, data: Dict[str, Any]) -> List:
        """Analyse année personnelle (cycle annuel)."""
        story = []
        story.append(Paragraph('Ton Année Personnelle', self.heading_style))
        
        current_year_num = data.get('personal_year', 1)
        year_description = data.get('year_description', 'Année de transformation.')
        
        story.append(Paragraph(
            f'Année numérale <b>{current_year_num}</b> — {year_description}',
            self.body_style,
        ))
        story.append(Spacer(0, 0.5 * cm))
        story.append(Paragraph(
            'Cette année résonne avec les énergies de manifestation et de croissance. '
            'Les cycles numériques te guident mois après mois.',
            self.body_style,
        ))
        
        return story
    
    def _pages_forecast(self, data: Dict[str, Any]) -> List:
        """Prévisions et cycles futurs."""
        story = []
        story.append(Paragraph('Prévisions des Cycles à Venir', self.heading_style))
        
        forecast = data.get('forecast', [])
        if isinstance(forecast, list) and len(forecast) > 0:
            for item in forecast[:3]:  # Max 3 prévisions
                if isinstance(item, dict):
                    period = item.get('period', 'Prochain mois')
                    insight = item.get('insight', 'Énergie nouvelle en approche.')
                    story.append(Paragraph(f'<b>{period}</b> : {insight}', self.body_style))
                    story.append(Spacer(0, 0.3 * cm))
        
        return story
    
    def _page_rituels_finaux(self, name: str) -> List:
        """Rituels d'intégration + signature Solena."""
        return [
            Paragraph('Rituels d\'Activation Numérologique', self.heading_style),
            Spacer(0, 0.3 * cm),
            Paragraph(
                '<b>1. Méditation du Nombre</b><br/>'
                'Chaque matin, visualise ton nombre de destin en lettres d\'or. '
                'Respire sa vibration en toi.<br/><br/>'
                '<b>2. Affirmation Quotidienne</b><br/>'
                'Répète : "Je suis aligné(e) avec mon essence numérale, '
                'ma destinée se manifeste avec grâce."<br/><br/>'
                '<b>3. Cristaux Numériques</b><br/>'
                'Porte une pierre correspondant à ton nombre clé.',
                self.body_style,
            ),
            Spacer(0, 1 * cm),
            Paragraph(
                '─ ✦ ─<br/><br/>'
                'Ce chemin numéral est ton secret cosmique.<br/>'
                f'À bientôt, {name}.<br/><br/>'
                '<i>Solena — La voix de Plume Astrale</i>',
                ParagraphStyle(
                    'Signature', fontName='Helvetica-Oblique', fontSize=11,
                    textColor=GOLD, alignment=TA_CENTER, leading=14
                ),
            ),
        ]


def generate_numerologie_pdf(
    first_name: str,
    birth_date_iso: str,
    numerology_data: Dict[str, Any],
    personal_year_data: Optional[Dict[str, Any]] = None,
    forecast_data: Optional[Dict[str, Any]] = None,
) -> bytes:
    """Wrapper pour générer le PDF numérologie."""
    return NumerologiePDFGenerator().generate(
        first_name=first_name,
        birth_date_iso=birth_date_iso,
        numerology_data=numerology_data,
        personal_year_data=personal_year_data,
        forecast_data=forecast_data,
    )
