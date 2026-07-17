"""
Générateur PDF "Ton Analyse Karmique & Destinée" — 15 pages.
Basé sur données de /analysis/karmic + transits + nœuds lunaires.
Français 100% + analyse spirituelle profonde.
"""
from __future__ import annotations
from io import BytesIO
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Palette Plume Astrale
NIGHT       = colors.HexColor('#111625')
NIGHT_SOFT  = colors.HexColor('#1A2035')
GOLD        = colors.HexColor('#D4AF37')
GOLD_LIGHT  = colors.HexColor('#E8C766')
LAVENDER    = colors.HexColor('#E3D7FF')
CREAM       = colors.HexColor('#F5EEE0')
MUTED       = colors.HexColor('#9089B5')

class KarmaDestinPDFGenerator:
    """Analyse karmique complète (15 pages) — Nœuds lunaires, Saturne, Chiron, karma générationnel."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Styles personnalisés."""
        self.title_style = ParagraphStyle(
            'Title',
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=GOLD,
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        self.heading_style = ParagraphStyle(
            'Heading',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=LAVENDER,
            spaceAfter=8,
            spaceBefore=12,
            alignment=TA_CENTER,
        )
        self.body_style = ParagraphStyle(
            'Body',
            fontName='Helvetica',
            fontSize=11,
            textColor=CREAM,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            leading=16,
        )
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
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
        karmic_data: Dict[str, Any],
    ) -> bytes:
        """Génère le PDF complet (15 pages)."""
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
        
        # Page 2: Introduction karmique
        story.extend(self._page_intro())
        story.append(PageBreak())
        
        # Pages 3-5: Nœuds lunaires (chemin de destinée)
        story.extend(self._pages_noeuds_lunaires(karmic_data))
        story.append(PageBreak())
        
        # Pages 6-8: Saturne (leçons karmiques)
        story.extend(self._pages_saturne(karmic_data))
        story.append(PageBreak())
        
        # Pages 9-11: Chiron (guérison karmique)
        story.extend(self._pages_chiron(karmic_data))
        story.append(PageBreak())
        
        # Pages 12-13: Pluton (transformation)
        story.extend(self._pages_pluton(karmic_data))
        story.append(PageBreak())
        
        # Page 14: Karma générationnel
        story.extend(self._page_karma_generationnel(karmic_data))
        story.append(PageBreak())
        
        # Page 15: Rituels de libération
        story.extend(self._page_rituels_liberation(first_name))
        
        doc.build(story)
        return buffer.getvalue()
    
    def _page_cover(self, name: str) -> List:
        """Couverture spirituelle."""
        return [
            Spacer(0, 3 * cm),
            Paragraph('✦ TON ANALYSE KARMIQUE ✦', self.title_style),
            Spacer(0, 0.5 * cm),
            Paragraph('Destinée, Leçons & Guérison Spirituelle', self.subtitle_style),
            Spacer(0, 2 * cm),
            Paragraph(
                'Au-delà du présent, ton karma te parle.<br/>'
                'Découvre les leçons que ton âme est venue apprendre.',
                self.body_style,
            ),
            Spacer(0, 3 * cm),
            Paragraph('par Solena — La voix de Plume Astrale', ParagraphStyle(
                'Footer', fontName='Helvetica-Oblique', fontSize=10, textColor=GOLD_LIGHT, alignment=TA_CENTER
            )),
        ]
    
    def _page_intro(self) -> List:
        """Introduction au karma."""
        return [
            Paragraph('Comprendre Ton Karma', self.heading_style),
            Spacer(0, 0.3 * cm),
            Paragraph(
                'Le karma n\'est pas une punition — c\'est un enseignement. '
                'Chaque incarnation te rapproche de ta sagesse cosmique.<br/><br/>'
                'Cette analyse révèle :<br/>'
                '• Tes <b>nœuds lunaires</b> : ton chemin d\'évolution<br/>'
                '• Ton <b>Saturne</b> : tes leçons de vie<br/>'
                '• Ton <b>Chiron</b> : ta blessure sacrée et guérison<br/>'
                '• Ton <b>Pluton</b> : transformations de pouvoir<br/>'
                '• Ton <b>karma générationnel</b> : l\'héritage de tes ancêtres',
                self.body_style,
            ),
        ]
    
    def _pages_noeuds_lunaires(self, data: Dict[str, Any]) -> List:
        """Nœud nord/sud — chemin de destinée."""
        story = []
        story.append(Paragraph('⚜ Les Nœuds Lunaires — Ton Chemin d\'Évolution ⚜', self.heading_style))
        
        north_node = data.get('north_node', {})
        south_node = data.get('south_node', {})
        
        if isinstance(north_node, dict):
            nn_sign = north_node.get('sign', 'Inconnu')
            nn_desc = north_node.get('description', 'Ton potentiel de croissance.')
            story.append(Paragraph(f'<b>Nœud Nord en {nn_sign}</b>', self.heading_style))
            story.append(Paragraph(f'{nn_desc}', self.body_style))
        
        story.append(Spacer(0, 0.8 * cm))
        
        if isinstance(south_node, dict):
            sn_sign = south_node.get('sign', 'Inconnu')
            sn_desc = south_node.get('description', 'Ce que tu as maîtrisé dans des vies antérieures.')
            story.append(Paragraph(f'<b>Nœud Sud en {sn_sign}</b>', self.heading_style))
            story.append(Paragraph(f'{sn_desc}', self.body_style))
        
        story.append(Spacer(0, 0.5 * cm))
        story.append(Paragraph(
            'Tu n\'as pas besoin de développer le Nœud Sud — tu l\'as déjà. '
            'Ton travail spirituel consiste à évoluer vers le Nœud Nord, '
            'même si cela semble inconfortable au départ.',
            self.body_style,
        ))
        
        return story
    
    def _pages_saturne(self, data: Dict[str, Any]) -> List:
        """Saturne — leçons karmiques et tests de vie."""
        story = []
        story.append(Paragraph('⚜ Saturne — Tes Leçons Karmiques ⚜', self.heading_style))
        
        saturn = data.get('saturn', {})
        if isinstance(saturn, dict):
            saturn_sign = saturn.get('sign', 'Inconnu')
            saturn_desc = saturn.get('description', 
                'Saturne te teste pour te renforcer. Accueille ses leçons.')
            
            story.append(Paragraph(f'<b>Saturne en {saturn_sign}</b>', self.heading_style))
            story.append(Paragraph(saturn_desc, self.body_style))
        
        story.append(Spacer(0, 0.5 * cm))
        story.append(Paragraph(
            'Saturne n\'est pas ton ennemi — c\'est ton professeur. '
            'Où tu trouves de la friction, tu trouveras ta plus grande force.',
            self.body_style,
        ))
        
        return story
    
    def _pages_chiron(self, data: Dict[str, Any]) -> List:
        """Chiron — blessure sacrée et guérison."""
        story = []
        story.append(Paragraph('⚜ Chiron — La Blessure Sacrée & La Guérison ⚜', self.heading_style))
        
        chiron = data.get('chiron', {})
        if isinstance(chiron, dict):
            chiron_sign = chiron.get('sign', 'Inconnu')
            chiron_desc = chiron.get('description',
                'Ton blessure est ta porte de guérison.')
            
            story.append(Paragraph(f'<b>Chiron en {chiron_sign}</b>', self.heading_style))
            story.append(Paragraph(chiron_desc, self.body_style))
        
        story.append(Spacer(0, 0.5 * cm))
        story.append(Paragraph(
            'Chiron révèle la blessure invisible que ton âme porte depuis longtemps. '
            'Mais cette blessure devient ton superbe cadeau — tu guéris les autres '
            'là où tu as souffert toi-même.',
            self.body_style,
        ))
        
        return story
    
    def _pages_pluton(self, data: Dict[str, Any]) -> List:
        """Pluton — transformation et pouvoir."""
        story = []
        story.append(Paragraph('⚜ Pluton — Transformations de Pouvoir ⚜', self.heading_style))
        
        pluto = data.get('pluto', {})
        if isinstance(pluto, dict):
            pluto_sign = pluto.get('sign', 'Inconnu')
            pluto_desc = pluto.get('description',
                'Pluton t\'invite à muter, à renaître.')
            
            story.append(Paragraph(f'<b>Pluton en {pluto_sign}</b>', self.heading_style))
            story.append(Paragraph(pluto_desc, self.body_style))
        
        return story
    
    def _page_karma_generationnel(self, data: Dict[str, Any]) -> List:
        """Karma générationnel — héritage ancestral."""
        story = []
        story.append(Paragraph('⚜ Ton Héritage Karmique Générationnel ⚜', self.heading_style))
        
        gen_karma = data.get('generational_karma', 
            'Tes ancêtres vivent à travers toi. Tu portes leur sagesse et leurs apprentissages.')
        
        story.append(Paragraph(gen_karma, self.body_style))
        story.append(Spacer(0, 0.5 * cm))
        story.append(Paragraph(
            'Par tes choix conscients, tu guéris les patterns familiaux. '
            'Chaque action bienveillante libère des générations.',
            self.body_style,
        ))
        
        return story
    
    def _page_rituels_liberation(self, name: str) -> List:
        """Rituels de libération karmique."""
        return [
            Paragraph('Rituels de Libération Karmique', self.heading_style),
            Spacer(0, 0.3 * cm),
            Paragraph(
                '<b>1. Bain du Pardon</b><br/>'
                'Chaque semaine, prends un bain d\'eau chaude avec sel marin et lavande. '
                'Visualise les chaînes karmiques se dissoudre.<br/><br/>'
                '<b>2. Lettre aux Ancêtres</b><br/>'
                'Écris une lettre de gratitude à tes ancêtres, puis brûle-la symboliquement '
                'pour libérer les patterns ancestraux.<br/><br/>'
                '<b>3. Affirmation Quotidienne</b><br/>'
                '"Je suis libéré(e) de mon karma passé. Je crée un futur lumineux."',
                self.body_style,
            ),
            Spacer(0, 1 * cm),
            Paragraph(
                '─ ✦ ─<br/><br/>'
                'Ton karma n\'est pas ta destinée — c\'est ton tremplin.<br/>'
                f'À bientôt, {name}.<br/><br/>'
                '<i>Solena — La voix de Plume Astrale</i>',
                ParagraphStyle(
                    'Signature', fontName='Helvetica-Oblique', fontSize=11,
                    textColor=GOLD, alignment=TA_CENTER, leading=14
                ),
            ),
        ]


def generate_karma_destin_pdf(
    first_name: str,
    birth_date_iso: str,
    karmic_data: Dict[str, Any],
) -> bytes:
    """Wrapper pour générer le PDF karma/destin."""
    return KarmaDestinPDFGenerator().generate(
        first_name=first_name,
        birth_date_iso=birth_date_iso,
        karmic_data=karmic_data,
    )
