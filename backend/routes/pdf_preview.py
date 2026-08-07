"""
routes/pdf_preview.py — endpoint public pour télécharger un aperçu 3 pages
d'un rapport premium Plume Astrale. Permet aux visiteurs anonymes de rassurer
avant achat (surtout pour la campagne Noël livres imprimés).

Route publique :
  GET /api/pdf-preview/{product}
    → Renvoie un PDF de 3 pages (couverture + sommaire + chapter opener)
      généré à la volée avec un prénom générique "Marie".

Produits supportés : astrocartographie, kabbale, karma-destin, numerologie,
theme-natal, synastrie.

Cache : le PDF est mis en cache mémoire par produit (les 3 pages sont
identiques d'une requête à l'autre → pas besoin de régénérer).
"""
from __future__ import annotations
from io import BytesIO
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
import logging

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors as _c

from services.pdf_bg import make_bg_canvas
from services.pdf_prestige import toc_page, chapter_opener, ornament

router = APIRouter(prefix="/pdf-preview", tags=["pdf-preview"])
logger = logging.getLogger(__name__)

# Cache mémoire (le contenu ne dépend d'aucun paramètre utilisateur)
_CACHE: dict[str, bytes] = {}

GOLD = _c.HexColor('#D4AF37')
CREAM = _c.HexColor('#F5EEE0')
MUTED = _c.HexColor('#9089B5')

# ─── Configuration par produit ────────────────────────────────
PRODUCTS = {
    'astrocartographie': {
        'title': "ASTROCARTOGRAPHIE",
        'subtitle': "Où vivre ta meilleure vie",
        'hero_png': '/app/backend/assets/pdf_covers/astrocarto_hero.png',
        'chapters': [
            {'roman': 'I',   'title': "L'astrocartographie"},
            {'roman': 'II',  'title': "Ta carte du monde"},
            {'roman': 'III', 'title': "Tes lignes planétaires"},
            {'roman': 'IV',  'title': "Tes trois villes choisies"},
            {'roman': 'V',   'title': "Les destinations de Soléna"},
            {'roman': 'VI',  'title': "Synthèse"},
            {'roman': 'VII', 'title': "Rituel d'ancrage"},
        ],
        'chapter1_body': "L'astrocartographie est une science ancienne. Chaque planète de ton thème natal projette 4 lignes sur la Terre. Vivre à moins de 800 km d'une ligne active profondément l'énergie de la planète concernée. Ce document explore trois villes que tu as choisies et deux destinations bonus, sélectionnées par Soléna selon la géographie unique de ton ciel.",
        'footer_label': "Astrocartographie",
    },
    'kabbale': {
        'title': "TON ARBRE DE VIE",
        'subtitle': "Kabbalistique",
        'hero_png': '/app/backend/assets/pdf_covers/kabbale_hero.png',
        'chapters': [
            {'roman': 'I',   'title': "L'Arbre de Vie kabbalistique"},
            {'roman': 'II',  'title': "Tes trois piliers"},
            {'roman': 'III', 'title': "Les 10 Sephiroth"},
            {'roman': 'IV',  'title': "Les 22 chemins"},
            {'roman': 'V',   'title': "Da'at, la sphère invisible"},
            {'roman': 'VI',  'title': "Synthèse"},
            {'roman': 'VII', 'title': "Rituels de communion"},
        ],
        'chapter1_body': "L'Arbre de Vie kabbalistique est une carte spirituelle vieille de deux mille ans. Il décrit dix sphères de conscience — les Sephiroth — reliées par vingt-deux chemins, qui représentent la descente de la Lumière divine dans le monde manifeste. Chaque Sephirah incarne une qualité d'être : de Kether, la couronne suprême, jusqu'à Malkuth, le royaume incarné.",
        'footer_label': "Ton Arbre de Vie",
    },
    'karma-destin': {
        'title': "TON ANALYSE KARMIQUE",
        'subtitle': "Destinée, Leçons & Guérison Spirituelle",
        'hero_png': '/app/backend/assets/pdf_covers/karma_hero.png',
        'chapters': [
            {'roman': 'I',   'title': "Comprendre ton karma"},
            {'roman': 'II',  'title': "Tes nœuds lunaires"},
            {'roman': 'III', 'title': "Saturne — les leçons"},
            {'roman': 'IV',  'title': "Chiron — la blessure sacrée"},
            {'roman': 'V',   'title': "Pluton — la transformation"},
            {'roman': 'VI',  'title': "Karma générationnel"},
            {'roman': 'VII', 'title': "Rituels de libération"},
        ],
        'chapter1_body': "Le karma n'est pas une punition — c'est un enseignement. Chaque incarnation te rapproche de ta sagesse cosmique. Cette analyse révèle tes nœuds lunaires (ton chemin d'évolution), ton Saturne (tes leçons de vie), ton Chiron (ta blessure d'âme), ton Pluton (ta transformation profonde) et ton karma générationnel — l'héritage que tu portes.",
        'footer_label': "Ton Analyse Karmique",
    },
    'numerologie': {
        'title': "TON CODE NUMÉROLOGIQUE",
        'subtitle': "Destinée, Cycles & Vibrations",
        'hero_png': '/app/backend/assets/pdf_covers/numerologie_hero.png',
        'chapters': [
            {'roman': 'I',   'title': "La numérologie sacrée"},
            {'roman': 'II',  'title': "Tes nombres-clés"},
            {'roman': 'III', 'title': "Ton année personnelle"},
            {'roman': 'IV',  'title': "Prévisions cycliques"},
            {'roman': 'V',   'title': "Ton Carré Lo-Shu"},
            {'roman': 'VI',  'title': "Rituels de vibration"},
        ],
        'chapter1_body': "La numérologie est un langage sacré. Chaque nombre porte une vibration, une énergie, une leçon. En additionnant les chiffres de ta date de naissance, on obtient ton Chemin de Vie — le fil rouge de ton incarnation. Ton nom révèle ton Expression, ton Nombre d'Âme, et ta Personnalité. Ce document décode l'ensemble de ta carte numérologique.",
        'footer_label': "Ton Analyse Numérologique",
    },
    'theme-natal': {
        'title': "TON THÈME NATAL",
        'subtitle': "Ton ciel de naissance, dévoilé",
        'hero_png': '/app/backend/assets/pdf_covers/natal_hero.png',
        'chapters': [
            {'roman': 'I',   'title': "Ton empreinte céleste"},
            {'roman': 'II',  'title': "Tes planètes intimes"},
            {'roman': 'III', 'title': "Tes planètes générationnelles"},
            {'roman': 'IV',  'title': "La danse des aspects"},
            {'roman': 'V',   'title': "Les douze maisons"},
            {'roman': 'VI',  'title': "Épilogue"},
        ],
        'chapter1_body': "Ton thème natal est la photographie exacte du ciel au moment de ta naissance. Il révèle qui tu es en profondeur — ton Soleil (ton identité), ta Lune (ton monde émotionnel), ton Ascendant (le masque que tu portes), et l'ensemble de tes planètes réparties dans les signes et les maisons. C'est ta carte d'identité cosmique.",
        'footer_label': "Ton Thème Natal",
    },
    'synastrie': {
        'title': "VOTRE SYNASTRIE",
        'subtitle': "L'astrologie de votre lien",
        'hero_png': '/app/backend/assets/pdf_covers/synastrie_hero.png',
        'chapters': [
            {'roman': 'I',   'title': "L'art de la rencontre"},
            {'roman': 'II',  'title': "Vos deux ciels"},
            {'roman': 'III', 'title': "Vos aspects majeurs"},
            {'roman': 'IV',  'title': "Vos maisons entrelacées"},
            {'roman': 'V',   'title': "Votre carte de compatibilité"},
            {'roman': 'VI',  'title': "Votre invitation"},
        ],
        'chapter1_body': "La synastrie est l'art de superposer deux thèmes natals pour révéler ce qui se joue entre deux êtres. Chaque planète de votre ciel entre en dialogue avec chaque planète de son ciel — vos Vénus qui s'attirent ou se froissent, vos Lunes qui se rassurent ou se heurtent, vos Mars qui s'électrisent. Ce document décrit chacun de ces dialogues.",
        'footer_label': "Synastrie",
    },
}


def _build_preview_pdf(product_key: str) -> bytes:
    """Construit un PDF de 3 pages : couverture + sommaire + premier chapter opener + intro."""
    cfg = PRODUCTS[product_key]
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=f"Aperçu — {cfg['title']}",
        author="Plume Astrale",
    )

    # Styles cohérents avec les autres PDF
    title_style = ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=22,
                                  textColor=GOLD, alignment=TA_CENTER, leading=28,
                                  spaceAfter=10)
    subtitle_style = ParagraphStyle('subtitle', fontName='Helvetica-Oblique', fontSize=13,
                                     textColor=CREAM, alignment=TA_CENTER, leading=16,
                                     spaceAfter=6)
    body_style = ParagraphStyle('body', fontName='Helvetica', fontSize=11,
                                 textColor=CREAM, alignment=TA_CENTER, leading=17)
    caption_style = ParagraphStyle('caption', fontName='Helvetica', fontSize=9,
                                    textColor=GOLD, alignment=TA_CENTER,
                                    leading=12, letterSpacing=2)
    h2_style = ParagraphStyle('h2', fontName='Helvetica-Oblique', fontSize=15,
                               textColor=CREAM, alignment=TA_CENTER, leading=20)

    mini_styles = {
        'caption': caption_style,
        'title': title_style,
        'subtitle': subtitle_style,
        'body': body_style,
        'h2': h2_style,
    }

    story = []

    # ═══ PAGE 1 : Couverture illustrée ═══
    from pathlib import Path as _P
    from reportlab.platypus import Image as _RLImage
    story.append(Spacer(0, 1.5 * cm))
    hero_path = _P(cfg['hero_png'])
    if hero_path.exists():
        try:
            img = _RLImage(str(hero_path), width=8 * cm, height=8 * cm, kind='proportional')
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(0, 0.5 * cm))
        except Exception:
            pass
    story.append(Paragraph(f'✦ {cfg["title"]} ✦', title_style))
    story.append(Spacer(0, 0.3 * cm))
    story.append(Paragraph(cfg['subtitle'], subtitle_style))
    story.append(Spacer(0, 1.5 * cm))
    watermark = ParagraphStyle(
        'watermark', fontName='Helvetica-Bold', fontSize=10,
        textColor=GOLD, alignment=TA_CENTER, leading=14, letterSpacing=3,
    )
    story.append(Paragraph('★  APERÇU LIVRE PRESTIGE — 3 PAGES  ★', watermark))
    story.append(Spacer(0, 0.4 * cm))
    story.append(Paragraph(
        "Ceci est un aperçu offert par Plume Astrale.<br/>"
        "Le livre complet fait plus de 30 pages personnalisées.",
        ParagraphStyle('teaser', fontName='Helvetica-Oblique', fontSize=10,
                        textColor=MUTED, alignment=TA_CENTER, leading=14),
    ))
    story.append(PageBreak())

    # ═══ PAGE 2 : Sommaire ═══
    toc_page(story, mini_styles, cfg['chapters'])

    # ═══ PAGE 3 : Chapter opener I + un extrait du texte d'intro ═══
    chapter_opener(story, mini_styles, cfg['chapters'][0]['roman'],
                    cfg['chapters'][0]['title'], "Aperçu — Plume Astrale")
    story.append(Spacer(0, 0.5 * cm))
    story.append(Paragraph(cfg['chapter1_body'], body_style))
    story.append(Spacer(0, 0.8 * cm))
    ornament(story, 'diamond')
    story.append(Spacer(0, 0.4 * cm))
    story.append(Paragraph(
        f'<font color="#D4AF37">Le livre complet contient {len(cfg["chapters"])} chapitres.</font><br/>'
        "Achète le rapport complet sur <b>plume-astrale.fr</b>",
        ParagraphStyle('cta_teaser', fontName='Helvetica-Oblique', fontSize=10,
                        textColor=CREAM, alignment=TA_CENTER, leading=15),
    ))

    doc.build(story,
              onFirstPage=make_bg_canvas(cfg['footer_label']),
              onLaterPages=make_bg_canvas(cfg['footer_label']))
    buffer.seek(0)
    return buffer.getvalue()


@router.get("/{product}")
async def get_pdf_preview(product: str, download: bool = Query(False)):
    """Retourne un aperçu 3 pages du produit demandé.

    Args:
        product: astrocartographie | kabbale | karma-destin | numerologie
                 | theme-natal | synastrie
        download: si True, force le téléchargement (Content-Disposition attachment)

    Returns:
        Un fichier PDF binaire.
    """
    key = product.lower().strip()
    if key not in PRODUCTS:
        raise HTTPException(status_code=404, detail=f"Produit '{product}' inconnu")

    # Cache : régénérer uniquement si absent
    if key not in _CACHE:
        try:
            _CACHE[key] = _build_preview_pdf(key)
        except Exception as e:
            logger.exception(f"[pdf_preview] gen failed for {key}")
            raise HTTPException(status_code=500, detail=f"Génération PDF impossible: {e}")

    disposition = (
        f'attachment; filename="apercu-{key}-plume-astrale.pdf"'
        if download else
        f'inline; filename="apercu-{key}.pdf"'
    )
    return Response(
        content=_CACHE[key],
        media_type='application/pdf',
        headers={
            'Content-Disposition': disposition,
            'Cache-Control': 'public, max-age=3600',
        },
    )



# Cache mémoire pour les pages rendues en JPEG (une seule fois par produit)
_PAGE_CACHE: dict[str, list[bytes]] = {}


def _render_pages_as_jpeg(product_key: str) -> list[bytes]:
    """Rasterise chaque page du PDF preview en JPEG haute qualité.

    Utilise pdf2image (poppler) — nécessite `pdftoppm` installé.
    Résultat mis en cache par produit.
    """
    if product_key in _PAGE_CACHE:
        return _PAGE_CACHE[product_key]

    if product_key not in _CACHE:
        _CACHE[product_key] = _build_preview_pdf(product_key)

    from pdf2image import convert_from_bytes
    # 150 DPI → bon compromis qualité / poids (~120 KB par page A4)
    images = convert_from_bytes(_CACHE[product_key], dpi=150, fmt='jpeg')
    pages: list[bytes] = []
    for img in images:
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=82, optimize=True)
        pages.append(buf.getvalue())
    _PAGE_CACHE[product_key] = pages
    return pages


@router.get("/{product}/page/{page_index}.jpg")
async def get_pdf_preview_page(product: str, page_index: int):
    """Retourne une page individuelle du PDF preview rendue en JPEG.

    Utilisé par le composant Flipbook front-end pour afficher un feuilletage
    interactif sur /livres. Page 0-indexée. Cache long (immutable côté client).
    """
    key = product.lower().strip()
    if key not in PRODUCTS:
        raise HTTPException(status_code=404, detail=f"Produit '{product}' inconnu")
    if page_index < 0 or page_index > 10:
        raise HTTPException(status_code=400, detail="page_index hors bornes")

    try:
        pages = _render_pages_as_jpeg(key)
    except Exception as e:
        logger.exception(f"[pdf_preview] page render failed for {key}")
        raise HTTPException(status_code=500, detail=f"Rendu image impossible: {e}")

    if page_index >= len(pages):
        raise HTTPException(status_code=404, detail=f"Page {page_index} indisponible")

    return Response(
        content=pages[page_index],
        media_type='image/jpeg',
        headers={
            'Content-Disposition': f'inline; filename="apercu-{key}-p{page_index}.jpg"',
            'Cache-Control': 'public, max-age=86400, immutable',
        },
    )


@router.get("/{product}/pages/meta")
async def get_pdf_preview_meta(product: str):
    """Retourne la liste des indices de page disponibles pour le flipbook."""
    key = product.lower().strip()
    if key not in PRODUCTS:
        raise HTTPException(status_code=404, detail=f"Produit '{product}' inconnu")
    try:
        pages = _render_pages_as_jpeg(key)
    except Exception as e:
        logger.exception(f"[pdf_preview] meta failed for {key}")
        raise HTTPException(status_code=500, detail=f"Meta impossible: {e}")
    return {'product': key, 'total_pages': len(pages)}
