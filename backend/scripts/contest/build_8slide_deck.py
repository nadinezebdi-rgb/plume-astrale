"""Génère un deck 8 slides optimisé pour le concours Emergent.

Structure :
1. Hero — Plume Astrale (promesse propre)
2. The problem — Why personal astrology feels empty
3. Why it's useful — The reframe (new slide)
4. The product journey — Enter / Explore / Keep
5. Built with Emergent — Tech credibility
6. Market Validation — KPIs big (104 payments, 13× ROAS, 183€, Live)
7. Business model + Roadmap — Paid readings → book → gift
8. Founder — Nadine Zebdi

Style : navy #142342 + gold #D4AF37 (cohérent avec le PDF Thème Natal).
"""
import copy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree

# ─── Design tokens ───────────────────────────────────────────────
NAVY = RGBColor(0x14, 0x23, 0x42)
GOLD = RGBColor(0xD4, 0xAF, 0x37)
GOLD_DIM = RGBColor(0xA7, 0x81, 0x40)
CREAM = RGBColor(0xF5, 0xEE, 0xE0)
MUTED = RGBColor(0x8A, 0x95, 0xAD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# Slide : 16:9 widescreen (standard contest)
W = Inches(13.333)
H = Inches(7.5)


def set_slide_bg(slide, rgb):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = rgb


def add_text(slide, left, top, width, height, text, *,
             font='Garamond', size=18, bold=False, italic=False,
             color=CREAM, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    lines = text.split('\n') if '\n' in text else [text]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = line
        f = run.font
        f.name = font
        f.size = Pt(size)
        f.bold = bold
        f.italic = italic
        f.color.rgb = color
    return tb


def add_gold_line(slide, left, top, width, height=Emu(10000), color=GOLD):
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    rect.line.fill.background()
    rect.fill.solid()
    rect.fill.fore_color.rgb = color
    return rect


def add_gold_frame(slide, inset=Inches(0.35)):
    """Dessine un double cadre or sur la slide."""
    # outer
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inset, inset,
                                W - 2*inset, H - 2*inset)
    r.fill.background()
    r.line.color.rgb = GOLD_DIM
    r.line.width = Pt(0.5)


def add_page_footer(slide, index, total=8, title=''):
    add_text(slide, Inches(0.6), H - Inches(0.5), Inches(4), Inches(0.3),
             'PLUME ASTRALE', font='Garamond', size=9, color=MUTED, align=PP_ALIGN.LEFT)
    if title:
        add_text(slide, Inches(5), H - Inches(0.5), Inches(3.33), Inches(0.3),
                 title, font='Garamond', size=9, italic=True, color=MUTED, align=PP_ALIGN.CENTER)
    add_text(slide, W - Inches(1.6), H - Inches(0.5), Inches(1), Inches(0.3),
             f'{index} / {total}', font='Garamond', size=9, color=MUTED, align=PP_ALIGN.RIGHT)


def add_slide_title(slide, title_text, subtitle_text=None):
    """Titre H1 + sous-titre italique or."""
    add_text(slide, Inches(0.9), Inches(0.9), W - Inches(1.8), Inches(0.9),
             title_text, font='Garamond', size=36, color=CREAM, align=PP_ALIGN.LEFT)
    if subtitle_text:
        add_text(slide, Inches(0.9), Inches(1.7), W - Inches(1.8), Inches(0.5),
                 subtitle_text, font='Garamond', size=18, italic=True,
                 color=GOLD, align=PP_ALIGN.LEFT)
    add_gold_line(slide, Inches(0.9), Inches(2.4), Inches(1.2))


# ─── BUILD ───────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width = W
prs.slide_height = H
blank = prs.slide_layouts[6]

# ─── Slide 1 — HERO ──────────────────────────────────────────────
s1 = prs.slides.add_slide(blank)
set_slide_bg(s1, NAVY)
add_gold_frame(s1)
add_text(s1, Inches(0.9), Inches(0.9), Inches(4), Inches(0.4),
         'P L U M E   A S T R A L E', font='Garamond', size=11,
         color=GOLD, align=PP_ALIGN.LEFT)
add_text(s1, Inches(0.9), Inches(2.4), W - Inches(1.8), Inches(1.6),
         'Personal birth-chart readings\nyou can keep.',
         font='Garamond', size=56, color=CREAM, align=PP_ALIGN.LEFT)
add_text(s1, Inches(0.9), Inches(4.6), W - Inches(1.8), Inches(0.5),
         'A guided, printable reading of your sky — composed from your exact birth data.',
         font='Garamond', size=18, italic=True, color=GOLD, align=PP_ALIGN.LEFT)
add_gold_line(s1, Inches(0.9), Inches(5.4), Inches(1.5))
add_text(s1, Inches(0.9), Inches(5.7), W - Inches(1.8), Inches(0.4),
         'Live product · plume-astrale.fr',
         font='Garamond', size=12, color=MUTED, align=PP_ALIGN.LEFT)
add_page_footer(s1, 1, 8)

# ─── Slide 2 — THE PROBLEM ───────────────────────────────────────
s2 = prs.slides.add_slide(blank)
set_slide_bg(s2, NAVY)
add_gold_frame(s2)
add_slide_title(s2, 'The user problem', 'A personal reading needs context.')
items = [
    ('01', 'Interpretation', 'Birth-chart symbols are hard to read without a trusted voice.'),
    ('02', 'Reading path', 'A long report without a path feels overwhelming.'),
    ('03', 'Something to keep', 'People want a tangible output they can revisit.'),
]
col_w = (W - Inches(2.4)) / 3
for i, (num, label, body) in enumerate(items):
    x = Inches(0.9) + col_w * i + Inches(0.3) * i
    add_text(s2, x, Inches(3.2), col_w, Inches(0.5),
             num, font='Garamond', size=36, color=GOLD, align=PP_ALIGN.LEFT)
    add_text(s2, x, Inches(4.0), col_w, Inches(0.5),
             label, font='Garamond', size=18, bold=True, color=CREAM, align=PP_ALIGN.LEFT)
    add_text(s2, x, Inches(4.6), col_w, Inches(1.5),
             body, font='Garamond', size=14, color=MUTED, align=PP_ALIGN.LEFT)
add_page_footer(s2, 2, 8)

# ─── Slide 3 — WHY IT'S USEFUL ───────────────────────────────────
s3 = prs.slides.add_slide(blank)
set_slide_bg(s3, NAVY)
add_gold_frame(s3)
add_slide_title(s3, "Why it's useful", 'A gentle, honest reading you can trust.')
useful = [
    ('A clear reading path', 'Guided from first page to synthesis — never a wall of symbols.'),
    ('In your own voice', 'AI composes a prose reading in a literary, intimate register.'),
    ('Something to keep', 'A luxurious PDF (32+ pages) you can return to for years.'),
    ('Transparent and symbolic', 'No prediction, no fate — a frame for self-reflection.'),
]
for i, (label, body) in enumerate(useful):
    row = i // 2
    col = i % 2
    x = Inches(0.9) + col * (W - Inches(1.8)) / 2
    y = Inches(3.0) + row * Inches(1.8)
    add_text(s3, x, y, (W - Inches(1.8))/2 - Inches(0.3), Inches(0.5),
             label, font='Garamond', size=20, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_text(s3, x, y + Inches(0.6), (W - Inches(1.8))/2 - Inches(0.3), Inches(1.1),
             body, font='Garamond', size=14, color=CREAM, align=PP_ALIGN.LEFT)
add_page_footer(s3, 3, 8)

# ─── Slide 4 — PRODUCT JOURNEY ───────────────────────────────────
s4 = prs.slides.add_slide(blank)
set_slide_bg(s4, NAVY)
add_gold_frame(s4)
add_slide_title(s4, 'The product journey', 'A guided reading in three steps.')
steps = [
    ('01', 'Enter', 'The user enters her birth date, time and place.'),
    ('02', 'Explore', 'She reads a personalized chart interpretation (planets · houses · aspects).'),
    ('03', 'Keep', 'She downloads a 32-page PDF, elegantly composed, in her name.'),
]
for i, (num, label, body) in enumerate(steps):
    x = Inches(0.9) + col_w * i + Inches(0.3) * i
    add_text(s4, x, Inches(3.2), col_w, Inches(0.5),
             num, font='Garamond', size=36, color=GOLD, align=PP_ALIGN.LEFT)
    add_text(s4, x, Inches(4.0), col_w, Inches(0.5),
             label, font='Garamond', size=22, bold=True, color=CREAM, align=PP_ALIGN.LEFT)
    add_text(s4, x, Inches(4.7), col_w, Inches(1.5),
             body, font='Garamond', size=14, color=MUTED, align=PP_ALIGN.LEFT)
add_page_footer(s4, 4, 8, 'Illustrative layout')

# ─── Slide 5 — BUILT WITH EMERGENT ───────────────────────────────
s5 = prs.slides.add_slide(blank)
set_slide_bg(s5, NAVY)
add_gold_frame(s5)
add_slide_title(s5, 'Built with Emergent', 'A connected application.')
tech = [
    ('01', 'Interface', 'A React application with a guided user journey.'),
    ('02', 'Intelligence', 'Astrology data + AI-assisted interpretation (GPT-5.4).'),
    ('03', 'Delivery', 'Payment, PDF generation and secure email delivery.'),
]
for i, (num, label, body) in enumerate(tech):
    x = Inches(0.9) + col_w * i + Inches(0.3) * i
    add_text(s5, x, Inches(3.2), col_w, Inches(0.5),
             num, font='Garamond', size=36, color=GOLD, align=PP_ALIGN.LEFT)
    add_text(s5, x, Inches(4.0), col_w, Inches(0.5),
             label, font='Garamond', size=22, bold=True, color=CREAM, align=PP_ALIGN.LEFT)
    add_text(s5, x, Inches(4.7), col_w, Inches(1.5),
             body, font='Garamond', size=14, color=MUTED, align=PP_ALIGN.LEFT)
add_page_footer(s5, 5, 8)

# ─── Slide 6 — MARKET VALIDATION (climax) ───────────────────────
s6 = prs.slides.add_slide(blank)
set_slide_bg(s6, NAVY)
add_gold_frame(s6)
add_slide_title(s6, 'Market validation', 'Not a prototype — a product the market has already bought.')

kpis = [
    ('104', 'paid orders', 'in the first weeks of distribution.'),
    ('13×', 'ROAS', 'on 183 € of Facebook Ads spend.'),
    ('32', 'pages', 'in each luxury PDF, delivered automatically.'),
]
for i, (big, label, note) in enumerate(kpis):
    x = Inches(0.9) + col_w * i + Inches(0.3) * i
    add_text(s6, x, Inches(3.1), col_w, Inches(1.4),
             big, font='Garamond', size=80, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_text(s6, x, Inches(4.7), col_w, Inches(0.4),
             label, font='Garamond', size=18, italic=True, color=CREAM, align=PP_ALIGN.LEFT)
    add_text(s6, x, Inches(5.2), col_w, Inches(1.0),
             note, font='Garamond', size=12, color=MUTED, align=PP_ALIGN.LEFT)
add_text(s6, Inches(0.9), Inches(6.4), W - Inches(1.8), Inches(0.4),
         '183 € spent · 104 paying customers · 13× return · live at plume-astrale.fr',
         font='Garamond', size=11, italic=True, color=GOLD_DIM, align=PP_ALIGN.LEFT)
add_page_footer(s6, 6, 8)

# ─── Slide 7 — LIVE ACQUISITION ─────────────────────────────────
s_live = prs.slides.add_slide(blank)
set_slide_bg(s_live, NAVY)
add_gold_frame(s_live)
add_slide_title(s_live, 'Live acquisition — running now',
                'A Facebook campaign is active while you read this slide.')

# Visual : 3 big KPIs du jour
live_kpis = [
    ('1 142', 'impressions', 'in the first 24 hours of today\'s wave.'),
    ('1 071', 'people reached', 'in a Scorpio-sign zodiac segment.'),
    ('10,34 €', 'spent today', 'campaign runs until Oct 27 — scaling live.'),
]
for i, (big, label, note) in enumerate(live_kpis):
    x = Inches(0.9) + col_w * i + Inches(0.3) * i
    add_text(s_live, x, Inches(3.0), col_w, Inches(1.0),
             big, font='Garamond', size=48, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_text(s_live, x, Inches(4.3), col_w, Inches(0.4),
             label, font='Garamond', size=16, italic=True, color=CREAM, align=PP_ALIGN.LEFT)
    add_text(s_live, x, Inches(4.8), col_w, Inches(1.1),
             note, font='Garamond', size=12, color=MUTED, align=PP_ALIGN.LEFT)

# Ad snippet en bas, mis en valeur
add_text(s_live, Inches(0.9), Inches(6.1), W - Inches(1.8), Inches(0.3),
         'Ad currently running:', font='Garamond', size=10, color=MUTED, align=PP_ALIGN.LEFT)
add_text(s_live, Inches(0.9), Inches(6.4), W - Inches(1.8), Inches(0.4),
         '« ♏ Scorpion… cette semaine, quelque chose est en… »',
         font='Garamond', size=14, italic=True, color=GOLD, align=PP_ALIGN.LEFT)
add_page_footer(s_live, 7, 9)

# ─── Slide 8 — BUSINESS MODEL + ROADMAP ─────────────────────────
s7 = prs.slides.add_slide(blank)
set_slide_bg(s7, NAVY)
add_gold_frame(s7)
add_slide_title(s7, 'Business model & roadmap', 'Paid readings today — a book experience tomorrow.')
columns = [
    ('Today', [
        '· Personal reports purchased individually',
        '· Credit system for recurring readings',
        '· 100% self-serve via Stripe',
    ]),
    ('Next 90 days', [
        '· Consistent 32-page print sample',
        '· Luxurious printed edition (A5 cream)',
        '· Gift pilot for the holiday season',
    ]),
    ('Horizon', [
        '· Synastry (compatibility) at scale',
        '· English market expansion',
        '· Book + ritual box subscription',
    ]),
]
for i, (col_title, bullets) in enumerate(columns):
    x = Inches(0.9) + col_w * i + Inches(0.3) * i
    add_text(s7, x, Inches(3.0), col_w, Inches(0.4),
             col_title, font='Garamond', size=20, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_text(s7, x, Inches(3.6), col_w, Inches(3.0),
             '\n'.join(bullets), font='Garamond', size=14, color=CREAM, align=PP_ALIGN.LEFT)
add_page_footer(s7, 8, 9)

# ─── Slide 9 — FOUNDER ──────────────────────────────────────────
s8 = prs.slides.add_slide(blank)
set_slide_bg(s8, NAVY)
add_gold_frame(s8)
add_text(s8, Inches(0.9), Inches(1.8), W - Inches(1.8), Inches(1.0),
         'Thank you.', font='Garamond', size=56, color=CREAM, align=PP_ALIGN.LEFT)
add_gold_line(s8, Inches(0.9), Inches(3.3), Inches(1.5))
add_text(s8, Inches(0.9), Inches(3.6), W - Inches(1.8), Inches(0.6),
         'Nadine Zebdi', font='Garamond', size=28, color=GOLD, align=PP_ALIGN.LEFT)
add_text(s8, Inches(0.9), Inches(4.3), W - Inches(1.8), Inches(0.5),
         'Founder of Plume Astrale', font='Garamond', size=16, italic=True, color=CREAM, align=PP_ALIGN.LEFT)
add_text(s8, Inches(0.9), Inches(4.9), W - Inches(1.8), Inches(0.5),
         'Digital product designer and developer', font='Garamond', size=14, color=MUTED, align=PP_ALIGN.LEFT)
add_text(s8, Inches(0.9), Inches(5.8), W - Inches(1.8), Inches(0.5),
         'plume-astrale.fr', font='Garamond', size=16, italic=True, color=GOLD, align=PP_ALIGN.LEFT)
add_page_footer(s8, 9, 9)


# ─── Speaker notes ──────────────────────────────────────────────
NOTES = {
    1: "Plume Astrale is a live product that offers personal birth-chart readings — composed from the user's exact birth data and delivered as a 32-page luxury PDF she can keep.",
    2: "People who turn to astrology for self-reflection face three friction points: symbols are hard to interpret, long reports feel like walls of text, and digital-only readings leave no tangible trace to come back to.",
    3: "Plume Astrale answers these frictions directly: a guided reading path, prose composed in a literary voice, a keepable PDF — framed symbolically, with no fate claims.",
    4: "The journey is three steps: Enter birth details · Explore the chart with its interpretation · Keep the 32-page PDF, elegantly composed.",
    5: "Built end-to-end with Emergent: React UI, astrology data + GPT-5.4 for the voice, Stripe for payment, automated PDF delivery.",
    6: "This is not a prototype. 104 paid orders have been made. 13× ROAS on 183 € of Facebook Ads. Each report is 32 pages, delivered automatically. The market has already answered yes.",
    7: "And distribution is active TODAY. A Facebook campaign targeting Scorpio-sign users is live right now, 1,142 impressions in the first 24 hours, running until October 27. We're not showing you historical data — we're showing you a product in motion.",
    8: "Today: paid individual readings, credit system, 100% self-serve. Next 90 days: consistent print sample, luxurious printed edition, holiday gift pilot. Horizon: synastry at scale, English market, and a subscription box combining book and ritual.",
    9: "Thank you. I'm Nadine Zebdi, founder of Plume Astrale, digital product designer and developer. plume-astrale.fr",
}
for i, slide in enumerate(prs.slides, 1):
    tf = slide.notes_slide.notes_text_frame
    tf.text = NOTES.get(i, '')


OUT = '/app/video_pitch_assets/Plume-Astrale-Contest-FINAL-9slides.pptx'
prs.save(OUT)
print(f'✅ Deck 8 slides sauvegardé : {OUT}')
print(f'   Slides : {len(prs.slides)}')
print(f'   Taille : {prs.slide_width}x{prs.slide_height} EMU (16:9)')
