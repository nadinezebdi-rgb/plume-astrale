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
        'book_title_default': 'Le Livre Astral',
        'cover_subtitle': 'Une lecture personnelle de votre ciel de naissance',
        'cover_edition': 'ÉDITION PERSONNELLE',
        'intro_para': ('Ce livre est composé à partir de votre ciel de naissance. '
                       'Il propose une lecture symbolique et personnelle, à confronter à votre expérience. '
                       'Il ne prédit pas un avenir certain et ne remplace pas votre liberté de choix.'),
        'preface_title': 'Préface',
        'preface_paras_tpl': [
            '{name}, ce livre vous invite à faire une pause et à regarder votre histoire sous un autre angle. Votre thème de naissance en est le point de départ : une carte singulière, composée pour un lieu et un instant précis.',
            'Les pages qui suivent mettent en mots des contrastes, des élans et des besoins. Vous pourrez vous reconnaître dans certaines lectures, en discuter d’autres et laisser de côté ce qui ne vous parle pas. Vous restez la personne la mieux placée pour donner du sens à votre vécu.',
            'Prenez le temps de lire, de noter vos réactions et de revenir sur un passage lorsque votre situation évolue. L’intention de ce livre est de soutenir cette attention à vous-même, avec nuance, curiosité et bienveillance.',
        ],
        'toc_title': 'Sommaire',
        'intro_chapter_title': 'Introduction — Comment lire votre thème',
        'closing_title': 'Pour poursuivre votre lecture',
        'closing_paras': [
            "Choisissez une idée qui vous a touché et reliez-la à une situation concrète de votre vie. Qu’est-ce qu’elle vous aide à nommer ? Quelle autre explication pourriez-vous envisager ?",
            "Notez une action simple à essayer cette semaine. Revenez ensuite à votre livre pour observer ce qui s’est éclairci, ce qui a changé et ce qui demande encore du temps.",
            "Plume Astrale — Édition personnelle. Les interprétations relèvent d’une démarche symbolique de connaissance de soi.",
        ],
        'cutout_hint': '✁  à découper · à offrir · à conserver',
        'cutout_sig': '— Plume Astrale, écrit pour toi',
    },
    'en': {
        'book_title_default': 'The Astral Book',
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


def _plain(value):
    return re.sub(r'<[^>]+>', '', html.unescape(str(value or ''))).strip()


def _paragraphs(value):
    # Only server-generated prose, no arbitrary HTML, image paths or links.
    text = str(value or '').replace('\r\n', '\n')
    text = re.sub(r'</p\s*>|<br\s*/?>', '\n\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
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

    def __init__(self, manuscript, image_path=None):
        super().__init__()
        self.m = manuscript
        self.image_path = image_path

    def draw(self):
        c = self.canv
        c.saveState()
        c.resetTransforms()
        c.setFillColor(NAVY)
        c.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
        if self.image_path:
            path = Path(self.image_path)
            if not path.is_file():
                raise ValueError('Illustration de couverture introuvable')
            c.drawImage(str(path), 0, 0, WIDTH, HEIGHT, mask='auto', preserveAspectRatio=False)
            c.setFillColor(NAVY)
            c.setFillAlpha(.85)
            c.rect(9*mm, 35*mm, WIDTH-18*mm, HEIGHT-70*mm, fill=1, stroke=0)
            c.setFillAlpha(1)
        c.setStrokeColor(GOLD)
        c.setLineWidth(.6)
        c.rect(9*mm, 9*mm, WIDTH-18*mm, HEIGHT-18*mm)
        # Celestial engraving: no feathers, no simulated natal positions.
        cx, cy, radius = WIDTH/2, 86*mm, 26*mm
        for r in (radius, radius-2*mm, radius*.7):
            c.circle(cx, cy, r, stroke=1, fill=0)
        for i in range(12):
            angle = i*math.pi/6
            c.line(cx+radius*.85*math.cos(angle), cy+radius*.85*math.sin(angle),
                   cx+radius*math.cos(angle), cy+radius*math.sin(angle))
        c.circle(cx, cy, 6*mm, stroke=1, fill=0)
        for dx,dy,size in [(-34,22,1),(36,-18,.7),(-27,-29,.6),(31,33,.7)]:
            c.circle(cx+dx*mm, cy+dy*mm, size, fill=1, stroke=0)
        c.setFillColor(colors.HexColor('#F6EAD2'))
        c.setFont('PlumeBook', 11)
        c.drawCentredString(WIDTH/2, 177*mm, 'P L U M E   A S T R A L E')
        title = (self.m.astro_data or {}).get('book_title') or 'Le Livre Astral'
        style = ParagraphStyle('CoverTitle', fontName='PlumeBook', fontSize=29,
            leading=32, alignment=TA_CENTER, textColor=colors.HexColor('#F6EAD2'))
        title_p = Paragraph(html.escape(title), style)
        _, h = title_p.wrap(WIDTH-28*mm, 80*mm)
        title_p.drawOn(c, 14*mm, 148*mm-h)
        name_style = ParagraphStyle('CoverName', parent=style, fontSize=23, leading=26)
        for font_size in (23, 21, 19, 17, 15, 13):
            name_style.fontSize = font_size
            name_style.leading = font_size + 2
            name_p = Paragraph(html.escape(self.m.first_name), name_style)
            _, h = name_p.wrap(WIDTH-28*mm, 45*mm)
            if h <= 42:
                break
        if h > 42:
            raise ValueError('Nom trop long pour la couverture : utiliser le prénom de lecture')
        name_p.drawOn(c, 14*mm, 132*mm-h)
        c.setFont('PlumeBook-Italic', 12)
        c.drawCentredString(WIDTH/2, 40*mm, 'Une lecture personnelle de votre ciel de naissance')
        c.setFont('PlumeBook', 10)
        c.drawCentredString(WIDTH/2, 25*mm, 'ÉDITION PERSONNELLE')
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
    def __init__(self, stream, name):
        super().__init__(stream, pagesize=(WIDTH, HEIGHT), leftMargin=21*mm,
            rightMargin=17*mm, topMargin=20*mm, bottomMargin=23*mm,
            title=f'Le Livre Astral de {name}', author='Plume Astrale')
        self.person_name = name
        self._cutout_pages: set[int] = set()
        self.addPageTemplates(PageTemplate('book',
            frames=[Frame(21*mm,23*mm,110*mm,167*mm,id='text',
                          leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],
            onPage=self._page))

    def _page(self, canvas, doc):
        # Mirrored gutter, identical usable width on recto and verso.
        self.pageTemplate.frames[0]._x1 = (21 if doc.page % 2 else 17)*mm
        self.pageTemplate.frames[0]._geom()
        # Fond crème parchemin sur toutes les pages intérieures (hors couverture p.1-2)
        if doc.page > 2:
            canvas.saveState()
            canvas.setFillColor(CREAM)
            canvas.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
            canvas.restoreState()
        if doc.page <= 2:
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
        canvas.drawRightString(WIDTH-17*mm,12*mm,str(doc.page-2))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if getattr(flowable, '_cutout_marker', False):
            self._cutout_pages.add(self.page)
            return
        if getattr(flowable, '_toc_key', None):
            key = flowable._toc_key
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flowable.getPlainText(),key,level=0,closed=False)
            self.notify('TOCEntry',(0,flowable.getPlainText(),self.page-2,key))


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
        path = _LIB_ROOT / 'planets' / 'sun_1080.png'
    elif 'house' in slug or 'maison' in slug:
        path = _LIB_ROOT / 'houses' / 'house1_1080.png'
    elif 'synthese' in slug or 'ciel' in slug:
        path = _LIB_ROOT / 'tarot' / '17_l_etoile_1080.png'
    elif 'aspect' in slug:
        path = _LIB_ROOT / 'tarot' / '08_la_force_1080.png'
    elif 'preface' in slug or 'introduction' in slug:
        path = _LIB_ROOT / 'tarot' / '01_le_bateleur_512.png'
    else:
        path = None
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
                image._restrictSize(104*mm,104*mm)
                story.append(image)
        elif kind == 'image':
            # Unknown image identifiers are not silently turned into invented images.
            raise ValueError('Illustration sans fichier résolu dans le manuscrit')
        elif kind == 'hairline':
            story.append(HRFlowable(width='45%',thickness=.5,color=GOLD,spaceAfter=12))
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


def render_book_pdf(manuscript, *, cover_png_path=None):
    """Full reading edition; print export removes only explicitly marked cover leaves."""
    validate_manuscript(manuscript)
    _fonts()
    styles = _styles()
    stream = io.BytesIO()
    doc = _BookDoc(stream,manuscript.first_name)
    story = [_Cover(manuscript,cover_png_path),PageBreak(),Spacer(1,5*mm),PageBreak()]
    story += [Spacer(1,22*mm),_heading('Le Livre Astral',styles),
              _heading(manuscript.first_name,styles),Spacer(1,20*mm)]
    for text in _paragraphs('Ce livre est composé à partir de votre ciel de naissance. '
        'Il propose une lecture symbolique et personnelle, à confronter à votre expérience. '
        'Il ne prédit pas un avenir certain et ne remplace pas votre liberté de choix.'):
        story.append(Paragraph(text,styles['body']))
    story += [PageBreak(),_heading('Préface',styles)]
    preface = [
        f"{manuscript.first_name}, ce livre vous invite à faire une pause et à regarder votre histoire sous un autre angle. Votre thème de naissance en est le point de départ : une carte singulière, composée pour un lieu et un instant précis.",
        "Les pages qui suivent mettent en mots des contrastes, des élans et des besoins. Vous pourrez vous reconnaître dans certaines lectures, en discuter d’autres et laisser de côté ce qui ne vous parle pas. Vous restez la personne la mieux placée pour donner du sens à votre vécu.",
        "Prenez le temps de lire, de noter vos réactions et de revenir sur un passage lorsque votre situation évolue. L’intention de ce livre est de soutenir cette attention à vous-même, avec nuance, curiosité et bienveillance.",
    ]
    for text in preface:
        story.append(Paragraph(html.escape(text),styles['body']))
    story += [PageBreak(),_heading('Sommaire',styles)]
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
        title = 'Introduction — Comment lire votre thème' if chapter in intro else chapter.title
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
            # Signature discrète en bas de page découpable
            story.append(Spacer(1, 12*mm))
            story.append(Paragraph(
                '<i>— Plume Astrale, écrit pour toi</i>',
                ParagraphStyle('CutoutSig', parent=styles['small'],
                               alignment=TA_CENTER, textColor=GOLD),
            ))
        while isinstance(story[-1],PageBreak):
            story.pop()
    story += [PageBreak(),_heading('Pour poursuivre votre lecture',styles)]
    for text in [
        "Choisissez une idée qui vous a touché et reliez-la à une situation concrète de votre vie. Qu’est-ce qu’elle vous aide à nommer ? Quelle autre explication pourriez-vous envisager ?",
        "Notez une action simple à essayer cette semaine. Revenez ensuite à votre livre pour observer ce qui s’est éclairci, ce qui a changé et ce qui demande encore du temps.",
        "Plume Astrale — Édition personnelle. Les interprétations relèvent d’une démarche symbolique de connaissance de soi.",
    ]:
        story.append(Paragraph(html.escape(text),styles['body']))
    from functools import partial
    from reportlab.pdfgen.canvas import Canvas
    doc.multiBuild(story,maxPasses=8,canvasmaker=partial(Canvas,initialFontName='PlumeBook'))
    reader = PdfReader(io.BytesIO(stream.getvalue()))
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    _embed_only_fonts(writer)
    # Interior is even; never invent pages to reach an advertised length.
    if (len(reader.pages)-2)%2:
        writer.add_blank_page(width=WIDTH,height=HEIGHT)
    writer.add_metadata({'/Title':f'Le Livre Astral de {manuscript.first_name}',
        '/Author':'Plume Astrale','/PlumeDesignVersion':DESIGN_VERSION,
        '/PlumeInteriorStart':'2'})
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
