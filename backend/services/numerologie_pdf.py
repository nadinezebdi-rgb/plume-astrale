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
from services.numerologie_cycles import build_cycles

# Enregistre la police OrnamentSerif (FreeSerif) au chargement du module afin que
# tout `<font name="OrnamentSerif">` inline dans les Paragraph soit résolu.
_register_luxury_fonts()

# Palette Plume Astrale
NIGHT       = colors.white
NIGHT_SOFT  = colors.HexColor('#F5F2EA')
GOLD        = colors.HexColor('#79570F')
GOLD_LIGHT  = colors.HexColor('#8A6418')
LAVENDER    = colors.HexColor('#514657')
CREAM       = colors.HexColor('#26242B')
MUTED       = colors.HexColor('#5E5A63')

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
        cycles: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """Génère le PDF complet (cycles, pinacles, Lo-Shu et biorythmes inclus).

        ai_sections : dict optionnel de narratifs enrichis (introduction,
        chemin_de_vie, destinee, ame, personnalite, jour_naissance,
        annee_personnelle, lo_shu, biorythmes, invitation_finale).
        """
        self._ai = ai_sections or {}
        self._cycles = cycles or {}
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

            cyc = self._cycles or {}
            chapters = [
                ('intro', "Introduction à la numérologie sacrée", "La numérologie sacrée", "Une invitation aux nombres", True),
                ('nombres', "Tes nombres-clés", "Tes nombres-clés", "Chemin de vie, expression, âme", True),
                ('annee', "Ton année personnelle", "Ton année personnelle", "Le cycle actif de ta vie", bool(personal_year_data)),
                ('mois', "Tes 12 prochains mois", "Mois par mois", "Ton horizon numérologique", bool(cyc.get('months'))),
                ('pinacles', "Tes grands cycles de vie & défis", "Pinacles & défis", "Les quatre saisons de ton existence", bool(cyc.get('pinnacles'))),
                ('forecast', "Prévisions cycliques", "Prévisions cycliques", "Ton horizon numérologique", bool(forecast_data)),
                ('loshu', "Ton Carré Lo-Shu", "Ton Carré Lo-Shu", "Numérologie chinoise ancestrale", bool(cyc.get('lo_shu')) or bool(self._ai.get('lo_shu'))),
                ('karma', "Dettes karmiques & leçons", "Dettes karmiques & leçons", "Ce que ton âme vient apprendre", bool(cyc.get('lo_shu'))),
                ('bio', "Tes biorythmes", "Biorythmes", "Les 90 prochains jours", bool(cyc.get('biorhythms')) or bool(self._ai.get('biorythmes'))),
                ('rituels', "Rituels de vibration", "Rituels de vibration", "Cinq pratiques numérologiques", True),
                ('compat', "Compatibilités numériques", "Compatibilités numériques", "Ta résonance avec les autres", True),
                ('affirm', "Affirmations & Mantras", "Affirmations & Mantras", "Sept phrases pour t'ancrer", True),
                ('journal', "Journal des vibrations", "Journal des vibrations", "Trois prompts pour intégrer", True),
            ]
            chapters = [c for c in chapters if c[4]]
            romans = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII']
            roman = {c[0]: romans[i] for i, c in enumerate(chapters)}

            _toc_page(story, _mini_styles, [
                {'roman': roman[c[0]], 'title': c[1], 'page': _pg(f'chap_{c[0]}')} for c in chapters
            ])

            builders = {
                'intro': lambda: self._page_intro(),
                'nombres': lambda: self._pages_nombres_cles(numerology_data, first_name),
                'annee': lambda: self._pages_annee_personnelle(personal_year_data, cyc),
                'mois': lambda: self._pages_mois(cyc),
                'pinacles': lambda: self._pages_pinacles(cyc),
                'forecast': lambda: self._pages_forecast(forecast_data),
                'loshu': lambda: self._pages_loshu(cyc),
                'karma': lambda: self._pages_karma(cyc),
                'bio': lambda: self._pages_biorythmes(cyc),
                'rituels': lambda: self._page_rituels_finaux(first_name),
                'compat': lambda: self._page_compatibilites(numerology_data, first_name),
                'affirm': lambda: self._page_affirmations_numo(first_name),
                'journal': lambda: self._page_journal_numo(first_name),
            }
            for i, (cid, _toc, opener_title, opener_sub, _on) in enumerate(chapters):
                story.append(chapter_marker(f'chap_{cid}'))
                _chapter_opener(story, _mini_styles, roman[cid], opener_title, opener_sub)
                story.extend(builders[cid]())
                if cid != 'journal':
                    story.append(PageBreak())

            if self._ai.get('invitation_finale'):
                story.append(Paragraph('<font name="OrnamentSerif">✦</font> Ton Invitation <font name="OrnamentSerif">✦</font>', self.heading_style))
                story.append(Spacer(0, 0.3 * cm))
                story.append(Paragraph(self._ai['invitation_finale'], self.body_style))
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
    
    def _pages_annee_personnelle(self, data: Dict[str, Any], cyc: Optional[Dict[str, Any]] = None) -> List:
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
        if cyc and cyc.get('personal_year_text') and not ai_narrative:
            story.append(Paragraph(
                f"<b>{cyc['personal_year_theme']}</b> — {cyc['personal_year_text']}",
                self.body_style,
            ))
        
        return story

    def _table(self, rows: List[List[Any]], widths: List[float]) -> Table:
        t = Table(rows, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NIGHT_SOFT),
            ('TEXTCOLOR', (0, 0), (-1, 0), GOLD),
            ('LINEBELOW', (0, 0), (-1, -1), 0.4, GOLD_LIGHT),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        return t

    def _cell(self, text: str, bold: bool = False) -> Paragraph:
        style = ParagraphStyle(
            'Cell', fontName='Helvetica-Bold' if bold else 'Helvetica', fontSize=9.5,
            textColor=CREAM, leading=13,
        )
        return Paragraph(text, style)

    def _pages_mois(self, cyc: Dict[str, Any]) -> List:
        """Calendrier des 12 prochains mois personnels."""
        story: List = [
            Paragraph('Tes 12 prochains mois', self.heading_style),
            Paragraph(
                f"Ton année personnelle actuelle est le <b>{cyc['personal_year']}</b> "
                f"({cyc['personal_year_theme']}). Chaque mois porte sa propre couleur, "
                "obtenue en additionnant ton année personnelle et le numéro du mois.",
                self.body_style,
            ),
            Spacer(0, 0.3 * cm),
        ]
        rows = [[self._cell('<b>Mois</b>'), self._cell('<b>Nombre</b>'), self._cell('<b>Ce que ce mois t\'invite à faire</b>')]]
        for m in cyc['months']:
            rows.append([
                self._cell(m['label'], bold=True),
                self._cell(str(m['personal_month'])),
                self._cell(f"<b>{m['theme']}.</b> {m['text']}"),
            ])
        story.append(self._table(rows, [3.3 * cm, 1.8 * cm, 12.4 * cm]))
        return story

    def _pages_pinacles(self, cyc: Dict[str, Any]) -> List:
        """Quatre pinacles (grandes périodes) et quatre défis."""
        story: List = [
            Paragraph('Tes quatre grands cycles', self.heading_style),
            Paragraph(
                'Ta vie se déroule en quatre grandes saisons, calculées à partir de ta date de naissance. '
                'Chacune apporte une énergie dominante et des opportunités spécifiques.',
                self.body_style,
            ),
            Spacer(0, 0.3 * cm),
        ]
        rows = [[self._cell('<b>Cycle</b>'), self._cell('<b>Période</b>'), self._cell('<b>Nombre</b>'), self._cell('<b>Énergie</b>')]]
        for p in cyc['pinnacles']:
            rows.append([
                self._cell(f"Cycle {p['index']}", bold=True),
                self._cell(f"{p['age']} (dès {p['year_from']})"),
                self._cell(str(p['number'])),
                self._cell(p['text']),
            ])
        story.append(self._table(rows, [2.2 * cm, 4.6 * cm, 1.8 * cm, 8.9 * cm]))
        story.append(Spacer(0, 0.6 * cm))
        story.append(Paragraph('Tes quatre défis', self.heading_style))
        story.append(Paragraph(
            'Les défis ne sont pas des obstacles figés : ce sont les points d\'entraînement '
            'qui te font grandir pendant chaque cycle.',
            self.body_style,
        ))
        rows = [[self._cell('<b>Défi</b>'), self._cell('<b>Nombre</b>'), self._cell('<b>Leçon</b>')]]
        for c in cyc['challenges']:
            rows.append([self._cell(f"Défi {c['index']}", bold=True), self._cell(str(c['number'])), self._cell(c['text'])])
        story.append(self._table(rows, [2.2 * cm, 1.8 * cm, 13.5 * cm]))
        return story

    def _loshu_grid(self, lo: Dict[str, Any]) -> Table:
        cell_style = ParagraphStyle(
            'LoShuCell', fontName='Helvetica-Bold', fontSize=18, textColor=GOLD,
            alignment=TA_CENTER, leading=22,
        )
        rows = []
        for line in lo['grid']:
            rows.append([
                Paragraph((str(n) * lo['counts'][n]) if lo['counts'][n] else '<font color="#B5B0A8">·</font>', cell_style)
                for n in line
            ])
        t = Table(rows, colWidths=[2.6 * cm] * 3, rowHeights=[1.9 * cm] * 3)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.8, GOLD_LIGHT),
            ('BACKGROUND', (0, 0), (-1, -1), NIGHT_SOFT),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        t.hAlign = 'CENTER'
        return t

    def _pages_loshu(self, cyc: Dict[str, Any]) -> List:
        lo = cyc.get('lo_shu')
        story: List = [Paragraph('Ton Carré Lo-Shu', self.heading_style)]
        if lo:
            story.append(Paragraph(
                'Le Lo-Shu est une grille de 3 × 3 cases. Les chiffres de ta date de naissance '
                's\'y placent : les cases remplies sont tes forces, les cases vides tes zones d\'apprentissage.',
                self.body_style,
            ))
            story.append(Spacer(0, 0.3 * cm))
            story.append(self._loshu_grid(lo))
            story.append(Spacer(0, 0.5 * cm))
        if self._ai.get('lo_shu'):
            story.append(Paragraph(self._ai['lo_shu'], self.body_style))
        if lo:
            story.append(Paragraph('Tes forces', self.heading_style))
            for item in lo['present']:
                n = item['number']
                count = f" (×{item['count']}, énergie renforcée)" if item['count'] > 1 else ''
                story.append(Paragraph(f"<b>{n}</b>{count} — {item['text']}", self.body_style))
            if lo['arrows']:
                story.append(Paragraph('Tes flèches d\'individualité', self.heading_style))
                for a in lo['arrows']:
                    story.append(Paragraph(f"<b>{a['name']}</b> — {a['text']}", self.body_style))
        return story

    def _pages_karma(self, cyc: Dict[str, Any]) -> List:
        story: List = [Paragraph('Dettes karmiques & leçons', self.heading_style)]
        debts = cyc.get('karmic_debts') or []
        if debts:
            story.append(Paragraph(
                'Certains nombres de ta date de naissance portent une mémoire : ils signalent un thème '
                'que ton âme est venue travailler.',
                self.body_style,
            ))
            for d in debts:
                story.append(Paragraph(f"<b>{d['number']}</b> (via ton {d['source']}) — {d['text']}", self.body_style))
        else:
            story.append(Paragraph(
                'Aucune dette karmique classique (13, 14, 16, 19) n\'apparaît dans ta date de naissance : '
                'tu ne portes pas de thème de rattrapage marqué, et tes apprentissages se jouent surtout '
                'à travers tes défis et les cases vides de ton carré.',
                self.body_style,
            ))
        lo = cyc.get('lo_shu') or {}
        if lo.get('missing'):
            story.append(Paragraph('Tes leçons à intégrer (chiffres absents)', self.heading_style))
            for item in lo['missing']:
                story.append(Paragraph(f"<b>{item['number']}</b> — {item['text']}", self.body_style))
        if lo.get('empty_arrows'):
            story.append(Paragraph('Flèches à cultiver', self.heading_style))
            for a in lo['empty_arrows']:
                story.append(Paragraph(f"<b>{a['name']}</b> — {a['text']}", self.body_style))
        return story

    def _pages_biorythmes(self, cyc: Dict[str, Any]) -> List:
        story: List = [Paragraph('Tes biorythmes des 90 prochains jours', self.heading_style)]
        bio = cyc.get('biorhythms')
        if self._ai.get('biorythmes'):
            story.append(Paragraph(self._ai['biorythmes'], self.body_style))
        if bio:
            story.append(Paragraph(
                'Les biorythmes décrivent trois cycles réguliers depuis ta naissance : physique (23 jours), '
                'émotionnel (28 jours) et intellectuel (33 jours). Ils sont un repère de rythme, pas une prédiction.',
                self.body_style,
            ))
            rows = [[self._cell('<b>Cycle</b>'), self._cell('<b>Aujourd\'hui</b>'), self._cell('<b>Prochains sommets</b>'), self._cell('<b>Jours de bascule</b>')]]
            for k in ('physique', 'émotionnel', 'intellectuel'):
                rows.append([
                    self._cell(k.capitalize(), bold=True),
                    self._cell(f"{bio['today'][k]:+d} %"),
                    self._cell(', '.join(bio['peaks'][k][:3]) or '—'),
                    self._cell(', '.join(bio['critical'][k][:4]) or '—'),
                ])
            story.append(self._table(rows, [3 * cm, 2.6 * cm, 5.4 * cm, 6.5 * cm]))
            story.append(Spacer(0, 0.3 * cm))
            story.append(Paragraph(
                'Les jours de bascule (le cycle passe par zéro) sont propices au recentrage : '
                'allège ton agenda et évite les décisions lourdes si tu te sens fatigué(e).',
                self.body_style,
            ))
        return story

    
    def _pages_forecast(self, data: Dict[str, Any]) -> List:
        """Prévisions et cycles futurs."""
        story = []
        story.append(Paragraph('Prévisions des Cycles à Venir', self.heading_style))
        
        forecast = data.get('forecast', [])
        if isinstance(forecast, list) and len(forecast) > 0:
            for item in forecast[:5]:
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
    cycles: Optional[Dict[str, Any]] = None,
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
        cycles=cycles if cycles is not None else build_cycles(birth_date_iso),
    )


def _cycles_summary(cycles: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Résumé compact et stable (sans dates) pour guider l'IA."""
    if not cycles:
        return {}
    return {
        'chemin_de_vie': cycles['life_path'],
        'annee_personnelle': cycles['personal_year'],
        'pinacles': [p['number'] for p in cycles['pinnacles']],
        'defis': [c['number'] for c in cycles['challenges']],
        'dettes_karmiques': [d['number'] for d in cycles['karmic_debts']],
        'lo_shu_chiffres_absents': [m['number'] for m in cycles['lo_shu']['missing']],
        'lo_shu_chiffres_repetes': cycles['lo_shu']['repeated'],
    }


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
            'resume_cycles': _cycles_summary(build_cycles(birth_date_iso)),
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
        cycles=build_cycles(birth_date_iso),
    )
