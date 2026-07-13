"""
Générateur PDF "Fenêtres de Rencontre Avancées" — 10 pages.
Fenêtres de rencontre calculées via transits + synastrie (si 2 thèmes).
Images cosmiques + calculs détaillés + conseils d'activation.
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

# Palette
NIGHT       = colors.HexColor('#111625')
NIGHT_SOFT  = colors.HexColor('#1A2035')
GOLD        = colors.HexColor('#D4AF37')
GOLD_LIGHT  = colors.HexColor('#E8C766')
LAVENDER    = colors.HexColor('#E3D7FF')
CREAM       = colors.HexColor('#F5EEE0')
MUTED       = colors.HexColor('#9089B5')

class FenetreRencontrePDFGenerator:
    """Fenêtres de rencontre avancées avec calculs astrologiques."""
    
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
        windows_data: List[Dict[str, Any]],
        synastry_data: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """Génère le PDF (10 pages)."""
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
        
        # Pages 3-8: Fenêtres détaillées
        for i, window in enumerate(windows_data[:3]):  # Max 3 fenêtres
            if i > 0:
                story.append(PageBreak())
            story.extend(self._page_window(window, i + 1))
        
        story.append(PageBreak())
        
        # Page 9: Synastrie (si données)
        if synastry_data:
            story.extend(self._page_synastrie(synastry_data))
            story.append(PageBreak())
        
        # Page 10: Rituels d'attraction
        story.extend(self._page_rituels_finaux(first_name))
        
        doc.build(story)
        return buffer.getvalue()
    
    def _page_cover(self, name: str) -> List:
        """Couverture mystique."""
        return [
            Spacer(0, 3 * cm),
            Paragraph('✦ FENÊTRES DE RENCONTRE ✦', self.title_style),
            Spacer(0, 0.5 * cm),
            Paragraph('Les Moments Cosmiques Favorables à ta Rencontre', self.subtitle_style),
            Spacer(0, 2 * cm),
            Paragraph(
                'L\'univers crée des fenêtres temporelles pour te rapprocher<br/>'
                'de ta personne destinée. Découvre quand frapper à la porte du destin.',
                self.body_style,
            ),
            Spacer(0, 3 * cm),
            Paragraph('par Solena — La voix de Plume Astrale', ParagraphStyle(
                'Footer', fontName='Helvetica-Oblique', fontSize=10, textColor=GOLD_LIGHT, alignment=TA_CENTER
            )),
        ]
    
    def _page_intro(self) -> List:
        """Introduction aux fenêtres."""
        return [
            Paragraph('Comprendre les Fenêtres de Rencontre', self.heading_style),
            Spacer(0, 0.3 * cm),
            Paragraph(
                'Une fenêtre de rencontre est un period temporelle où l\'univers aligné '
                'les énergies pour te permettre de rencontrer ta personne de destinée.<br/><br/>'
                'Ces fenêtres sont calculées selon :<br/>'
                '• <b>Transits de Vénus</b> — amour et attraction<br/>'
                '• <b>Transits de Jupiter</b> — expansion et nouvelles rencontres<br/>'
                '• <b>Phases Lunaires</b> — intentions et manifestations<br/>'
                '• <b>Ton thème natal</b> — tes périodes les plus magnétiques',
                self.body_style,
            ),
            Spacer(0, 0.5 * cm),
            Paragraph(
                '<b>⚠️ Important :</b> Une fenêtre ne signifie pas que tu vas rencontrer '
                'automatiquement quelqu\'un. Elle signifie que les énergies sont favorables. '
                'À toi de sortir, de rayonner, de croire.',
                self.body_style,
            ),
        ]
    
    def _page_window(self, window: Dict[str, Any], index: int) -> List:
        """Page pour une fenêtre spécifique."""
        story = []
        
        window_type = window.get('kind', f'Fenêtre {index}')
        period = window.get('period', 'À déterminer')
        description = window.get('text', 'Période d\'opportunités.')
        
        story.append(Paragraph(f'✦ {window_type} ✦', self.heading_style))
        story.append(Paragraph(f'Période : {period}', self.subtitle_style))
        story.append(Spacer(0, 0.5 * cm))
        
        story.append(Paragraph(description, self.body_style))
        story.append(Spacer(0, 0.8 * cm))
        
        # Conseils d'activation
        story.append(Paragraph('<b>Comment Activer Cette Fenêtre :</b>', self.heading_style))
        story.append(Paragraph(
            f'<b>1. Intention Consciente</b><br/>'
            f'Pendant cette période, fixe clairement ton intention de rencontre. '
            f'Visualise la personne avec qui tu veux être.<br/><br/>'
            f'<b>2. Action Tangible</b><br/>'
            f'Sort, engage-toi socialement, dit oui aux invitations. '
            f'L\'univers aide ceux qui se mettent en action.<br/><br/>'
            f'<b>3. Radiance Intérieure</b><br/>'
            f'Crée un rituel de beauté et d\'amour-propre. Rayonne ta meilleure version.',
            self.body_style,
        ))
        
        return story
    
    def _page_synastrie(self, data: Dict[str, Any]) -> List:
        """Analyse synastrie (si données 2 thèmes)."""
        story = []
        story.append(Paragraph('✦ Analyse de Compatibilité ✦', self.heading_style))
        
        compatibility_score = data.get('compatibility_score', 'À calculer')
        interpretation = data.get('interpretation', 
            'La compatibilité entre deux âmes est complexe et multidimensionnelle.')
        
        story.append(Paragraph(
            f'<b>Score de Compatibilité : {compatibility_score}%</b>',
            self.subtitle_style,
        ))
        story.append(Spacer(0, 0.5 * cm))
        
        story.append(Paragraph(interpretation, self.body_style))
        
        return story
    
    def _page_rituels_finaux(self, name: str) -> List:
        """Rituels d'attraction et d'activation."""
        return [
            Paragraph('Rituels d\'Attraction pour Ouvrir la Fenêtre', self.heading_style),
            Spacer(0, 0.3 * cm),
            Paragraph(
                '<b>Rituel de la Chandelle Rose</b><br/>'
                'Chaque soir pendant la fenêtre, allume une chandelle rose. '
                'Visualise une lueur dorée t\'enveloppant, t\'attirant les âmes aimantes.<br/><br/>'
                '<b>Rituel du Miroir Magique</b><br/>'
                'Regarde-toi 3 minutes dans le miroir avec tendresse. '
                'Dis à haute voix : "Je suis magnétique, aimante et prêt(e) pour la rencontre."<br/><br/>'
                '<b>Cristaux Amplificateurs</b><br/>'
                'Porte une pierre de rose (amour) ou de citrine (manifestation) pendant la fenêtre.<br/><br/>'
                '<b>Affirmation Nocturne</b><br/>'
                '"L\'univers m\'apporte la rencontre parfaite au moment parfait. '
                'Je suis ouvert(e) à l\'amour."',
                self.body_style,
            ),
            Spacer(0, 1 * cm),
            Paragraph(
                '─ ✦ ─<br/><br/>'
                'Le destin t\'appelle. Réponds à son invitation.<br/>'
                f'À bientôt, {name}.<br/><br/>'
                '<i>Solena — La voix de Plume Astrale</i>',
                ParagraphStyle(
                    'Signature', fontName='Helvetica-Oblique', fontSize=11,
                    textColor=GOLD, alignment=TA_CENTER, leading=14
                ),
            ),
        ]


def generate_fenetre_rencontre_pdf(
    first_name: str,
    birth_date_iso: str,
    windows_data: List[Dict[str, Any]],
    synastry_data: Optional[Dict[str, Any]] = None,
) -> bytes:
    """Wrapper pour générer le PDF fenêtres avancées."""
    return FenetreRencontrePDFGenerator().generate(
        first_name=first_name,
        birth_date_iso=birth_date_iso,
        windows_data=windows_data,
        synastry_data=synastry_data,
    )
