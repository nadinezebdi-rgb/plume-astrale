"""
Générateur PDF "Fenêtres de Rencontre Avancées" — 10 pages.
Fenêtres de rencontre calculées via transits + synastrie (si 2 thèmes).
Images cosmiques + calculs détaillés + conseils d'activation.
"""
from __future__ import annotations
from io import BytesIO
from typing import Any, Dict, List, Optional
import requests
from urllib.request import urlopen

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, PageTemplate, Frame,
)
from reportlab.pdfgen import canvas
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
    
    # Images tarot de la library (HD 1080px)
    TAROT_IMAGES = {
        'amoureux': 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library/tarot/06_les_amoureux_1080.png',
        'etoile': 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library/tarot/17_l_etoile_1080.png',
        'soleil': 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library/tarot/19_le_soleil_1080.png',
        'lune': 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library/tarot/18_la_lune_1080.png',
        'imperatrice': 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library/tarot/03_l_imperatrice_1080.png',
    }
    
    VIOLET_DARK = colors.HexColor('#2D1B4E')  # Fond violet foncé cosmique
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.affirmations = []  # Stocker les affirmations
        self._setup_styles()
    
    def _add_background(self, canvas_obj, doc):
        """Ajoute un fond violet foncé à chaque page."""
        canvas_obj.saveState()
        canvas_obj.setFillColor(self.VIOLET_DARK)
        canvas_obj.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
        canvas_obj.restoreState()
    
    def _draw_violet_background(self, canvas_obj, doc):
        """Callback pour ajouter le fond."""
        self._add_background(canvas_obj, doc)
    
    def _load_image(self, url: str, width: float, height: float) -> Optional[Image]:
        """Charge une image depuis une URL."""
        try:
            img_data = BytesIO(urlopen(url).read())
            img = Image(img_data, width=width, height=height)
            return img
        except Exception as e:
            print(f"⚠️ Impossible de charger l'image: {e}")
            return None
    
    def _setup_styles(self):
        """Styles personnalisés."""
        self.title_style = ParagraphStyle(
            'Title',
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=CREAM,  # ✅ Blanc/lisible au lieu de GOLD
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        self.heading_style = ParagraphStyle(
            'Heading',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=LAVENDER,  # ✅ Garde la lavande (lisible)
            spaceAfter=8,
            spaceBefore=12,
            alignment=TA_CENTER,
        )
        self.body_style = ParagraphStyle(
            'Body',
            fontName='Helvetica',
            fontSize=11,
            textColor=CREAM,  # ✅ Blanc (lisible)
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            leading=16,
        )
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            fontName='Helvetica-Oblique',
            fontSize=13,
            textColor=GOLD_LIGHT,  # ✅ Garde la couleur accent
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
        """Génère le PDF (10 pages réelles avec fond violet en arrière-plan)."""
        # Stocker les affirmations
        self.affirmations = affirmations or []
        
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
        )
        
        # Template pour ajouter fond violet EN ARRIÈRE-PLAN
        class VioletPageTemplate(PageTemplate):
            def __init__(self, *args, generator=None, **kwargs):
                self.generator = generator
                super().__init__(*args, **kwargs)
            
            def beforeDrawPage(self, canvas_obj, doc):
                """Appel AVANT de dessiner le contenu - c'est ici qu'on met le fond"""
                canvas_obj.saveState()
                canvas_obj.setFillColor(self.generator.VIOLET_DARK)
                # Remplir toute la page
                canvas_obj.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
                canvas_obj.restoreState()
        
        # Créer un Frame pour le contenu
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
        
        # Page 2: Introduction complète
        story.extend(self._page_intro())
        story.append(PageBreak())
        
        # Pages 3-5: Fenêtres détaillées (3 pages)
        for i, window in enumerate(windows_data[:3]):  # Max 3 fenêtres
            story.extend(self._page_window(window, i + 1))
            if i < 2:  # PageBreak entre les fenêtres
                story.append(PageBreak())
        
        story.append(PageBreak())
        
        # Page 6: Conseils pratiques pour manifester
        story.extend(self._page_manifestation())
        story.append(PageBreak())
        
        # Page 7: Synastrie (si données) ou page bonus
        if synastry_data:
            story.extend(self._page_synastrie(synastry_data))
        else:
            story.extend(self._page_transits_bonus(birth_date_iso))
        story.append(PageBreak())
        
        # Page 8: Rituels d'activation avancés
        story.extend(self._page_rituels_avances())
        story.append(PageBreak())
        
        # Page 9: Cristaux et pierres énergétiques
        story.extend(self._page_cristaux())
        story.append(PageBreak())
        
        # Page 10: Affirmations quotidiennes + Conclusion
        story.extend(self._page_affirmations_finales(first_name))
        
        doc.build(story)
        return buffer.getvalue()
    
    def _page_cover(self, name: str) -> List:
        """Couverture mystique avec image tarot XXL."""
        story = []
        story.append(Spacer(0, 0.8 * cm))
        
        # Image tarot GRANDE (6.5cm x 8.5cm - 2x plus grande)
        img = self._load_image(self.TAROT_IMAGES['amoureux'], 6.5 * cm, 8.5 * cm)
        if img:
            img_table = Table([[img]], colWidths=[6.5 * cm])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (0, 0), colors.transparent),
            ]))
            story.append(img_table)
            story.append(Spacer(0, 0.8 * cm))
        
        story.append(Paragraph('✦ FENÊTRES DE RENCONTRE ✦', self.title_style))
        story.append(Spacer(0, 0.3 * cm))
        story.append(Paragraph('Les Moments Cosmiques Favorables à ta Rencontre', self.subtitle_style))
        story.append(Spacer(0, 1 * cm))
        story.append(Paragraph(
            'L\'univers crée des fenêtres temporelles pour te rapprocher<br/>'
            'de ta personne destinée. Découvre quand frapper à la porte du destin.',
            self.body_style,
        ))
        story.append(Spacer(0, 1.5 * cm))
        story.append(Paragraph('par Solena — La voix de Plume Astrale', ParagraphStyle(
            'Footer', fontName='Helvetica-Oblique', fontSize=10, textColor=GOLD_LIGHT, alignment=TA_CENTER
        )))
        
        return story
    
    def _page_intro(self) -> List:
        """Introduction aux fenêtres avec image grande."""
        story = []
        
        # Image tarot GRANDE (6.5cm x 8.5cm)
        img = self._load_image(self.TAROT_IMAGES['etoile'], 6.5 * cm, 8.5 * cm)
        if img:
            img_table = Table([[img]], colWidths=[6.5 * cm])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('BACKGROUND', (0, 0), (0, 0), colors.transparent),
            ]))
            story.append(img_table)
            story.append(Spacer(0, 0.5 * cm))
        
        story.append(Paragraph('Comprendre les Fenêtres de Rencontre', self.heading_style))
        story.append(Spacer(0, 0.3 * cm))
        story.append(Paragraph(
            'Une fenêtre de rencontre est une période temporelle où l\'univers aligne '
            'les énergies pour te permettre de rencontrer ta personne de destinée.<br/><br/>'
            'Ces fenêtres sont calculées selon :<br/>'
            '• <b>Transits de Vénus</b> — amour et attraction<br/>'
            '• <b>Transits de Jupiter</b> — expansion et nouvelles rencontres<br/>'
            '• <b>Phases Lunaires</b> — intentions et manifestations<br/>'
            '• <b>Ton thème natal</b> — tes périodes les plus magnétiques',
            self.body_style,
        ))
        story.append(Spacer(0, 0.5 * cm))
        story.append(Paragraph(
            '<b>⚠️ Important :</b> Une fenêtre ne signifie pas que tu vas rencontrer '
            'automatiquement quelqu\'un. Elle signifie que les énergies sont favorables. '
            'À toi de sortir, de rayonner, de croire.',
            self.body_style,
        ))
        
        return story
    
    def _page_window(self, window: Dict[str, Any], index: int) -> List:
        """Page pour une fenêtre spécifique avec image grande."""
        story = []
        
        window_type = window.get('kind', f'Fenêtre {index}')
        period = window.get('period', 'À déterminer')
        description = window.get('text', 'Période d\'opportunités.')
        
        # Sélectionner une image différente pour chaque fenêtre
        tarot_key = ['amoureux', 'soleil', 'lune'][index - 1] if index <= 3 else 'amoureux'
        img = self._load_image(self.TAROT_IMAGES.get(tarot_key, self.TAROT_IMAGES['amoureux']), 6.5 * cm, 8.5 * cm)
        
        if img:
            img_table = Table([[img]], colWidths=[6.5 * cm])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),                ('BACKGROUND', (0, 0), (0, 0), colors.transparent),            ]))
            story.append(img_table)
            story.append(Spacer(0, 0.5 * cm))
        
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
        """Analyse synastrie avec image grande."""
        story = []
        
        # Image tarot GRANDE (6.5cm x 8.5cm)
        img = self._load_image(self.TAROT_IMAGES['imperatrice'], 6.5 * cm, 8.5 * cm)
        if img:
            img_table = Table([[img]], colWidths=[6.5 * cm])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('BACKGROUND', (0, 0), (0, 0), colors.transparent),
            ]))
            story.append(img_table)
            story.append(Spacer(0, 0.5 * cm))
        
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
    
    def _page_manifestation(self) -> List:
        """Page 6: Conseils pratiques pour manifester."""
        story = []
        story.append(Paragraph('Manifeste Ta Rencontre en 3 Étapes', self.heading_style))
        story.append(Spacer(0, 0.3 * cm))
        
        story.append(Paragraph(
            '<b>1️⃣ CLARITÉ — Sais exactement ce que tu veux</b><br/>'
            'Écris une description de ta personne idéale. Non pas en termes physiques, '
            'mais en qualités : "Je cherche quelqu\'un de bienveillant, créatif et conscient."<br/><br/>'
            
            '<b>2️⃣ VIBRATION — Sois la fréquence que tu attires</b><br/>'
            'Tu attires ce que tu émets. Si tu cherches quelqu\'un de joyeux, sois joyeuse. '
            'Travaille sur ta confiance, ton estime de toi et ta paix intérieure.<br/><br/>'
            
            '<b>3️⃣ ACTION — Sors de ta zone de confort</b><br/>'
            'L\'univers envoie des signes, mais c\'est à toi d\'agir. Accepte les invitations, '
            'utilise les apps de rencontres, souris aux gens nouveaux.',
            
            self.body_style,
        ))
        
        return story
    
    def _page_transits_bonus(self, birth_date_iso: str) -> List:
        """Page 7 (bonus): Infos supplémentaires sur les transits actuels."""
        story = []
        story.append(Paragraph('✦ Les Énergies Cosmiques en Jeu ✦', self.heading_style))
        story.append(Spacer(0, 0.3 * cm))
        
        story.append(Paragraph(
            '<b>Vénus en Transit</b><br/>'
            'Vénus est la planète de l\'amour et du désir. Ses passages favorables '
            'créent des moments de magnétisme irrésistible. Tu es plus attirant(e), '
            'plus rayonnant(e), plus confiant(e).<br/><br/>'
            
            '<b>Jupiter, l\'Expanseur Cosmique</b><br/>'
            'Jupiter amplifie tout ce qu\'il touche. Quand il active ta Maison 7 (le couple), '
            'c\'est l\'invitation à ouvrir ton cœur. Les rencontres deviennent plus probables.<br/><br/>'
            
            '<b>La Lune Nouvelle — L\'Intention</b><br/>'
            'La Lune Nouvelle est le moment le plus puissant pour poser tes intentions. '
            'C\'est le moment de dire à l\'univers ce que tu désires.<br/><br/>'
            
            '<b>La Lune Pleine — La Manifestation</b><br/>'
            'La Lune Pleine amplifie tout. Si tu as semé l\'intention à la nouvelle, '
            'tu récoltes à la pleine.'
            
            , self.body_style,
        ))
        
        return story
    
    def _page_rituels_avances(self) -> List:
        """Page 8: Rituels avancés pour ouverture des fenêtres."""
        story = []
        
        img = self._load_image(self.TAROT_IMAGES['soleil'], 5 * cm, 6.5 * cm)
        if img:
            img_table = Table([[img]], colWidths=[5 * cm])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('BACKGROUND', (0, 0), (0, 0), colors.transparent),
            ]))
            story.append(img_table)
            story.append(Spacer(0, 0.3 * cm))
        
        story.append(Paragraph('Rituels Puissants pour Ouvrir les Portes', self.heading_style))
        story.append(Spacer(0, 0.3 * cm))
        
        story.append(Paragraph(
            '<b>🔮 Rituel du Miroir d\'Amour (7 minutes)</b><br/>'
            'Regarde-toi intensément dans un miroir avec tendresse. Vois toi magnifique, aimé(e), magnétique. '
            'Trace un cœur invisible sur le miroir. Dit 3 fois : "Je suis prêt(e) pour l\'amour."<br/><br/>'
            
            '<b>🕯️ Rituel de la Chandelle Rose & Dorée</b><br/>'
            'Allume une chandelle rose (amour) et une dorée (intention manifestée). '
            'Laisse-les brûler 20 minutes en visualisant ta rencontre parfaite.<br/><br/>'
            
            '<b💎 Ritual des Cristaux Amplificateurs</b><br/>'
            'Porte sur toi : Rose (amour), Citrine (manifestation), Quartz clair (intention). '
            'Pose-les sur ton cœur chaque soir pendant 5 minutes.'
            
            , self.body_style,
        ))
        
        return story
    
    def _page_cristaux(self) -> List:
        """Page 9: Cristaux et pierres énergétiques."""
        story = []
        story.append(Paragraph('✦ Les Cristaux de l\'Amour ✦', self.heading_style))
        story.append(Spacer(0, 0.3 * cm))
        
        story.append(Paragraph(
            '<b>Pierre de Rose</b><br/>'
            'La reine de l\'amour. Guérit les blessures du cœur, apaise les peurs d\'abandonnement, '
            'attire l\'amour vrai. Porte-la près de ton cœur.<br/><br/>'
            
            '<b>Citrine</b><br/>'
            'La pierre de la manifestation et de l\'abondance. Elle amplifie tes intentions et '
            'crée un magnétisme irrésistible. Place-la sur ta table de nuit.<br/><br/>'
            
            '<b>Quartz Clair</b><br/>'
            'Le cristal universel. Il amplifie l\'énergie de toute intention et purifie ton aura. '
            'Combine-le avec la rose pour un duo puissant.<br/><br/>'
            
            '<b>Tourmaline Rose</b><br/>'
            'Attire l\'amour spirituel et les connexions authentiques. Réduit la culpabilité et les regrets. '
            'Parfaite pour une rencontre consciente.'
            
            , self.body_style,
        ))
        
        return story
    
    def _page_affirmations_finales(self, name: str) -> List:
        """Page 10: Affirmations quotidiennes et conclusion."""
        story = []
        story.append(Paragraph('✦ Tes Affirmations Quotidiennes ✦', self.heading_style))
        story.append(Spacer(0, 0.3 * cm))
        
        story.append(Paragraph(
            'Récite ces affirmations chaque matin en te regardant dans les yeux :<br/><br/>',
            self.body_style,
        ))
        
        # Utiliser les affirmations enrichies ou les defaults
        if self.affirmations:
            affirmations_text = '<br/>'.join([f'<b>"{aff}"</b>' for aff in self.affirmations])
        else:
            affirmations_text = (
                '<b>"Je suis magnétique et attirant(e)."</b><br/>'
                '<b>"L\'univers m\'apporte la rencontre parfaite au moment parfait."</b><br/>'
                '<b>"Je mérite un amour vrai et conscient."</b><br/>'
                '<b>"Mon cœur est ouvert et lumineux."</b><br/>'
                '<b>"Je reconnais mon âme sœur dès que je la rencontre."</b><br/>'
                '<b>"Je suis prêt(e) à recevoir l\'amour."</b><br/>'
                '<b>"Chaque jour m\'rapproche de mon amour destiné."</b>'
            )
        
        story.append(Paragraph(affirmations_text + '<br/><br/>', self.body_style))
        
        story.append(Paragraph(
            '─ ✦ ─<br/><br/>'
            f'Chère {name}, tu as entre les mains la carte de ton destin amoureux. '
            'Ces fenêtres ne sont pas des promesses, ce sont des invitations. '
            'L\'univers t\'ouvre des portes ; à toi d\'y marcher avec confiance et rayonnement.<br/><br/>'
            
            'N\'oublie pas : tu n\'es jamais seule. Les étoiles veillent sur toi.<br/><br/>'
            
            '<i>Avec tout mon amour cosmique,</i><br/>'
            '<i>Solena — La voix de Plume Astrale</i>',
            
            ParagraphStyle(
                'Conclusion', fontName='Helvetica-Oblique', fontSize=10,
                textColor=CREAM, alignment=TA_CENTER, leading=14
            ),
        ))
        
        return story


def generate_fenetre_rencontre_pdf(
    first_name: str,
    birth_date_iso: str,
    windows_data: List[Dict[str, Any]],
    synastry_data: Optional[Dict[str, Any]] = None,
    affirmations: Optional[List[str]] = None,
) -> bytes:
    """Wrapper pour générer le PDF fenêtres avancées avec affirmations enrichies."""
    return FenetreRencontrePDFGenerator().generate(
        first_name=first_name,
        birth_date_iso=birth_date_iso,
        windows_data=windows_data,
        synastry_data=synastry_data,
        affirmations=affirmations,
    )
