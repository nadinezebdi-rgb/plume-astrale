"""Templates de pages éditoriales pour les PDF Plume Astrale."""

from __future__ import annotations

import os
from typing import Optional, List

from reportlab.lib.units import cm
from reportlab.platypus import (
    Spacer,
    PageBreak,
    Image as RLImage,
    Table,
    TableStyle,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor

from services.pdf_theme import SafeParagraph as Paragraph
from services.pdf_editorial_system import (
    GOLD, CREAM, GREY_SUBTLE, GOLD_HEX, CREAM_HEX, GREY_HEX,
    H_CHAPTER, H_PAGE, SUBTITLE, BODY, QUOTE, CALLOUT, CAPTION,
    LEAD_CHAPTER, LEAD_PAGE, LEAD_BODY, LEAD_QUOTE, LEAD_CALLOUT,
    SP_XS, SP_S, SP_M, SP_L, SP_XL, SP_XXL,
    styles_cormorant, styles_cormorant_italic, styles_cinzel,
)


def t_quote(
    story,
    quote_text: str,
    attribution: Optional[str] = None,
) -> None:
    """Page de citation."""
    story.append(Spacer(1, 8.5 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦</font>',
        ParagraphStyle(
            'quote_star',
            fontName=styles_cinzel(),
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=SP_M,
        ),
    ))
    story.append(Paragraph(
        f'« {quote_text} »',
        ParagraphStyle(
            'quote_body',
            fontName=styles_cormorant_italic(),
            fontSize=QUOTE,
            textColor=CREAM,
            alignment=TA_CENTER,
            leading=LEAD_QUOTE,
        ),
    ))
    if attribution:
        story.append(Spacer(1, SP_L))
        story.append(Paragraph(
            f'— {attribution}',
            ParagraphStyle(
                'quote_attr',
                fontName=styles_cinzel(),
                fontSize=CAPTION,
                textColor=GOLD,
                alignment=TA_CENTER,
            ),
        ))
    story.append(PageBreak())


def t_chapter_opening(
    story,
    roman: str,
    title: str,
    kicker: Optional[str] = None,
    illustration_path: Optional[str] = None,
) -> None:
    """Ouverture d'acte."""
    story.append(Spacer(1, 3.5 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">ACTE {roman}</font>',
        ParagraphStyle(
            'co_roman',
            fontName=styles_cinzel(),
            fontSize=13,
            alignment=TA_CENTER,
            spaceAfter=SP_M,
        ),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle(
            'co_title',
            fontName=styles_cormorant(),
            fontSize=H_CHAPTER,
            textColor=CREAM,
            alignment=TA_CENTER,
            leading=LEAD_CHAPTER,
            spaceAfter=SP_L,
        ),
    ))
    if kicker:
        story.append(Paragraph(
            kicker,
            ParagraphStyle(
                'co_kicker',
                fontName=styles_cormorant_italic(),
                fontSize=SUBTITLE,
                textColor=GREY_SUBTLE,
                alignment=TA_CENTER,
                leading=LEAD_BODY,
                spaceAfter=SP_XL,
            ),
        ))
    if illustration_path and os.path.exists(illustration_path):
        try:
            story.append(RLImage(
                illustration_path,
                width=8 * cm,
                height=8 * cm,
                mask='auto',
            ))
        except Exception:
            pass
    story.append(PageBreak())


def t_portrait(
    story,
    chapter_tag: str,
    title: str,
    question: str,
    body_html: str,
    illustration_path: Optional[str] = None,
) -> None:
    """Portrait de chapitre."""
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ {chapter_tag.upper()} ✦</font>',
        ParagraphStyle(
            'p_tag',
            fontName=styles_cinzel(),
            fontSize=CAPTION,
            alignment=TA_CENTER,
            spaceAfter=SP_S,
        ),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle(
            'p_title',
            fontName=styles_cormorant(),
            fontSize=H_PAGE,
            textColor=CREAM,
            alignment=TA_CENTER,
            leading=LEAD_PAGE,
            spaceAfter=SP_M,
        ),
    ))
    if illustration_path and os.path.exists(illustration_path):
        try:
            story.append(RLImage(
                illustration_path,
                width=5 * cm,
                height=5 * cm,
                mask='auto',
            ))
            story.append(Spacer(1, SP_S))
        except Exception:
            pass
    story.append(Paragraph(
        f'« {question} »',
        ParagraphStyle(
            'p_q',
            fontName=styles_cormorant_italic(),
            fontSize=SUBTITLE,
            textColor=GOLD,
            alignment=TA_CENTER,
            leading=LEAD_BODY,
            spaceAfter=SP_L,
        ),
    ))
    story.append(Paragraph(
        body_html,
        ParagraphStyle(
            'p_body',
            fontName=styles_cormorant(),
            fontSize=BODY,
            textColor=CREAM,
            alignment=TA_JUSTIFY,
            leading=LEAD_BODY,
            leftIndent=1.5 * cm,
            rightIndent=1.5 * cm,
        ),
    ))
    story.append(PageBreak())


def t_analysis(
    story,
    title: str,
    body_html: str,
    illustration_path: Optional[str] = None,
    inset_quote: Optional[str] = None,
) -> None:
    """Analyse en deux colonnes, avec continuation sur plusieurs pages."""
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        title,
        ParagraphStyle(
            'a_title',
            fontName=styles_cormorant(),
            fontSize=H_PAGE,
            textColor=CREAM,
            alignment=TA_LEFT,
            leading=LEAD_PAGE,
            spaceAfter=SP_L,
            leftIndent=1.5 * cm,
        ),
    ))
    text_para = Paragraph(
        body_html,
        ParagraphStyle(
            'a_body',
            fontName=styles_cormorant(),
            fontSize=BODY,
            textColor=CREAM,
            alignment=TA_JUSTIFY,
            leading=LEAD_BODY,
        ),
    )
    right_col: list = []
    if illustration_path and os.path.exists(illustration_path):
        try:
            right_col.append(RLImage(
                illustration_path,
                width=6.5 * cm,
                height=6.5 * cm,
                mask='auto',
            ))
            right_col.append(Spacer(1, SP_S))
        except Exception:
            pass
    if inset_quote:
        right_col.append(Paragraph(
            f'<font color="{GOLD_HEX}">« {inset_quote} »</font>',
            ParagraphStyle(
                'a_inset',
                fontName=styles_cormorant_italic(),
                fontSize=CALLOUT,
                textColor=GOLD,
                alignment=TA_LEFT,
                leading=LEAD_CALLOUT,
            ),
        ))

    # Autorise la division d'une ligne trop haute entre plusieurs pages.
    tbl = Table(
        [[text_para, right_col]],
        colWidths=[9 * cm, 7 * cm],
        hAlign='CENTER',
        splitInRow=1,
    )
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, 0), SP_M),
    ]))
    story.append(tbl)
    story.append(PageBreak())


def t_focus(
    story,
    kicker: str,
    single_word: str,
    meaning: str,
) -> None:
    """Page consacrée à une notion."""
    story.append(Spacer(1, 7 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">{kicker.upper()}</font>',
        ParagraphStyle(
            'f_kicker',
            fontName=styles_cinzel(),
            fontSize=CAPTION,
            alignment=TA_CENTER,
            spaceAfter=SP_L,
        ),
    ))
    story.append(Paragraph(
        single_word.upper(),
        ParagraphStyle(
            'f_word',
            fontName=styles_cormorant(),
            fontSize=H_CHAPTER + 8,
            textColor=CREAM,
            alignment=TA_CENTER,
            leading=LEAD_CHAPTER + 10,
            spaceAfter=SP_XL,
        ),
    ))
    story.append(Paragraph(
        meaning,
        ParagraphStyle(
            'f_mean',
            fontName=styles_cormorant_italic(),
            fontSize=SUBTITLE,
            textColor=GREY_SUBTLE,
            alignment=TA_CENTER,
            leading=LEAD_BODY,
            leftIndent=3 * cm,
            rightIndent=3 * cm,
        ),
    ))
    story.append(PageBreak())


def t_callout(
    story,
    title: str,
    tips: List[str],
    memorable_line: str,
) -> None:
    """Trois conseils et une phrase à retenir."""
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ À RETENIR ✦</font>',
        ParagraphStyle(
            'cl_tag',
            fontName=styles_cinzel(),
            fontSize=CAPTION,
            alignment=TA_CENTER,
            spaceAfter=SP_S,
        ),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle(
            'cl_title',
            fontName=styles_cormorant(),
            fontSize=H_PAGE,
            textColor=CREAM,
            alignment=TA_CENTER,
            leading=LEAD_PAGE,
            spaceAfter=SP_L,
        ),
    ))
    for i, tip in enumerate(tips[:3], 1):
        story.append(Paragraph(
            f'<font color="{GOLD_HEX}">{i:02d}</font>&nbsp;&nbsp;{tip}',
            ParagraphStyle(
                f'cl_tip{i}',
                fontName=styles_cormorant(),
                fontSize=CALLOUT,
                textColor=CREAM,
                alignment=TA_LEFT,
                leading=LEAD_CALLOUT,
                leftIndent=2 * cm,
                rightIndent=1.5 * cm,
                spaceAfter=SP_S,
            ),
        ))
    story.append(Spacer(1, SP_L))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">« {memorable_line} »</font>',
        ParagraphStyle(
            'cl_mem',
            fontName=styles_cormorant_italic(),
            fontSize=QUOTE,
            alignment=TA_CENTER,
            leading=LEAD_QUOTE,
            leftIndent=2 * cm,
            rightIndent=2 * cm,
        ),
    ))
    story.append(PageBreak())


def t_ritual(
    story,
    title: str,
    steps: List[str],
    duration: str,
    stone: str,
    color: str,
    breathing: str,
    illustration_path: Optional[str] = None,
) -> None:
    """Étapes et paramètres d'un rituel."""
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ RITUEL ✦</font>',
        ParagraphStyle(
            'r_tag',
            fontName=styles_cinzel(),
            fontSize=CAPTION,
            alignment=TA_CENTER,
            spaceAfter=SP_S,
        ),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle(
            'r_title',
            fontName=styles_cormorant(),
            fontSize=H_PAGE,
            textColor=CREAM,
            alignment=TA_CENTER,
            leading=LEAD_PAGE,
            spaceAfter=SP_M,
        ),
    ))
    if illustration_path and os.path.exists(illustration_path):
        try:
            story.append(RLImage(
                illustration_path,
                width=4.5 * cm,
                height=4.5 * cm,
                mask='auto',
            ))
            story.append(Spacer(1, SP_M))
        except Exception:
            pass

    sens = [
        ['Temps', duration],
        ['Pierre', stone],
        ['Couleur', color],
        ['Souffle', breathing],
    ]
    rows = [[
        Paragraph(
            f'<font color="{GOLD_HEX}">{label}</font>',
            ParagraphStyle(
                f'r_hdr{i}',
                fontName=styles_cinzel(),
                fontSize=CAPTION - 2,
                alignment=TA_CENTER,
            ),
        )
        for i, (label, _) in enumerate(sens)
    ]]
    rows.append([
        Paragraph(
            value,
            ParagraphStyle(
                f'r_val{i}',
                fontName=styles_cormorant_italic(),
                fontSize=BODY,
                textColor=CREAM,
                alignment=TA_CENTER,
                leading=LEAD_BODY,
            ),
        )
        for i, (_, value) in enumerate(sens)
    ])
    tbl = Table(
        rows,
        colWidths=[3.8 * cm] * 4,
        hAlign='CENTER',
    )
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), SP_S),
        ('TOPPADDING', (0, 1), (-1, 1), SP_XS),
    ]))
    story.append(tbl)
    story.append(Spacer(1, SP_L))
    for i, step in enumerate(steps, 1):
        story.append(Paragraph(
            f'<font color="{GOLD_HEX}">{i}.</font>&nbsp;&nbsp;{step}',
            ParagraphStyle(
                f'r_st{i}',
                fontName=styles_cormorant(),
                fontSize=BODY,
                textColor=CREAM,
                alignment=TA_LEFT,
                leading=LEAD_BODY,
                leftIndent=1.5 * cm,
                rightIndent=1.5 * cm,
                spaceAfter=SP_S,
            ),
        ))
    story.append(PageBreak())


def t_journal(
    story,
    question: str,
    context_line: Optional[str] = None,
) -> None:
    """Question et espace d'écriture."""
    from reportlab.platypus import HRFlowable

    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ JOURNAL ✦</font>',
        ParagraphStyle(
            'j_tag',
            fontName=styles_cinzel(),
            fontSize=CAPTION,
            alignment=TA_CENTER,
            spaceAfter=SP_M,
        ),
    ))
    story.append(Paragraph(
        question,
        ParagraphStyle(
            'j_q',
            fontName=styles_cormorant_italic(),
            fontSize=SUBTITLE,
            textColor=CREAM,
            alignment=TA_CENTER,
            leading=LEAD_BODY,
            spaceAfter=SP_S,
            leftIndent=1.5 * cm,
            rightIndent=1.5 * cm,
        ),
    ))
    if context_line:
        story.append(Paragraph(
            context_line,
            ParagraphStyle(
                'j_ctx',
                fontName=styles_cormorant_italic(),
                fontSize=CAPTION,
                textColor=GREY_SUBTLE,
                alignment=TA_CENTER,
                spaceAfter=SP_L,
            ),
        ))
    else:
        story.append(Spacer(1, SP_L))

    for _ in range(10):
        story.append(HRFlowable(
            width='75%',
            thickness=0.5,
            color=HexColor('#332E22'),
            spaceBefore=SP_S + 4,
            spaceAfter=0,
            hAlign='CENTER',
        ))
    story.append(PageBreak())


def t_synthesis(
    story,
    title: str,
    forces: List[str],
    defis: List[str],
    mission: str,
    closing_quote: Optional[str] = None,
) -> None:
    """Forces, défis et mission."""
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ SYNTHÈSE ✦</font>',
        ParagraphStyle(
            's_tag',
            fontName=styles_cinzel(),
            fontSize=CAPTION,
            alignment=TA_CENTER,
            spaceAfter=SP_S,
        ),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle(
            's_title',
            fontName=styles_cormorant(),
            fontSize=H_PAGE,
            textColor=CREAM,
            alignment=TA_CENTER,
            leading=LEAD_PAGE,
            spaceAfter=SP_L,
        ),
    ))

    def _bulleted(
        items: List[str],
        header: str,
        color: str,
    ) -> Paragraph:
        content = (
            f'<font color="{color}"><b>{header}</b></font>'
            '<br/><br/>'
        )
        content += '<br/><br/>'.join(
            f'✦&nbsp;&nbsp;{item}' for item in items[:3]
        )
        return Paragraph(
            content,
            ParagraphStyle(
                f's_{header}',
                fontName=styles_cormorant(),
                fontSize=BODY,
                textColor=CREAM,
                alignment=TA_LEFT,
                leading=LEAD_BODY,
            ),
        )

    # Autorise la continuation des textes longs sur plusieurs pages.
    tbl = Table(
        [[
            _bulleted(forces, 'FORCES', GOLD_HEX),
            _bulleted(defis, 'DÉFIS', GREY_HEX),
        ]],
        colWidths=[8 * cm, 8 * cm],
        hAlign='CENTER',
        splitInRow=1,
    )
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, 0), SP_L),
    ]))
    story.append(tbl)
    story.append(Spacer(1, SP_XL))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">MISSION</font>',
        ParagraphStyle(
            's_mtag',
            fontName=styles_cinzel(),
            fontSize=CAPTION,
            alignment=TA_CENTER,
            spaceAfter=SP_XS,
        ),
    ))
    story.append(Paragraph(
        mission,
        ParagraphStyle(
            's_m',
            fontName=styles_cormorant_italic(),
            fontSize=CALLOUT,
            textColor=CREAM,
            alignment=TA_CENTER,
            leading=LEAD_CALLOUT,
            leftIndent=2 * cm,
            rightIndent=2 * cm,
        ),
    ))
    if closing_quote:
        story.append(Spacer(1, SP_L))
        story.append(Paragraph(
            f'« {closing_quote} »',
            ParagraphStyle(
                's_cq',
                fontName=styles_cormorant_italic(),
                fontSize=SUBTITLE,
                textColor=GOLD,
                alignment=TA_CENTER,
                leading=LEAD_BODY,
                leftIndent=1.5 * cm,
                rightIndent=1.5 * cm,
            ),
        ))
    story.append(PageBreak())


def t_double_illustration(
    story,
    illustration_path: str,
    caption: Optional[str] = None,
) -> None:
    """Page d'illustration."""
    story.append(Spacer(1, 2 * cm))
    if illustration_path and os.path.exists(illustration_path):
        try:
            story.append(RLImage(
                illustration_path,
                width=14 * cm,
                height=14 * cm,
                mask='auto',
            ))
        except Exception:
            pass
    if caption:
        story.append(Spacer(1, SP_L))
        story.append(Paragraph(
            caption,
            ParagraphStyle(
                'di_cap',
                fontName=styles_cormorant_italic(),
                fontSize=SUBTITLE,
                textColor=GOLD,
                alignment=TA_CENTER,
                leading=LEAD_BODY,
                leftIndent=2 * cm,
                rightIndent=2 * cm,
            ),
        ))
    story.append(PageBreak())
