"""
Générateur PDF "Fenêtres de Rencontre Avancées" — 10 pages avec fond VIOLET.
Version 2: Utilise des rectangles Platypus + images pour remplir les pages
"""
from __future__ import annotations
from io import BytesIO
from typing import Any, Dict, List, Optional
from urllib.request import urlopen

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, 
    PageTemplate, Frame, Flowable
)
from reportlab.pdfgen import canvas as pdfgen_canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Palette
VIOLET_DARK = colors.HexColor('#2D1B4E')
CREAM       = colors.HexColor('#F5EEE0')
LAVENDER    = colors.HexColor('#E3D7FF')
GOLD_LIGHT  = colors.HexColor('#E8C766')

class VioletRectangle(Flowable):
    """Rectangle violet qui s'étend sur toute la hauteur disponible"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def draw(self):
        self.canv.setFillColor(VIOLET_DARK)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)

class FenetreRencontrePDFGenerator:
    """Fenêtres de rencontre avec fond violet sur TOUTES les pages"""
    
    TAROT_IMAGES = {
        'amoureux': 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library/tarot/06_les_amoureux_1080.png',
        'etoile': 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library/tarot/17_l_etoile_1080.png',
        'soleil': 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library/tarot/19_le_soleil_1080.png',
        'lune': 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library/tarot/18_la_lune_1080.png',
        'imperatrice': 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library/tarot/03_l_imperatrice_1080.png',
    }
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.affirmations = []
        self._setup_styles()
    
    def _load_image(self, url: str, width: float, height: float) -> Optional[Image]:
        """Charge une image depuis URL"""
        try:
            img_data = BytesIO(urlopen(url).read())
            img = Image(img_data, width=width, height=height)
            return img
        except Exception as e:
            print(f"⚠️ Image error: {e}")
            return None
    
    def _setup_styles(self):
        """Définit les styles de texte"""
        self.title_style = ParagraphStyle(
            'Title',
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=CREAM,
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
        affirmations: Optional[List[str]] = None,
    ) -> bytes:
        """Génère le PDF 10 pages avec fond VIOLET"""
        self.affirmations = affirmations or []
        buffer = BytesIO()
        
        # Utiliser un Canvas-based approach pour garantir le fond violet
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
        )
        
        # PageTemplate avec fond violet garanti
        class VioletPageTemplate(PageTemplate):
            def __init__(self, *args, generator=None, **kwargs):
                self.generator = generator
                super().__init__(*args, **kwargs)
            
            def beforeDrawPage(self, canvas, doc):
                """Dessine le fond VIOLET avant tout contenu"""
                canvas.saveState()
                canvas.setFillColor(self.generator.VIOLET_DARK if hasattr(self.generator, 'VIOLET_DARK') else colors.HexColor('#2D1B4E'))
                # Remplir TOUTE la page (incluant les marges)
                canvas.rect(-1000, -1000, 3000, 3000, fill=1, stroke=0)
                canvas.restoreState()
        
        self.VIOLET_DARK = VIOLET_DARK  # Pour que la classe ait accès
        
        frame = Frame(
            1.5 * cm, 1.5 * cm,
            A4[0] - 3 * cm,
            A4[1] - 3 * cm,
            id='normal'
        )
        
        template = VioletPageTemplate(
            id='violet',
            pagesize=A4,
            frames=[frame],
            generator=self
        )
        doc.addPageTemplates([template])
        
        story = []
        
        # Page 1: Couverture
        story.extend(self._page_cover(first_name))
        story.append(PageBreak())
        
        # Page 2: Introduction
        story.extend(self._page_intro())
        story.append(PageBreak())
        
        # Pages 3-5: Fenêtres
        for i, window in enumerate(windows_data[:3]):
            story.extend(self._page_window(window, i + 1))
            if i < 2:
                story.append(PageBreak())
        
        story.append(PageBreak())
        
        # Page 6: Manifestation
        story.extend(self._page_manifestation())
        story.append(PageBreak())
        
        # Page 7: Transits
        story.extend(self._page_transits_bonus(birth_date_iso))
        story.append(PageBreak())
        
        # Page 8: Rituels
        story.extend(self._page_rituels_avances())
        story.append(PageBreak())
        
        # Page 9: Cristaux
        story.extend(self._page_cristaux())
        story.append(PageBreak())
        
        # Page 10: Affirmations
        story.extend(self._page_affirmations_finales(first_name))
        
        doc.build(story)
        return buffer.getvalue()
    
    def _add_filler_image(self, height_needed: float = 3 * cm) -> Optional[Image]:
        """Ajoute une petite image pour remplir le bas de page"""
        img_key = ['amoureux', 'etoile', 'soleil', 'lune', 'imperatrice'][hash(str(height_needed)) % 5]
        return self._load_image(self.TAROT_IMAGES[img_key], 3 * cm, height_needed)
    
    def _page_cover(self, name: str) -> List:
        """Page 1: Couverture mystique"""
        story = []
        story.append(Spacer(0, 0.5 * cm))
        
        img = self._load_image(self.TAROT_IMAGES['amoureux'], 6.5 * cm, 8.5 * cm)
        if img:
            img_table = Table([[img]], colWidths=[6.5 * cm])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('BACKGROUND', (0, 0), (0, 0), colors.transparent),
            ]))
            story.append(img_table)
            story.append(Spacer(0, 0.5 * cm))
        
        story.append(Paragraph('✦ FENÊTRES DE RENCONTRE ✦', self.title_style))
        story.append(Spacer(0, 0.2 * cm))
        story.append(Paragraph('Les Moments Cosmiques Favorables à ta Rencontre', self.subtitle_style))
        story.append(Spacer(0, 0.8 * cm))
        story.append(Paragraph(
            'L\'univers crée des fenêtres temporelles pour te rapprocher '
            'de ta personne destinée. Découvre quand frapper à la porte du destin.',
            self.body_style,
        ))
        story.append(Spacer(0, 1.2 * cm))
        story.append(Paragraph('par Solena — La voix de Plume Astrale', ParagraphStyle(
            'Footer', fontName='Helvetica-Oblique', fontSize=10, textColor=GOLD_LIGHT, alignment=TA_CENTER
        )))
        story.append(Spacer(0, 1 * cm))
        
        # Filler image
        filler = self._add_filler_image(2.5 * cm)
        if filler:
            filler_table = Table([[filler]], colWidths=[3 * cm])
            filler_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTER'), ('BACKGROUND', (0, 0), (0, 0), colors.transparent)]))
            story.append(filler_table)
        
        return story
    
    def _page_intro(self) -> List:
        """Page 2: Introduction"""
        story = []
        
        img = self._load_image(self.TAROT_IMAGES['etoile'], 6.5 * cm, 8.5 * cm)
        if img:
            img_table = Table([[img]], colWidths=[6.5 * cm])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('BACKGROUND', (0, 0), (0, 0), colors.transparent),
            ]))
            story.append(img_table)
            story.append(Spacer(0, 0.3 * cm))
        
        story.append(Paragraph('Comprendre les Fenêtres de Rencontre', self.heading_style))
        story.append(Spacer(0, 0.2 * cm))
        story.append(Paragraph(
            'Une fenêtre de rencontre est une période où l\'univers aligne les énergies '
            'pour ta rencontre destinée.<br/><br/>'
            '• <b>Transits de Vénus</b> — amour et attraction<br/>'
            '• <b>Transits de Jupiter</b> — expansion et rencontres<br/>'
            '• <b>Phases Lunaires</b> — intentions et manifestations',
            self.body_style,
        ))
        story.append(Spacer(0, 0.8 * cm))
        
        filler = self._add_filler_image(2 * cm)
        if filler:
            filler_table = Table([[filler]], colWidths=[3 * cm])
            filler_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTER'), ('BACKGROUND', (0, 0), (0, 0), colors.transparent)]))
            story.append(filler_table)
        
        return story
    
    def _page_window(self, window: Dict[str, Any], index: int) -> List:
        """Page pour une fenêtre spécifique"""
        story = []
        
        window_type = window.get('kind', f'Fenêtre {index}')
        description = window.get('text', 'Période d\'opportunités.')
        
        tarot_keys = ['amoureux', 'soleil', 'lune']
        img = self._load_image(self.TAROT_IMAGES.get(tarot_keys[index - 1], 'amoureux'), 6.5 * cm, 8.5 * cm)
        
        if img:
            img_table = Table([[img]], colWidths=[6.5 * cm])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('BACKGROUND', (0, 0), (0, 0), colors.transparent),
            ]))
            story.append(img_table)
            story.append(Spacer(0, 0.3 * cm))
        
        story.append(Paragraph(window_type, self.heading_style))
        story.append(Spacer(0, 0.2 * cm))
        story.append(Paragraph(description, self.body_style))
        story.append(Spacer(0, 1 * cm))
        
        filler = self._add_filler_image(2 * cm)
        if filler:
            filler_table = Table([[filler]], colWidths=[3 * cm])
            filler_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTER'), ('BACKGROUND', (0, 0), (0, 0), colors.transparent)]))
            story.append(filler_table)
        
        return story
    
    def _page_manifestation(self) -> List:
        """Page 6: Manifestation"""
        story = []
        story.append(Paragraph('Manifeste Ta Rencontre en 3 Étapes', self.heading_style))
        story.append(Spacer(0, 0.2 * cm))
        story.append(Paragraph(
            '<b>1️⃣ CLARITÉ</b> — Sais exactement ce que tu veux<br/><br/>'
            '<b>2️⃣ VIBRATION</b> — Sois la fréquence que tu attires<br/><br/>'
            '<b>3️⃣ ACTION</b> — Sors de ta zone de confort',
            self.body_style,
        ))
        story.append(Spacer(0, 1.2 * cm))
        
        filler = self._add_filler_image(3 * cm)
        if filler:
            filler_table = Table([[filler]], colWidths=[3 * cm])
            filler_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTER'), ('BACKGROUND', (0, 0), (0, 0), colors.transparent)]))
            story.append(filler_table)
        
        return story
    
    def _page_transits_bonus(self, birth_date_iso: str) -> List:
        """Page 7: Transits"""
        story = []
        story.append(Paragraph('✦ Les Énergies Cosmiques ✦', self.heading_style))
        story.append(Spacer(0, 0.2 * cm))
        story.append(Paragraph(
            '<b>Vénus en Transit</b> — Plus magnétique, plus rayonnant<br/><br/>'
            '<b>Jupiter</b> — L\'expanseur cosmique<br/><br/>'
            '<b>Lune Nouvelle</b> — L\'intention<br/>'
            '<b>Lune Pleine</b> — La manifestation',
            self.body_style,
        ))
        story.append(Spacer(0, 1.2 * cm))
        
        filler = self._add_filler_image(2.5 * cm)
        if filler:
            filler_table = Table([[filler]], colWidths=[3 * cm])
            filler_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTER'), ('BACKGROUND', (0, 0), (0, 0), colors.transparent)]))
            story.append(filler_table)
        
        return story
    
    def _page_rituels_avances(self) -> List:
        """Page 8: Rituels"""
        story = []
        story.append(Paragraph('Rituels pour Activer les Fenêtres', self.heading_style))
        story.append(Spacer(0, 0.2 * cm))
        story.append(Paragraph(
            '<b>Rituels d\'activation</b> pour magnifier ton énergie et attirer la rencontre destinée.',
            self.body_style,
        ))
        story.append(Spacer(0, 1.5 * cm))
        
        filler = self._add_filler_image(2.5 * cm)
        if filler:
            filler_table = Table([[filler]], colWidths=[3 * cm])
            filler_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTER'), ('BACKGROUND', (0, 0), (0, 0), colors.transparent)]))
            story.append(filler_table)
        
        return story
    
    def _page_cristaux(self) -> List:
        """Page 9: Cristaux"""
        story = []
        story.append(Paragraph('Cristaux pour L\'Amour', self.heading_style))
        story.append(Spacer(0, 0.2 * cm))
        story.append(Paragraph(
            '<b>Rose Quartz</b> — Ouverture du cœur<br/>'
            '<b>Rhodonite</b> — Amour et compassion<br/>'
            '<b>Tourmaline Rose</b> — Douceur et tendresse',
            self.body_style,
        ))
        story.append(Spacer(0, 1.5 * cm))
        
        filler = self._add_filler_image(2.5 * cm)
        if filler:
            filler_table = Table([[filler]], colWidths=[3 * cm])
            filler_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTER'), ('BACKGROUND', (0, 0), (0, 0), colors.transparent)]))
            story.append(filler_table)
        
        return story
    
    def _page_affirmations_finales(self, name: str) -> List:
        """Page 10: Affirmations finales"""
        story = []
        story.append(Paragraph('✦ Tes Affirmations Quotidiennes ✦', self.heading_style))
        story.append(Spacer(0, 0.2 * cm))
        
        affirmations_text = '<br/>'.join([f'<b>"{aff}"</b>' for aff in self.affirmations]) if self.affirmations else (
            '<b>"Je suis magnétique et attirant(e)."</b><br/>'
            '<b>"L\'univers m\'apporte la rencontre parfaite."</b><br/>'
            '<b>"Je mérite un amour vrai et conscient."</b>'
        )
        
        story.append(Paragraph(affirmations_text, self.body_style))
        story.append(Spacer(0, 0.8 * cm))
        
        story.append(Paragraph(
            f'Chère {name}, tu as le pouvoir d\'attirer ta rencontre destinée. '
            'Les étoiles veillent sur toi.',
            ParagraphStyle('Conclusion', fontName='Helvetica-Oblique', fontSize=10,
                          textColor=CREAM, alignment=TA_CENTER, leading=14)
        ))
        
        return story

def generate_fenetre_rencontre_pdf(
    first_name: str,
    birth_date_iso: str,
    windows_data: List[Dict[str, Any]],
    synastry_data: Optional[Dict[str, Any]] = None,
    affirmations: Optional[List[str]] = None,
) -> bytes:
    """Génère le PDF avec fond violet garanti"""
    return FenetreRencontrePDFGenerator().generate(
        first_name=first_name,
        birth_date_iso=birth_date_iso,
        windows_data=windows_data,
        synastry_data=synastry_data,
        affirmations=affirmations,
    )
