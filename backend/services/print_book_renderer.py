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

ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 148 * mm, 210 * mm
NAVY = colors.HexColor('#142342')
INK = colors.HexColor('#243047')
GOLD = colors.HexColor('#A78140')
MUTED = colors.HexColor('#526077')
DESIGN_VERSION = 'plume-book-flow-2026-10'


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


class _BookDoc(BaseDocTemplate):
    def __init__(self, stream, name):
        super().__init__(stream, pagesize=(WIDTH, HEIGHT), leftMargin=21*mm,
            rightMargin=17*mm, topMargin=20*mm, bottomMargin=23*mm,
            title=f'Le Livre Astral de {name}', author='Plume Astrale')
        self.person_name = name
        self.addPageTemplates(PageTemplate('book',
            frames=[Frame(21*mm,23*mm,110*mm,167*mm,id='text',
                          leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],
            onPage=self._page))

    def _page(self, canvas, doc):
        # Mirrored gutter, identical usable width on recto and verso.
        self.pageTemplate.frames[0]._x1 = (21 if doc.page % 2 else 17)*mm
        self.pageTemplate.frames[0]._geom()
        if doc.page <= 2:
            return
        canvas.saveState()
        canvas.setFillColor(MUTED)
        canvas.setFont('PlumeBook', 9)
        canvas.drawString(17*mm, 12*mm, 'PLUME ASTRALE')
        canvas.drawRightString(WIDTH-17*mm,12*mm,str(doc.page-2))
        canvas.restoreState()

    def afterFlowable(self, flowable):
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


def _append_blocks(story, chapter, styles):
    for block in chapter.blocks:
        kind = getattr(block.kind,'value',block.kind)
        data = block.data or {}
        if kind in ('chapter_opening','feather'):
            continue
        if kind == 'page_break':
            if story and not isinstance(story[-1],PageBreak):
                story.append(PageBreak())
        elif kind == 'h2':
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
        title = 'Introduction — Comment lire votre thème' if chapter in intro else chapter.title
        story.append(_heading(title,styles,f'chapter-{index}'))
        if chapter.kicker:
            story.append(Paragraph(html.escape(chapter.kicker),styles['kicker']))
        _append_blocks(story,chapter,styles)
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
