"""Book composition with real text flow and distinct reading/Lulu interiors.

All editions use the same manuscript. No network or AI calls during rendering.
Cover dimensions must come from the selected Lulu product's actual template.
"""
from __future__ import annotations
import base64
import html
import io
import math
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, Image, PageBreak, PageTemplate,
    Paragraph, Spacer, CondPageBreak, HRFlowable,
)
from reportlab.platypus.tableofcontents import TableOfContents

# Textes structurels : i18n minimale FR/EN pour la couverture, préface, sommaire…
_I18N = {
    'fr': {
        'book_title_default': 'Thème Natal',
        'book_subtitle_default': 'Complet',
        'cover_eyebrow': '✦  TON PORTRAIT CÉLESTE  ✦',
        'cover_subtitle': 'Une lecture personnelle de ton ciel de naissance',
        'cover_edition': 'ÉDITION PERSONNELLE',
        'intro_para': ('Ce livre est composé à partir de ton ciel de naissance. '
                       'Il propose une lecture symbolique et personnelle, à confronter à ton expérience. '
                       'Il ne prédit pas un avenir certain et ne remplace pas ta liberté de choix.'),
        'preface_title': 'Préface',
        'preface_paras_tpl': [
            '{name}, ce livre t’invite à faire une pause et à regarder ton histoire sous un autre angle. Ton thème de naissance en est le point de départ : une carte singulière, composée pour un lieu et un instant précis.',
            'Les pages qui suivent mettent en mots des contrastes, des élans et des besoins. Tu pourras te reconnaître dans certaines lectures, en discuter d’autres et laisser de côté ce qui ne te parle pas. Tu restes la personne la mieux placée pour donner du sens à ton vécu.',
            'Prends le temps de lire, de noter tes réactions et de revenir sur un passage lorsque ta situation évolue. L’intention de ce livre est de soutenir cette attention à toi-même, avec nuance, curiosité et bienveillance.',
        ],
        'toc_title': 'Sommaire',
        'intro_chapter_title': 'Introduction — Comment lire ton thème',
        'closing_title': 'Pour poursuivre ta lecture',
        'closing_paras': [
            "Choisis une idée qui t’a touché et relie-la à une situation concrète de ta vie. Qu’est-ce qu’elle t’aide à nommer ? Quelle autre explication pourrais-tu envisager ?",
            "Note une action simple à essayer cette semaine. Reviens ensuite à ton livre pour observer ce qui s’est éclairci, ce qui a changé et ce qui demande encore du temps.",
            "Plume Astrale — Édition personnelle. Les interprétations relèvent d’une démarche symbolique de connaissance de soi.",
        ],
        'cutout_hint': '✁  à découper · à offrir · à conserver',
        'cutout_sig': '— Plume Astrale, écrit pour toi',
    },
    'en': {
        'book_title_default': 'Natal Chart',
        'book_subtitle_default': 'Complete',
        'cover_eyebrow': '✦  YOUR CELESTIAL PORTRAIT  ✦',
        'cover_subtitle': 'A personal reading of your birth sky',
        'cover_edition': 'PERSONAL EDITION',
        'intro_para': ('This book is composed from your birth chart. It offers a symbolic '
                       'and personal reading, to be checked against your experience. It does not '
                       'predict a certain future and does not replace your freedom to choose.'),
        'preface_title': 'Preface',
        'preface_paras_tpl': [
            '{name}, this book invites you to pause and look at your story from another angle. Your birth chart is its starting point: a singular map, composed for one precise place and moment.',
            'The pages that follow put into words contrasts, impulses and needs. You will recognize yourself in some readings, debate others, and set aside what does not speak to you. You remain the person best placed to make sense of your lived experience.',
            'Take time to read, to note your reactions, and to return to a passage when your situation evolves. The intention of this book is to support that attention to yourself — with nuance, curiosity and care.',
        ],
        'toc_title': 'Contents',
        'intro_chapter_title': 'Introduction — How to read your chart',
        'closing_title': 'To continue your reading',
        'closing_paras': [
            "Choose an idea that moved you and tie it to a concrete situation in your life. What does it help you name? What other explanation might you consider?",
            "Note one simple action to try this week. Then return to your book to observe what has cleared, what has changed, and what still needs time.",
            "Plume Astrale — Personal Edition. These interpretations are a symbolic practice of self-knowledge.",
        ],
        'cutout_hint': '✁  cut · gift · keep',
        'cutout_sig': '— Plume Astrale, written for you',
    },
}


def _t(language, key):
    return _I18N.get(language, _I18N['fr']).get(key, _I18N['fr'][key])


ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 148 * mm, 210 * mm
NAVY = colors.HexColor('#142342')
INK = colors.HexColor('#243047')
GOLD = colors.HexColor('#A78140')
GOLD_BRIGHT = colors.HexColor('#D4AF37')   # or doré brillant pour la couverture
MUTED = colors.HexColor('#526077')
CREAM = colors.HexColor('#F5EEE0')  # fond papier parchemin (matching site hero)
DESIGN_VERSION = 'plume-book-flow-2026-10'

# Mapping planète / maison → asset illustration (bibliothèque)
_PLANET_ASSET = {
    'Soleil': 'planets/sun_512.png',    'Sun': 'planets/sun_512.png',
    'Lune': 'planets/moon_512.png',     'Moon': 'planets/moon_512.png',
    'Mercure': 'planets/mercury_512.png','Mercury': 'planets/mercury_512.png',
    'Vénus': 'planets/venus_512.png',   'Venus': 'planets/venus_512.png',
    'Mars': 'planets/mars_512.png',
    'Jupiter': 'planets/jupiter_512.png',
    'Saturne': 'planets/saturn_512.png','Saturn': 'planets/saturn_512.png',
    'Uranus': 'planets/uranus_512.png',
    'Neptune': 'planets/neptune_512.png',
    'Pluton': 'planets/pluto_512.png',  'Pluto': 'planets/pluto_512.png',
}
_LIB_ROOT = ROOT / 'assets' / 'library'


def _fonts():
    directory = ROOT / 'assets' / 'book' / 'fonts'
    for suffix, filename in [('', 'Regular'), ('-Bold', 'Bold'), ('-Italic', 'Italic')]:
        name = 'PlumeBook' + suffix
        if name not in pdfmetrics.getRegisteredFontNames():
            path = directory / f'CormorantGaramond-{filename}.ttf'
            if not path.exists():
                raise RuntimeError(f'Police de livre absente : {path.name}')
            pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily('PlumeBook', normal='PlumeBook',
                                 bold='PlumeBook-Bold', italic='PlumeBook-Italic',
                                 boldItalic='PlumeBook-Bold')
    # Ornament font pour ✦ ❖ ⚜ ◆ — Cormorant Garamond n'a pas ces glyphes
    # (ils sont rendus en .notdef = tofu). FreeSerif les couvre.
    if 'PlumeOrnament' not in pdfmetrics.getRegisteredFontNames():
        for candidate in (
            Path('/usr/share/fonts/truetype/freefont/FreeSerif.ttf'),
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'),
        ):
            if candidate.exists():
                pdfmetrics.registerFont(TTFont('PlumeOrnament', str(candidate)))
                break


def _plain(value):
    # Strip HTML tags, then supprime les caractères unicode qui n'existent pas dans
    # Cormorant Garamond (sinon rendu en .notdef = tofu). Liste : symboles
    # astrologiques (℞ ♃ ♀ ♂ ☉ ☽), ornements (✦ ❖ ⚜ ◆) — ces derniers doivent être
    # posés via la police PlumeOrnament ailleurs, pas dans le texte courant.
    text = re.sub(r'<[^>]+>', '', html.unescape(str(value or ''))).strip()
    # Supprime les glyphes astrologiques et ornements orphelins susceptibles
    # de rendre en tofu dans un Paragraph Cormorant.
    FORBIDDEN_IN_BODY = '℞♃♀♂☉☽☿♁♄♅♆♇✦❖⚜◆'
    for ch in FORBIDDEN_IN_BODY:
        text = text.replace(ch, '')
    # Supprime aussi le NUL (U+0000) et les caractères de contrôle non imprimables
    text = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', text)
    return text.strip()


def _paragraphs(value):
    # Only server-generated prose, no arbitrary HTML, image paths or links.
    text = str(value or '').replace('\r\n', '\n')
    text = re.sub(r'</p\s*>|<br\s*/?>', '\n\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    # Supprime les glyphes qui provoquent un tofu en Cormorant Garamond.
    for ch in '℞♃♀♂☉☽☿♁♄♅♆♇✦❖⚜◆':
        text = text.replace(ch, '')
    text = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', text)
    return [html.escape(html.unescape(p.strip())) for p in re.split(r'\n\s*\n', text) if p.strip()]


def _styles():
    common = dict(fontName='PlumeBook', textColor=INK)
    return {
        'body': ParagraphStyle('BookBody', fontSize=12, leading=16.5,
            alignment=TA_JUSTIFY, spaceAfter=9, allowWidows=0, allowOrphans=0, **common),
        'heading': ParagraphStyle('BookHeading', fontSize=25, leading=29,
            spaceAfter=18, alignment=TA_CENTER, keepWithNext=True, **common),
        'h2': ParagraphStyle('BookH2', fontName='PlumeBook-Bold', textColor=INK,
            fontSize=16, leading=20, spaceBefore=12, spaceAfter=10, keepWithNext=True),
        'kicker': ParagraphStyle('BookKicker', fontName='PlumeBook-Italic', textColor=MUTED,
            fontSize=12, leading=16, spaceAfter=16, alignment=TA_CENTER, keepWithNext=True),
        'small': ParagraphStyle('BookSmall', fontSize=10, leading=14, spaceAfter=8, **common),
        'toc': ParagraphStyle('BookTOC', fontSize=11, leading=14, spaceBefore=5,
            leftIndent=0, firstLineIndent=0, rightIndent=12, **common),
    }


class _Cover(Flowable):
    width = WIDTH - 40 * mm
    height = HEIGHT - 44 * mm

    def __init__(self, manuscript, image_path=None, lang='fr'):
        super().__init__()
        self.m = manuscript
        self.image_path = image_path
        self.lang = lang

    def _draw_stars(self, c):
        """Champ d'étoiles doré, deterministe, inspiré de la hero du site Thème Natal."""
        import random
        rng = random.Random(42)  # seed stable → même étoile à chaque export
        c.setFillColor(GOLD_BRIGHT)
        # Petites étoiles pâles un peu partout
        for _ in range(140):
            x = rng.uniform(6*mm, WIDTH-6*mm)
            y = rng.uniform(6*mm, HEIGHT-6*mm)
            r = rng.choice([.18, .22, .28, .35, .5]) * mm
            c.setFillAlpha(rng.uniform(.25, .85))
            c.circle(x, y, r, stroke=0, fill=1)
        # Quelques « étoiles filantes » discrètes (petits traits)
        c.setStrokeColor(GOLD_BRIGHT)
        c.setLineWidth(.25)
        for _ in range(5):
            x = rng.uniform(15*mm, WIDTH-15*mm)
            y = rng.uniform(15*mm, HEIGHT-15*mm)
            dx = rng.choice([-1,1]) * rng.uniform(2.5*mm, 4*mm)
            dy = rng.choice([-1,1]) * rng.uniform(1*mm, 2*mm)
            c.setStrokeAlpha(rng.uniform(.15, .35))
            c.line(x, y, x+dx, y+dy)
        c.setStrokeAlpha(1)
        c.setFillAlpha(1)

    def draw(self):
        c = self.canv
        c.saveState()
        c.resetTransforms()
        # ── 1) Fond navy profond (identique à la hero section de /theme-natal-luxe)
        c.setFillColor(NAVY)
        c.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
        # ── 2) Champ d'étoiles dorées
        self._draw_stars(c)
        # ── 3) Illustration (optionnelle) : discrete overlay, pas plein cadre
        if self.image_path:
            path = Path(self.image_path)
            if not path.is_file():
                raise ValueError('Illustration de couverture introuvable')
            # Vignette circulaire discrète, non pleine page, pour ne pas étouffer le titre
            c.saveState()
            c.setFillAlpha(.22)
            c.drawImage(str(path), WIDTH/2-30*mm, 112*mm, 60*mm, 60*mm,
                        mask='auto', preserveAspectRatio=True)
            c.setFillAlpha(1)
            c.restoreState()
        # ── 4) Double cadre or (fin extérieur, filet intérieur plus épais)
        c.setStrokeColor(GOLD_BRIGHT)
        c.setLineWidth(.6)
        c.rect(8*mm, 8*mm, WIDTH-16*mm, HEIGHT-16*mm)
        c.setLineWidth(1.4)
        c.rect(11*mm, 11*mm, WIDTH-22*mm, HEIGHT-22*mm)
        # ── 5) Ornements d'angle (petits soleils dans les 4 coins)
        for cx_o, cy_o in [(14*mm,14*mm),(WIDTH-14*mm,14*mm),
                            (14*mm,HEIGHT-14*mm),(WIDTH-14*mm,HEIGHT-14*mm)]:
            c.circle(cx_o, cy_o, 1.2*mm, stroke=1, fill=0)
            for ang in range(0,360,45):
                a = ang*math.pi/180
                c.line(cx_o+1.8*mm*math.cos(a), cy_o+1.8*mm*math.sin(a),
                       cx_o+2.6*mm*math.cos(a), cy_o+2.6*mm*math.sin(a))
        # ── 6) TOP : « P L U M E   A S T R A L E » en or léger (logo texte)
        c.setFillColor(GOLD_BRIGHT)
        c.setFont('PlumeBook', 10)
        c.drawCentredString(WIDTH/2, 188*mm, 'P L U M E   A S T R A L E')
        # Filet or sous le logo
        c.setLineWidth(.4)
        c.line(WIDTH/2-16*mm, 184*mm, WIDTH/2+16*mm, 184*mm)
        # ── 7) EYEBROW : « ✦  TON PORTRAIT CÉLESTE  ✦ » (petit, or, lettres espacées)
        # Les ✦ sont rendus avec PlumeOrnament (FreeSerif) car Cormorant Garamond
        # n'a pas ce glyphe → sinon tofu.
        c.setFillColor(GOLD_BRIGHT)
        eyebrow = _t(self.lang, 'cover_eyebrow')
        # Séparer les ✦ du texte principal pour alterner les polices.
        eyebrow_center_y = 172 * mm
        if 'PlumeOrnament' in pdfmetrics.getRegisteredFontNames() and '✦' in eyebrow:
            inner = eyebrow.replace('✦', '').strip()  # « TON PORTRAIT CÉLESTE »
            # Mesure manuelle des composants pour centrage
            c.setFont('PlumeOrnament', 8.5)
            star_w = c.stringWidth('✦', 'PlumeOrnament', 8.5)
            c.setFont('PlumeBook', 8.5)
            inner_w = c.stringWidth(inner, 'PlumeBook', 8.5)
            gap = 3 * mm
            total_w = star_w + gap + inner_w + gap + star_w
            x = (WIDTH - total_w) / 2
            # ✦ gauche
            c.setFont('PlumeOrnament', 8.5)
            c.drawString(x, eyebrow_center_y, '✦')
            # Texte
            c.setFont('PlumeBook', 8.5)
            c.drawString(x + star_w + gap, eyebrow_center_y, inner)
            # ✦ droite
            c.setFont('PlumeOrnament', 8.5)
            c.drawString(x + star_w + gap + inner_w + gap, eyebrow_center_y, '✦')
        else:
            c.setFont('PlumeBook', 8.5)
            c.drawCentredString(WIDTH / 2, eyebrow_center_y, eyebrow)
        # ── 8) TITRE : « Thème Natal » en italique dorée brillante (hero style)
        title = (self.m.astro_data or {}).get('book_title') or _t(self.lang, 'book_title_default')
        style_title = ParagraphStyle('CoverTitle', fontName='PlumeBook-Italic',
            fontSize=42, leading=46, alignment=TA_CENTER, textColor=GOLD_BRIGHT)
        title_p = Paragraph(html.escape(title), style_title)
        _, th = title_p.wrap(WIDTH-28*mm, 56*mm)
        title_p.drawOn(c, 14*mm, 158*mm-th)
        # ── 9) Filet or sous le titre
        # (le mot « Complet » historiquement posé ici a été retiré Feb 2026 :
        # il créait une superposition visuelle disgracieuse sous le titre.)
        c.setStrokeColor(GOLD_BRIGHT)
        c.setLineWidth(.4)
        c.line(WIDTH/2-20*mm, 132*mm, WIDTH/2+20*mm, 132*mm)
        # ── 11) PRÉNOM : « Pour Nadine » en italique or clair
        name_style = ParagraphStyle('CoverName', fontName='PlumeBook-Italic',
            fontSize=20, leading=24, alignment=TA_CENTER, textColor=GOLD_BRIGHT)
        for font_size in (20, 18, 16, 14, 12):
            name_style.fontSize = font_size
            name_style.leading = font_size + 4
            name_p = Paragraph(html.escape(f'Pour {self.m.first_name}'), name_style)
            _, h = name_p.wrap(WIDTH-28*mm, 30*mm)
            if h <= 28:
                break
        if h > 28:
            raise ValueError('Nom trop long pour la couverture : utiliser le prénom de lecture')
        name_p.drawOn(c, 14*mm, 118*mm-h)
        # ── 12) BOTTOM : subtitle + edition en or
        c.setFillColor(GOLD_BRIGHT)
        c.setFont('PlumeBook-Italic', 11.5)
        c.drawCentredString(WIDTH/2, 42*mm, _t(self.lang, 'cover_subtitle'))
        c.setFont('PlumeBook', 9)
        c.drawCentredString(WIDTH/2, 24*mm, _t(self.lang, 'cover_edition'))
        c.restoreState()


class _CutoutMark(Flowable):
    """Marker invisible : signale au _BookDoc que la page courante doit être
    rendue en « page à découper » (bordure pointillée, pas de folio ni d'entête).
    """
    _cutout_marker = True
    width = 0
    height = 0

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        pass


class _BookDoc(BaseDocTemplate):
    def __init__(self, stream, name, cover_pages=2):
        super().__init__(stream, pagesize=(WIDTH, HEIGHT), leftMargin=21*mm,
            rightMargin=17*mm, topMargin=20*mm, bottomMargin=23*mm,
            title=f'Le Livre Astral de {name}', author='Plume Astrale')
        self.person_name = name
        self.cover_pages = cover_pages
        self._cutout_pages: set[int] = set()
        self.addPageTemplates(PageTemplate('book',
            frames=[Frame(21*mm,23*mm,110*mm,167*mm,id='text',
                          leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],
            onPage=self._page))

    def _page(self, canvas, doc):
        # Mirrored gutter, identical usable width on recto and verso.
        self.pageTemplate.frames[0]._x1 = (21 if doc.page % 2 else 17)*mm
        self.pageTemplate.frames[0]._geom()
        # Fond crème parchemin sur toutes les pages intérieures (hors couverture)
        if doc.page > self.cover_pages:
            canvas.saveState()
            canvas.setFillColor(CREAM)
            canvas.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
            canvas.restoreState()
        if doc.page <= self.cover_pages:
            return
        # Ex Libris : page « à découper » (pas de folio, bordure pointillée)
        if doc.page in self._cutout_pages:
            canvas.saveState()
            canvas.setStrokeColor(GOLD)
            canvas.setLineWidth(.45)
            canvas.setDash([2.4, 2.4])
            margin = 11*mm
            canvas.rect(margin, margin, WIDTH-2*margin, HEIGHT-2*margin)
            canvas.setDash()  # reset
            # Pictogramme ciseaux + libellé discret, en haut à gauche hors cadre
            canvas.setFillColor(MUTED)
            canvas.setFont('PlumeBook-Italic', 7.5)
            canvas.drawString(margin + 1.5*mm, margin - 3.2*mm,
                              '✁  à découper · à offrir · à conserver')
            canvas.restoreState()
            return
        canvas.saveState()
        canvas.setFillColor(MUTED)
        canvas.setFont('PlumeBook', 9)
        canvas.drawString(17*mm, 12*mm, 'PLUME ASTRALE')
        canvas.drawRightString(WIDTH-17*mm,12*mm,str(doc.page-self.cover_pages))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if getattr(flowable, '_cutout_marker', False):
            self._cutout_pages.add(self.page)
            return
        if getattr(flowable, '_toc_key', None):
            key = flowable._toc_key
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flowable.getPlainText(),key,level=0,closed=False)
            self.notify('TOCEntry',(0,flowable.getPlainText(),self.page-self.cover_pages,key))


def _heading(text, styles, key=None):
    p = Paragraph(html.escape(text), styles['heading'])
    if key:
        p._toc_key = key
    return p


def validate_manuscript(manuscript):
    if not manuscript.chapters:
        raise ValueError('Manuscrit sans chapitres')
    for chapter in manuscript.chapters:
        text = ' '.join(_plain(b.data.get('text')) for b in chapter.blocks)
        if 'Ce chapitre s’écrit encore' in text or "Ce chapitre s'écrit encore" in text:
            raise ValueError(f'Chapitre incomplet : {chapter.slug}')
        meaningful = [b for b in chapter.blocks if str(getattr(b.kind,'value',b.kind))
                      not in ('chapter_opening','feather','hairline','page_break')]
        if not meaningful:
            raise ValueError(f'Chapitre vide : {chapter.slug}')


def _chapter_illust_for_slug(slug: str):
    """Renvoie le path d'illustration (string) pour un chapitre, selon son slug."""
    slug = (slug or '').lower()
    if 'planet' in slug:
        path = _LIB_ROOT / 'planets' / 'sun_512.png'
    elif 'house' in slug or 'maison' in slug:
        path = _LIB_ROOT / 'houses' / 'house1_512.png'
    elif 'synthese' in slug or 'ciel' in slug:
        path = _LIB_ROOT / 'tarot' / '17_l_etoile_512.png'
    elif 'aspect' in slug:
        path = _LIB_ROOT / 'tarot' / '08_la_force_512.png'
    elif 'preface' in slug or 'introduction' in slug:
        path = _LIB_ROOT / 'tarot' / '01_le_bateleur_512.png'
    elif 'closing' in slug:
        path = _LIB_ROOT / 'tarot' / '19_le_soleil_512.png'
    else:
        path = None
    return str(path) if path and path.is_file() else None


def _chapter_tail_illust_for_slug(slug: str):
    """Illustration d'ornement de fin de chapitre : vignette thématique différente
    de l'ouverture, pour combler l'espace blanc en fin de section comme dans
    un vrai livre de collection."""
    slug = (slug or '').lower()
    if 'planet' in slug:
        path = _LIB_ROOT / 'tarot' / '18_la_lune_512.png'
    elif 'house' in slug or 'maison' in slug:
        path = _LIB_ROOT / 'tarot' / '03_l_imperatrice_512.png'
    elif 'synthese' in slug or 'ciel' in slug:
        path = _LIB_ROOT / 'tarot' / '07_le_chariot_512.png'
    elif 'aspect' in slug:
        path = _LIB_ROOT / 'tarot' / '06_les_amoureux_512.png'
    elif 'preface' in slug or 'introduction' in slug:
        path = _LIB_ROOT / 'tarot' / '17_l_etoile_512.png'
    elif 'closing' in slug or 'ex_libris' in slug:
        path = _LIB_ROOT / 'tarot' / '12_le_pendu_512.png'
    else:
        path = _LIB_ROOT / 'tarot' / '17_l_etoile_512.png'
    return str(path) if path and path.is_file() else None


def _planet_image_for_h2(text):
    """Si le H2 commence par un nom de planète, renvoie le path image, sinon None."""
    plain = _plain(text).strip()
    first_word = plain.split()[0] if plain else ''
    # Essayer avec et sans accents (Vénus, Pluton, etc.)
    for key, asset in _PLANET_ASSET.items():
        if first_word.lower().startswith(key.lower()):
            path = _LIB_ROOT / asset
            if path.is_file():
                return str(path)
    return None


def _append_blocks(story, chapter, styles):
    for block in chapter.blocks:
        kind = getattr(block.kind,'value',block.kind)
        data = block.data or {}
        if kind == 'chapter_opening':
            # Illustration de chapitre déjà injectée dans le flux principal (avant _heading).
            # Ce bloc reste un marqueur pour la hiérarchie — pas de rendu additionnel.
            continue
        if kind == 'feather':
            # Ornement de clôture discret au cœur du chapitre : un filet or
            # fin + une petite étoile centrale, pour aérer sans laisser de blanc.
            story.append(Spacer(1, 6*mm))
            story.append(HRFlowable(width='28%', thickness=.5, color=GOLD,
                                     hAlign='CENTER', spaceAfter=4))
            star_style = ParagraphStyle('Feather', fontName='PlumeOrnament' if 'PlumeOrnament' in pdfmetrics.getRegisteredFontNames() else 'PlumeBook',
                fontSize=11, leading=14, alignment=TA_CENTER, textColor=GOLD)
            story.append(Paragraph('✦', star_style))
            story.append(HRFlowable(width='28%', thickness=.5, color=GOLD,
                                     hAlign='CENTER', spaceBefore=4, spaceAfter=4))
            continue
        if kind == 'page_break':
            if story and not isinstance(story[-1],PageBreak):
                story.append(PageBreak())
        elif kind == 'h2':
            # Si H2 planète, ajoute l'icône planète à gauche
            img_path = _planet_image_for_h2(data.get('text'))
            if img_path:
                story.append(CondPageBreak(45*mm))
                try:
                    img = Image(img_path, width=18*mm, height=18*mm, mask='auto')
                    img.hAlign = 'CENTER'
                    story.append(Spacer(1, 2*mm))
                    story.append(img)
                    story.append(Spacer(1, 2*mm))
                except Exception:
                    pass
                story.append(Paragraph(html.escape(_plain(data.get('text'))), styles['h2']))
            else:
                story.extend([CondPageBreak(35*mm),Paragraph(html.escape(_plain(data.get('text'))),styles['h2'])])
        elif kind == 'trio_cards':
            text = ' · '.join(f"{i.get('label','')} : {i.get('sign','')}" for i in data.get('items',[]))
            story.append(Paragraph(html.escape(text),styles['kicker']))
        elif kind == 'natal_chart':
            src = data.get('src') or ''
            if src.startswith('data:image/png;base64,'):
                image = Image(io.BytesIO(base64.b64decode(src.split(',',1)[1])))
                if data.get('full_page'):
                    # Carte du ciel en **affiche pleine page A5** : la roue
                    # occupe seule la page, centrée, avec juste la légende
                    # discrète en pied. Cadre de texte A5 utile = 110×167 mm,
                    # on vise 108×145 mm pour garder une respiration or.
                    story.append(PageBreak())
                    image._restrictSize(108*mm, 148*mm)
                    image.hAlign = 'CENTER'
                    story.append(Spacer(1, 4*mm))
                    story.append(image)
                    story.append(Spacer(1, 6*mm))
                    legend_style = ParagraphStyle('ChartLegend', fontName='PlumeBook-Italic',
                        fontSize=10, leading=14, alignment=TA_CENTER, textColor=MUTED)
                    story.append(Paragraph(html.escape(_plain(data.get('alt') or '')), legend_style))
                    story.append(PageBreak())
                else:
                    image._restrictSize(104*mm, 104*mm)
                    story.append(image)
        elif kind == 'image':
            # Illustration IA (Nano Banana) ou fichier résolu. Payload accepté :
            #   - data.src = 'data:image/png;base64,...' (préféré, portable)
            #   - data.path = chemin disque local
            # Dimensions : full_page=True → page poster A5 (108×148 mm),
            # sinon vignette dimensionnée par max_width_mm / max_height_mm
            # (défauts 70×70 mm — fin de section planétaire).
            src = data.get('src') or ''
            path = data.get('path')
            image_obj = None
            try:
                if src.startswith('data:image/') and ';base64,' in src:
                    image_obj = Image(io.BytesIO(base64.b64decode(src.split(',', 1)[1])))
                elif path:
                    image_obj = Image(path)
            except Exception:
                image_obj = None
            if image_obj is None:
                raise ValueError('Illustration sans fichier résolu dans le manuscrit')
            if data.get('full_page'):
                story.append(PageBreak())
                image_obj._restrictSize(108*mm, 148*mm)
                image_obj.hAlign = 'CENTER'
                story.append(Spacer(1, 6*mm))
                story.append(image_obj)
                caption = _plain(data.get('caption') or '')
                if caption:
                    cap_style = ParagraphStyle('IllustCap', fontName='PlumeBook-Italic',
                        fontSize=10, leading=14, alignment=TA_CENTER, textColor=MUTED)
                    story.append(Spacer(1, 4*mm))
                    story.append(Paragraph(html.escape(caption), cap_style))
                story.append(PageBreak())
            else:
                w_mm = float(data.get('max_width_mm') or 70)
                h_mm = float(data.get('max_height_mm') or 70)
                image_obj._restrictSize(w_mm*mm, h_mm*mm)
                image_obj.hAlign = 'CENTER'
                story.append(Spacer(1, 4*mm))
                story.append(image_obj)
                story.append(Spacer(1, 4*mm))
        elif kind == 'hairline':
            story.append(HRFlowable(width='45%',thickness=.5,color=GOLD,
                                     hAlign='CENTER',spaceBefore=6,spaceAfter=12))
        elif kind == 'natal_meta':
            text = ' · '.join(str(data.get(k) or '') for k in ('sign','house','degree','note') if data.get(k))
            story.append(Paragraph(html.escape(text),styles['small']))
        else:
            if data.get('label'):
                story.append(Paragraph(html.escape(str(data['label'])),styles['h2']))
            for text in _paragraphs(data.get('text')):
                story.append(Paragraph(text,styles['body']))
            if data.get('source'):
                story.append(Paragraph(html.escape(str(data['source'])),styles['small']))


def _embed_only_fonts(writer):
    """Remove ReportLab's unused base-font resource on pages with embedded text."""
    for page in writer.pages:
        resource = page.get('/Resources')
        fonts = resource.get_object().get('/Font') if resource else None
        if not fonts:
            continue
        fonts = fonts.get_object()
        embedded = next((ref for ref in fonts.values()
                         if str(ref.get_object().get('/Subtype')) == '/TrueType'), None)
        if embedded:
            for key, ref in list(fonts.items()):
                if ref.get_object().get('/BaseFont') == '/Helvetica':
                    fonts[key] = embedded


def render_book_pdf(manuscript, *, cover_png_path=None, language=None):
    """Full reading edition; print export removes only explicitly marked cover leaves."""
    validate_manuscript(manuscript)
    _fonts()
    styles = _styles()
    # Détection de la langue : priorité au paramètre, sinon astro_data.language, défaut fr
    lang = language or (manuscript.astro_data or {}).get('language') or 'fr'
    if lang not in _I18N:
        lang = 'fr'
    stream = io.BytesIO()
    # Édition imprimée : page blanche traditionnelle après la couverture.
    # Édition numérique : enchaîner directement sur la préface (évite deux pages de titre vides).
    edition_raw = getattr(manuscript, 'edition', None)
    is_digital = str(getattr(edition_raw, 'value', edition_raw) or '').lower() in ('numerique', 'digital')
    cover_pages = 1 if is_digital else 2
    doc = _BookDoc(stream, manuscript.first_name, cover_pages=cover_pages)
    if is_digital:
        story = [_Cover(manuscript, cover_png_path, lang=lang), PageBreak()]
    else:
        story = [_Cover(manuscript, cover_png_path, lang=lang), PageBreak(), Spacer(1, 5*mm), PageBreak(),
                 Spacer(1,22*mm),_heading(_t(lang,'book_title_default'),styles),
                 _heading(manuscript.first_name,styles),Spacer(1,20*mm)]
        for text in _paragraphs(_t(lang,'intro_para')):
            story.append(Paragraph(text,styles['body']))
        story.append(PageBreak())
    story += [_heading(_t(lang,'preface_title'),styles)]
    preface = [tpl.format(name=manuscript.first_name) for tpl in _t(lang,'preface_paras_tpl')]
    for text in preface:
        story.append(Paragraph(html.escape(text),styles['body']))
    story += [PageBreak(),_heading(_t(lang,'toc_title'),styles)]
    toc = TableOfContents()
    toc.levelStyles = [styles['toc']]
    toc.dotsMinLevel = 0
    story.append(toc)
    intro = [ch for ch in manuscript.chapters if ch.slug in ('natal_preface','natal_introduction')]
    other = [ch for ch in manuscript.chapters if ch not in intro]
    chapters = intro + other
    for index,chapter in enumerate(chapters):
        story.append(PageBreak())
        is_ex_libris = chapter.slug == 'ex_libris'
        if is_ex_libris:
            # Page découpable : marque la page courante + marges verticales généreuses.
            story.append(_CutoutMark())
            story.append(Spacer(1, 18*mm))
        title = _t(lang,'intro_chapter_title') if chapter in intro else chapter.title
        # Illustration d'ouverture de chapitre (fond crème + icône centrale 50mm)
        illust = _chapter_illust_for_slug(chapter.slug) if not is_ex_libris else None
        if illust:
            try:
                opener_img = Image(illust, width=50*mm, height=50*mm, mask='auto')
                opener_img.hAlign = 'CENTER'
                story.append(Spacer(1, 15*mm))
                story.append(opener_img)
                story.append(Spacer(1, 8*mm))
            except Exception:
                story.append(Spacer(1, 25*mm))
        story.append(_heading(title,styles,f'chapter-{index}'))
        if chapter.kicker:
            story.append(Paragraph(html.escape(chapter.kicker),styles['kicker']))
        if is_ex_libris:
            # Petit filet or sous le titre + espace pour aérer le paragraphe signature
            story.append(HRFlowable(width='35%',thickness=.4,color=GOLD,
                                     spaceBefore=0,spaceAfter=14))
        _append_blocks(story,chapter,styles)
        if is_ex_libris:
            story.append(Spacer(1, 12*mm))
            story.append(Paragraph(
                f'<i>{_t(lang,"cutout_sig")}</i>',
                ParagraphStyle('CutoutSig', parent=styles['small'],
                               alignment=TA_CENTER, textColor=GOLD),
            ))
        while isinstance(story[-1],PageBreak):
            story.pop()
    story += [PageBreak(),_heading(_t(lang,'closing_title'),styles)]
    for text in _t(lang,'closing_paras'):
        story.append(Paragraph(html.escape(text),styles['body']))
    from functools import partial
    from reportlab.pdfgen.canvas import Canvas
    doc.multiBuild(story,maxPasses=8,canvasmaker=partial(Canvas,initialFontName='PlumeBook'))
    reader = PdfReader(io.BytesIO(stream.getvalue()))
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    _embed_only_fonts(writer)
    # Édition imprimée : parité stricte des pages intérieures (reliure brochée).
    # Édition numérique : jamais de page blanche de fin.
    if not is_digital and (len(reader.pages)-cover_pages)%2:
        writer.add_blank_page(width=WIDTH,height=HEIGHT)
    writer.add_metadata({'/Title':f'Le Livre Astral de {manuscript.first_name}',
        '/Author':'Plume Astrale','/PlumeDesignVersion':DESIGN_VERSION,
        '/PlumeInteriorStart':str(cover_pages)})
    out=io.BytesIO(); writer.write(out)
    return out.getvalue()


def lulu_interior(pdf_bytes):
    """A5 interior plus 0.125 inch bleed on every side, without crop marks.

    Reject unknown/legacy PDFs instead of relabelling an arbitrary PDF print-ready.
    """
    reader=PdfReader(io.BytesIO(pdf_bytes))
    if (reader.metadata or {}).get('/PlumeDesignVersion') != DESIGN_VERSION:
        raise ValueError('Ancien PDF : régénérez le livre avant export Lulu')
    start=int(reader.metadata['/PlumeInteriorStart'])
    writer=PdfWriter()
    from pypdf import PageObject, Transformation
    from pypdf.generic import RectangleObject
    bleed = 3.175 * mm
    for page in list(reader.pages)[start:]:
        if abs(float(page.mediabox.width)-WIDTH)>.1 or abs(float(page.mediabox.height)-HEIGHT)>.1:
            raise ValueError('Format intérieur non A5')
        sheet = PageObject.create_blank_page(width=WIDTH+2*bleed,height=HEIGHT+2*bleed)
        # Actual added canvas around the trim, not boxes outside the MediaBox.
        page.pop('/Annots', None)
        sheet.merge_transformed_page(page, Transformation().translate(bleed,bleed))
        sheet.trimbox = RectangleObject((bleed,bleed,bleed+WIDTH,bleed+HEIGHT))
        sheet.bleedbox = RectangleObject((0,0,WIDTH+2*bleed,HEIGHT+2*bleed))
        writer.add_page(sheet)
    if len(writer.pages)<32:
        raise ValueError('Intérieur inférieur à 32 pages : compléter le contenu avant impression brochée')
    writer.add_metadata({'/Title':str(reader.metadata.get('/Title','Livre Astral')),
        '/Author':'Plume Astrale','/PlumeDesignVersion':DESIGN_VERSION,
        '/PlumeInteriorStart':'0','/PlumeExport':'Lulu interior A5 with 3.175mm bleed'})
    out=io.BytesIO(); writer.write(out)
    return out.getvalue()


def lulu_cover(manuscript, *, width_mm, height_mm, front_box_mm, back_box_mm):
    """Cover spread using rectangles from the exact Lulu product template.

    No estimated spine, binding or hardcover hinge. Rectangles are x,y,w,h from
    the bottom left in mm, excluding the template's bleed/safety area.
    """
    _fonts()
    from reportlab.pdfgen.canvas import Canvas
    if width_mm<=0 or height_mm<=0:
        raise ValueError('Dimensions Lulu invalides')
    for box in (front_box_mm,back_box_mm):
        x,y,w,h=box
        if min(x,y)<0 or min(w,h)<=0 or x+w>width_mm or y+h>height_mm:
            raise ValueError('Zone de couverture hors gabarit Lulu')
    stream=io.BytesIO()
    c=Canvas(stream,pagesize=(width_mm*mm,height_mm*mm),initialFontName='PlumeBook')
    c.setFillColor(NAVY);c.rect(0,0,width_mm*mm,height_mm*mm,fill=1,stroke=0)
    x,y,w,h=front_box_mm
    c.setFont('PlumeBook',18);c.setFillColor(colors.HexColor('#F6EAD2'))
    bx,by,bw,bh=back_box_mm
    p=Paragraph('Une lecture personnelle de votre ciel, pour explorer vos élans, vos liens et vos possibilités.',
        ParagraphStyle('Back',fontName='PlumeBook',fontSize=15,leading=21,textColor=colors.HexColor('#F6EAD2')))
    _,ph=p.wrap((bw-24)*mm,(bh-30)*mm);p.drawOn(c,(bx+12)*mm,(by+bh*.65)*mm-ph)
    c.showPage();c.save()
    writer=PdfWriter(clone_from=io.BytesIO(stream.getvalue()))
    background=writer.pages[0]
    from pypdf import Transformation
    front_stream=io.BytesIO()
    front_canvas=Canvas(front_stream,pagesize=(WIDTH,HEIGHT),initialFontName='PlumeBook')
    front=_Cover(manuscript)
    front.canv=front_canvas
    front.draw()
    front_canvas.showPage();front_canvas.save()
    digital=PdfReader(io.BytesIO(front_stream.getvalue())).pages[0]
    background.merge_transformed_page(digital,Transformation().scale(w/148,h/210).translate(x*mm,y*mm))
    _embed_only_fonts(writer)
    out=io.BytesIO();writer.write(out)
    return out.getvalue()
