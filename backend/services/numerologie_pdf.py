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

from services.pdf_bg import make_bg_canvas
from services.pdf_theme import register_fonts as _register_luxury_fonts

# Enregistre la police OrnamentSerif (FreeSerif) au chargement du module afin que
# tout `<font name="OrnamentSerif">` inline dans les Paragraph soit résolu.
_register_luxury_fonts()

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
        ai_sections: Optional[Dict[str, str]] = None,
        referral_code: Optional[str] = None,
        referral_link: Optional[str] = None,
    ) -> bytes:
        """Génère le PDF complet (12 pages).

        ai_sections : dict optionnel de narratifs enrichis (introduction,
        chemin_de_vie, destinee, ame, personnalite, jour_naissance,
        annee_personnelle, lo_shu, biorythmes, invitation_finale).
        """
        self._ai = ai_sections or {}
        _mini_styles = {
            'caption': self.subtitle_style,
            'h2': self.heading_style,
            'title': self.title_style,
            'subtitle': self.subtitle_style,
        }

        from services.pdf_multipass_toc import build_with_toc, chapter_marker
        from services.pdf_prestige import toc_page as _toc_page, chapter_opener as _chapter_opener

        def _build_story(page_map):
            story = []
            story.extend(self._page_cover(first_name))
            story.append(PageBreak())

            def _pg(cid, fb=None):
                return page_map.get(cid, fb) if page_map is not None else fb

            _toc_page(story, _mini_styles, [
                {'roman': 'I',    'title': "Introduction à la numérologie sacrée", 'page': _pg('chap1')},
                {'roman': 'II',   'title': "Tes nombres-clés",                     'page': _pg('chap2')},
                {'roman': 'III',  'title': "Ton année personnelle",                'page': _pg('chap3')},
                {'roman': 'IV',   'title': "Prévisions cycliques",                 'page': _pg('chap4')},
                {'roman': 'V',    'title': "Ton Carré Lo-Shu",                     'page': _pg('chap5')},
                {'roman': 'VI',   'title': "Rituels de vibration",                 'page': _pg('chap6')},
                {'roman': 'VII',  'title': "Compatibilités numériques",            'page': _pg('chap7')},
                {'roman': 'VIII', 'title': "Affirmations & Mantras",               'page': _pg('chap8')},
                {'roman': 'IX',   'title': "Journal des vibrations",               'page': _pg('chap9')},
            ])

            story.append(chapter_marker('chap1'))
            _chapter_opener(story, _mini_styles, 'I', "La numérologie sacrée", "Une invitation aux nombres")
            story.extend(self._page_intro())
            story.append(PageBreak())

            story.append(chapter_marker('chap2'))
            _chapter_opener(story, _mini_styles, 'II', "Tes nombres-clés", "Chemin de vie, expression, âme")
            story.extend(self._pages_nombres_cles(numerology_data, first_name))
            story.append(PageBreak())

            if personal_year_data:
                story.append(chapter_marker('chap3'))
                _chapter_opener(story, _mini_styles, 'III', "Ton année personnelle", "Le cycle actif de ta vie")
                story.extend(self._pages_annee_personnelle(personal_year_data))
                story.append(PageBreak())

            if forecast_data:
                story.append(chapter_marker('chap4'))
                _chapter_opener(story, _mini_styles, 'IV', "Prévisions cycliques", "Ton horizon numérologique")
                story.extend(self._pages_forecast(forecast_data))
                story.append(PageBreak())

            if self._ai.get('lo_shu'):
                story.append(chapter_marker('chap5'))
                _chapter_opener(story, _mini_styles, 'V', "Ton Carré Lo-Shu", "Numérologie chinoise ancestrale")
                story.append(Paragraph('<font name="OrnamentSerif">✦</font> Ton Carré Lo-Shu — Numérologie Chinoise <font name="OrnamentSerif">✦</font>', self.heading_style))
                story.append(Spacer(0, 0.3 * cm))
                story.append(Paragraph(self._ai['lo_shu'], self.body_style))
                story.append(PageBreak())

            if self._ai.get('biorythmes'):
                story.append(Paragraph('<font name="OrnamentSerif">✦</font> Tes Biorythmes des 90 Prochains Jours <font name="OrnamentSerif">✦</font>', self.heading_style))
                story.append(Spacer(0, 0.3 * cm))
                story.append(Paragraph(self._ai['biorythmes'], self.body_style))
                story.append(PageBreak())

            if self._ai.get('invitation_finale'):
                story.append(Paragraph('<font name="OrnamentSerif">✦</font> Ton Invitation <font name="OrnamentSerif">✦</font>', self.heading_style))
                story.append(Spacer(0, 0.3 * cm))
                story.append(Paragraph(self._ai['invitation_finale'], self.body_style))
                story.append(PageBreak())

            story.append(chapter_marker('chap6'))
            _chapter_opener(story, _mini_styles, 'VI', "Rituels de vibration", "Cinq pratiques numérologiques")
            story.extend(self._page_rituels_finaux(first_name))
            story.append(PageBreak())

            story.append(chapter_marker('chap7'))
            _chapter_opener(story, _mini_styles, 'VII', "Compatibilités numériques", "Ta résonance avec les autres")
            story.extend(self._page_compatibilites(numerology_data, first_name))
            story.append(PageBreak())

            story.append(chapter_marker('chap8'))
            _chapter_opener(story, _mini_styles, 'VIII', "Affirmations & Mantras", "Sept phrases pour t'ancrer")
            story.extend(self._page_affirmations_numo(first_name))
            story.append(PageBreak())

            story.append(chapter_marker('chap9'))
            _chapter_opener(story, _mini_styles, 'IX', "Journal des vibrations", "Trois prompts pour intégrer")
            story.extend(self._page_journal_numo(first_name))

            # ═══ Colophon Nocturne — dernière page ═══
            story.append(PageBreak())
            from services.pdf_colophon import build_colophon
            build_colophon(
                story, _mini_styles, prenom=first_name,
                referral_code=referral_code, referral_link=referral_link,
                product_name='Ton Code Numérologique',
            )
            return story

        return build_with_toc(
            _build_story,
            doc_kwargs={
                'pagesize': A4,
                'topMargin': 1.5 * cm, 'bottomMargin': 1.5 * cm,
                'leftMargin': 1.5 * cm, 'rightMargin': 1.5 * cm,
            },
            on_first_page=make_bg_canvas('Ton Analyse Numérologique'),
            on_later_pages=make_bg_canvas('Ton Analyse Numérologique'),
        )

    def _page_cover(self, name: str) -> List:
        """Couverture prestige avec hero illustré (chemin de vie)."""
        from reportlab.platypus import Image as _RLImage
        from pathlib import Path as _Path
        elements: List = [Spacer(0, 1.5 * cm)]
        _hero = _Path('/app/backend/assets/pdf_covers/numerologie_hero.png')
        if _hero.exists():
            try:
                img = _RLImage(str(_hero), width=8 * cm, height=8 * cm, kind='proportional')
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(0, 0.4 * cm))
            except Exception:
                pass
        elements.extend([
            Paragraph('<font name="OrnamentSerif">✦</font> TON CODE NUMÉROLOGIQUE <font name="OrnamentSerif">✦</font>', self.title_style),
            Spacer(0, 0.5 * cm),
            Paragraph(f'Destinée, Cycles & Vibrations', self.subtitle_style),
            Spacer(0, 0.9 * cm),
        ])
        # ═══ Nom du destinataire en dorure gaufrée ═══
        from services.pdf_cover_personalization import embossed_name as _embossed
        _embossed(elements, name, size='large')
        elements.extend([
            Spacer(0, 0.6 * cm),
            Paragraph(
                'Chaque nombre vibre avec une essence cosmique.<br/>Ta date de naissance révèle tes cycles karmiques.',
                self.body_style,
            ),
            Spacer(0, 1 * cm),
            Paragraph('par Solena — La voix de Plume Astrale', ParagraphStyle(
                'Footer', fontName='Helvetica-Oblique', fontSize=10, textColor=GOLD_LIGHT, alignment=TA_CENTER
            )),
        ])
        return elements
    
    def _page_intro(self) -> List:
        """Introduction à la numérologie sacrée."""
        if getattr(self, '_ai', {}).get('introduction'):
            return [
                Paragraph('Bienvenue dans ton Univers Numéral', self.heading_style),
                Spacer(0, 0.3 * cm),
                Paragraph(self._ai['introduction'], self.body_style),
            ]
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
        """Détail des 3 nombres principaux — chacun sur sa page (3 pages)."""
        story = []
        story.append(Paragraph('Tes Nombres Clés', self.heading_style))

        # Extrait données (peut varier selon format API)
        destiny_num = data.get('destiny_number', 1)
        expression_num = data.get('expression_number', 1)
        heart_num = data.get('heart_number', 1)

        ai = getattr(self, '_ai', {})
        # Mapping label affiché → clé narrative IA correspondante
        entries = [
            ('Nombre de Destin', str(destiny_num), 'chemin_de_vie'),
            ('Nombre d\'Expression', str(expression_num), 'destinee'),
            ('Nombre de Cœur', str(heart_num), 'ame'),
        ]

        for i, (title, num, ai_key) in enumerate(entries):
            if i > 0:
                # Chaque nombre-clé mérite sa page dédiée (respect de la promesse
                # marketing 16 pages minimum + confort de lecture).
                story.append(PageBreak())

            num_clean = num.split('/')[0] if '/' in num else num  # Gère '11/2' format
            label, description = NOMBRES_FR.get(num_clean, ('Inconnu', 'Vibration secrète'))

            story.append(Paragraph(f'<b>{title}</b> : {label} — Vibration {num}', self.heading_style))
            # Narratif IA prioritaire (plusieurs paragraphes), fallback description courte
            narrative = ai.get(ai_key) or description
            story.append(Paragraph(narrative, self.body_style))

            # Ne pas ajouter la ligne générique si IA a déjà fourni un long narratif
            if not ai.get(ai_key):
                story.append(Paragraph(
                    f'La vibration du <b>{num}</b> te pousse vers une destinée '
                    'unique. Explore cette énergie pour manifester ton potentiel.',
                    self.body_style,
                ))
            # Ancrage rituel bref au bas de chaque page-nombre (crédibilité éditoriale)
            story.append(Spacer(0, 0.4 * cm))
            story.append(Paragraph(
                f'<i>Ancrage — laisse cette vibration résonner en toi. Où la retrouves-tu '
                f'dans tes journées actuelles ?</i>',
                self.body_style,
            ))

        # Section bonus : nombres complémentaires (personnalité + jour de naissance)
        # Ces sections n'apparaissent que si l'IA a enrichi
        if ai.get('personnalite'):
            story.append(PageBreak())
            story.append(Paragraph('<b>Nombre de Personnalité</b> — L\'image que tu projettes', self.heading_style))
            story.append(Paragraph(ai['personnalite'], self.body_style))

        if ai.get('jour_naissance'):
            story.append(PageBreak())
            story.append(Paragraph('<b>Nombre du Jour de Naissance</b> — Ton talent inné', self.heading_style))
            story.append(Paragraph(ai['jour_naissance'], self.body_style))

        return story
    
    def _pages_annee_personnelle(self, data: Dict[str, Any]) -> List:
        """Analyse année personnelle (cycle annuel)."""
        story = []
        story.append(Paragraph('Ton Année Personnelle', self.heading_style))
        
        current_year_num = data.get('personal_year', 1)
        ai_narrative = getattr(self, '_ai', {}).get('annee_personnelle')
        
        story.append(Paragraph(
            f'Année numérale <b>{current_year_num}</b>',
            self.heading_style,
        ))
        
        if ai_narrative:
            # Narratif IA long (3 paragraphes)
            story.append(Paragraph(ai_narrative, self.body_style))
        else:
            year_description = data.get('year_description', 'Année de transformation.')
            story.append(Paragraph(year_description, self.body_style))
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
                '─ <font name="OrnamentSerif">✦</font> ─<br/><br/>'
                'Ce chemin numéral est ton secret cosmique.<br/>'
                f'À bientôt, {name}.<br/><br/>'
                '<i>Solena — La voix de Plume Astrale</i>',
                ParagraphStyle(
                    'Signature', fontName='Helvetica-Oblique', fontSize=11,
                    textColor=GOLD, alignment=TA_CENTER, leading=14
                ),
            ),
        ]

    def _page_compatibilites(self, data: Dict[str, Any], name: str) -> List:
        """Compatibilités numérologiques — carte des affinités selon les nombres."""
        destiny_num = data.get('destiny_number', 1)
        num_clean = str(destiny_num).split('/')[0]
        # Table simplifiée des affinités (numérologie classique)
        AFFINITIES = {
            '1': ('3, 5, 6', "les créatifs, les libres, les aimants"),
            '2': ('1, 4, 8', "les leaders, les bâtisseurs, les stratèges"),
            '3': ('1, 5, 7', "les entrepreneurs, les aventuriers, les sages"),
            '4': ('2, 6, 8', "les diplomates, les protecteurs, les puissants"),
            '5': ('1, 3, 7', "les leaders, les créatifs, les mystiques"),
            '6': ('2, 3, 9', "les diplomates, les créatifs, les humanistes"),
            '7': ('3, 5, 9', "les créatifs, les libres, les humanistes"),
            '8': ('2, 4, 6', "les diplomates, les bâtisseurs, les protecteurs"),
            '9': ('3, 6, 7', "les créatifs, les protecteurs, les sages"),
            '11': ('2, 4, 22', "les diplomates, les bâtisseurs, les visionnaires"),
            '22': ('4, 8, 11', "les bâtisseurs, les puissants, les intuitifs"),
            '33': ('6, 9, 11', "les protecteurs, les humanistes, les intuitifs"),
        }
        aff_nums, aff_desc = AFFINITIES.get(num_clean, ('3, 5, 7', "les âmes qui résonnent"))

        return [
            Paragraph('Avec qui résonnes-tu ?', self.heading_style),
            Spacer(0, 0.3 * cm),
            Paragraph(
                f'{name}, avec ton nombre de destin <b>{destiny_num}</b>, tu vibres particulièrement '
                f'en présence des personnes dont le nombre est <b>{aff_nums}</b> — {aff_desc}.',
                self.body_style,
            ),
            Spacer(0, 0.5 * cm),
            Paragraph(
                'Cela ne signifie pas que les autres nombres sont exclus — la numérologie '
                'ne dresse pas de barrière. Elle éclaire simplement les résonances naturelles, '
                'celles où le dialogue s\'installe sans effort, où les projets se déploient '
                'sans friction inutile.',
                self.body_style,
            ),
            Spacer(0, 0.7 * cm),
            Paragraph('<b>Trois clés de compatibilité</b>', self.heading_style),
            Paragraph(
                '<b>I. Amitié</b> — Cherche des personnes dont le nombre de destin partage '
                'les mêmes racines vibratoires que le tien. Vous n\'aurez pas besoin d\'expliquer.<br/><br/>'
                '<b>II. Amour</b> — Compare vos <i>nombres de cœur</i> plutôt que vos destins. '
                'C\'est là que se joue l\'intimité profonde.<br/><br/>'
                '<b>III. Travail</b> — Choisis un partenaire dont le nombre d\'<i>expression</i> '
                'complète le tien. Vous couvrirez ensemble un spectre plus large.',
                self.body_style,
            ),
            Spacer(0, 0.6 * cm),
            Paragraph(
                '<i>Note dans ton journal les trois personnes avec qui tu résonnes le plus '
                'aujourd\'hui. Vérifie leurs nombres — souvent, la carte confirme ce que ton '
                'corps sait déjà.</i>',
                self.body_style,
            ),
        ]

    def _page_affirmations_numo(self, name: str) -> List:
        """Sept affirmations numérologiques calibrées."""
        return [
            Paragraph('Sept affirmations pour tes vibrations', self.heading_style),
            Spacer(0, 0.4 * cm),
            Paragraph(
                '<i>Choisis-en une par matin. Répète-la trois fois à voix basse, la main sur '
                'le sternum. Les nombres sont des fréquences — ta voix les active.</i>',
                self.body_style,
            ),
            Spacer(0, 0.6 * cm),
            Paragraph(
                '<b>I.</b>  Je suis en résonance avec les nombres qui composent mon être.<br/><br/>'
                '<b>II.</b>  Ma date de naissance n\'est pas un hasard — c\'est un code.<br/><br/>'
                '<b>III.</b>  Je manifeste avec grâce ce que ma vibration attire à moi.<br/><br/>'
                '<b>IV.</b>  Chaque cycle numérique est une invitation, jamais une contrainte.<br/><br/>'
                '<b>V.</b>  J\'accueille les défis de mon année personnelle comme des enseignements.<br/><br/>'
                '<b>VI.</b>  Mon Nombre de Cœur est ma vérité intime — je le respecte, je l\'écoute.<br/><br/>'
                f'<b>VII.</b>  {name}, je suis unique, calibrée, alignée. Rien ne me manque.',
                ParagraphStyle(
                    'affirm_numo', fontName='Helvetica-Oblique', fontSize=11.5,
                    textColor=CREAM, alignment=TA_LEFT, leading=17, spaceAfter=6,
                ),
            ),
        ]

    def _page_journal_numo(self, name: str) -> List:
        """Trois prompts d'écriture numérologique."""
        return [
            Paragraph('Trois prompts pour intégrer tes nombres', self.heading_style),
            Spacer(0, 0.4 * cm),
            Paragraph(
                '<i>Un carnet, une lumière tamisée, dix minutes. Réponds sans réfléchir — '
                'la première image qui vient est la bonne.</i>',
                self.body_style,
            ),
            Spacer(0, 0.7 * cm),
            Paragraph(
                '<b>Prompt 1 — La vibration dominante</b><br/>'
                'Où, dans ma vie actuelle, ma vibration principale s\'exprime-t-elle le plus '
                'librement ? Où est-elle bridée ?',
                self.body_style,
            ),
            Spacer(0, 0.3 * cm),
            Paragraph(
                '<font color="#9089B5">'
                '________________________________________________________<br/>'
                '________________________________________________________<br/>'
                '________________________________________________________'
                '</font>',
                self.body_style,
            ),
            Spacer(0, 0.7 * cm),
            Paragraph(
                '<b>Prompt 2 — Le cycle en cours</b><br/>'
                'Que m\'apprend cette année personnelle ? Quelle décision différée par peur '
                'suis-je invitée à prendre maintenant ?',
                self.body_style,
            ),
            Spacer(0, 0.3 * cm),
            Paragraph(
                '<font color="#9089B5">'
                '________________________________________________________<br/>'
                '________________________________________________________<br/>'
                '________________________________________________________'
                '</font>',
                self.body_style,
            ),
            Spacer(0, 0.7 * cm),
            Paragraph(
                '<b>Prompt 3 — L\'ancrage</b><br/>'
                f'{name}, quelle est la plus petite habitude quotidienne qui incarne ma '
                'vibration idéale ? Puis-je la commencer demain matin ?',
                self.body_style,
            ),
            Spacer(0, 0.3 * cm),
            Paragraph(
                '<font color="#9089B5">'
                '________________________________________________________<br/>'
                '________________________________________________________<br/>'
                '________________________________________________________'
                '</font>',
                self.body_style,
            ),
        ]


def generate_numerologie_pdf(
    first_name: str,
    birth_date_iso: str,
    numerology_data: Dict[str, Any],
    personal_year_data: Optional[Dict[str, Any]] = None,
    forecast_data: Optional[Dict[str, Any]] = None,
    ai_sections: Optional[Dict[str, str]] = None,
    referral_code: Optional[str] = None,
    referral_link: Optional[str] = None,
) -> bytes:
    """Wrapper pour générer le PDF numérologie (accepte ai_sections optionnel)."""
    return NumerologiePDFGenerator().generate(
        first_name=first_name,
        birth_date_iso=birth_date_iso,
        numerology_data=numerology_data,
        personal_year_data=personal_year_data,
        forecast_data=forecast_data,
        ai_sections=ai_sections,
        referral_code=referral_code,
        referral_link=referral_link,
    )


async def generate_numerologie_pdf_ai(
    first_name: str,
    birth_date_iso: str,
    numerology_data: Dict[str, Any],
    personal_year_data: Optional[Dict[str, Any]] = None,
    forecast_data: Optional[Dict[str, Any]] = None,
    referral_code: Optional[str] = None,
    referral_link: Optional[str] = None,
) -> bytes:
    """Génère le PDF Numérologie AVEC enrichissement IA transverse.
    Fallback silencieux sur le texte générique si l'IA échoue."""
    try:
        from services.report_ai_enrichment import enrich_report
        context = {
            'numerology': numerology_data,
            'personal_year': personal_year_data,
            'forecast': forecast_data,
        }
        ai_sections = await enrich_report(
            report_type='numerology',
            prenom=first_name,
            birth_date_iso=birth_date_iso,
            context=context,
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f'[numerologie] AI enrich fail: {e}')
        ai_sections = {}
    return NumerologiePDFGenerator().generate(
        first_name=first_name,
        birth_date_iso=birth_date_iso,
        numerology_data=numerology_data,
        personal_year_data=personal_year_data,
        forecast_data=forecast_data,
        ai_sections=ai_sections,
        referral_code=referral_code,
        referral_link=referral_link,
    )
