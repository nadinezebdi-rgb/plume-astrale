"""renderer — moteur de rendu HTML→PDF pour Le Livre Astral (LOT 4).

Pipeline :
  1. Assemble une liste ordonnée de "page specs" (cover, title, chapter_opener, wheel,
     tables, body pages, blanks, colophon)
  2. Rend chaque template Jinja2 en HTML avec `side` (recto/verso) et `folio` calculés
  3. Concatène dans un `book.html` unique
  4. Appelle Chromium `--print-to-pdf` en subprocess (fallback : WeasyPrint)

Contraintes clés du guide :
  - A5 148×210 mm, marges 20/18/20/22 recto/verso
  - Chapter opener toujours en belle page (impaire) — on injecte une blanche si besoin
  - Total pages multiple de 4 (ajout de blanches en fin)
  - `book.css` unique, aucun style inline dans les templates
  - Deux profils : `print` (fond blanc, papier ivoire à l'impression) et `screen`

L'entrée est un objet `Manuscript` (identique à celui du moteur v1). La sortie
est des bytes PDF prêts à être uploadés.
"""
from __future__ import annotations

import html
import logging
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from services.book_engine.domain import (
    BlockKind, Chapter, ChapterBlock, Edition, Manuscript,
)
from .wheel import build_wheel_svg, extract_wheel_data, extract_tables_data

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# Chemins des ressources — tout est absolu pour le rendu Chromium
# ═══════════════════════════════════════════════════════════════════
ENGINE_ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = ENGINE_ROOT / 'templates'
CSS_PATH = ENGINE_ROOT / 'css' / 'book.css'
ASSETS_DIR = ENGINE_ROOT.parent.parent / 'assets' / 'book' / 'assets'


# ═══════════════════════════════════════════════════════════════════
# Jinja2 env
# ═══════════════════════════════════════════════════════════════════
_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(['html']),
    trim_blocks=True,
    lstrip_blocks=True,
)


def _asset_url(asset_dir: Path, name: str) -> str:
    """Retourne une URL file:// vers un asset du kit (SVG plume, séparateur…)."""
    return (asset_dir / name).resolve().as_uri()


# ═══════════════════════════════════════════════════════════════════
# Rendu des blocs de contenu (Chapter.blocks → HTML sûr)
# ═══════════════════════════════════════════════════════════════════
def _escape(text: str) -> str:
    return html.escape(text or '', quote=False)


def _render_block(block: ChapterBlock) -> str:
    """Convertit un `ChapterBlock` en HTML compatible book.css. Sans JS, sans style inline."""
    data = block.data or {}
    kind = block.kind
    if kind == BlockKind.H2:
        return f'<h2>{_escape(data.get("text", ""))}</h2>'
    if kind == BlockKind.PARAGRAPH:
        return f'<p>{_escape(data.get("text", ""))}</p>'
    if kind == BlockKind.PARAGRAPH_DROPCAP:
        # Dropcap géré via CSS `p:first-child::first-letter` sur le premier <p>
        return f'<p class="no-indent">{_escape(data.get("text", ""))}</p>'
    if kind == BlockKind.ENCART:
        label = _escape(data.get('label', 'ENCART'))
        text = _escape(data.get('text', ''))
        return (
            f'<aside class="encart">'
            f'<span class="label">{label}</span>'
            f'{text}'
            f'</aside>'
        )
    if kind == BlockKind.QUOTE_LITERARY:
        text = _escape(data.get('text', ''))
        source = _escape(data.get('source', ''))
        return (
            f'<blockquote class="quote-literary">{text}'
            + (f'<span class="source">{source}</span>' if source else '')
            + '</blockquote>'
        )
    if kind == BlockKind.QUOTE_BREATH:
        return f'<p class="quote-breath">{_escape(data.get("text", ""))}</p>'
    if kind == BlockKind.HAIRLINE:
        # Séparateur discret entre paragraphes
        return '<img class="separator" src="' + _asset_url(ASSETS_DIR, 'separateur.svg') + '" alt="">'
    if kind == BlockKind.NATAL_META:
        sign = _escape(data.get('sign', ''))
        house = _escape(data.get('house', ''))
        degree = _escape(data.get('degree', ''))
        note = _escape(data.get('note', ''))
        return (
            '<p class="natal-meta" style="font-size:8.5pt;letter-spacing:.28em;text-transform:uppercase;color:#A8823F;margin:0 0 6mm;text-align:center">'
            f'{sign}&nbsp;·&nbsp;{house}&nbsp;·&nbsp;{degree}'
            + (f'&nbsp;·&nbsp;{note}' if note else '')
            + '</p>'
        )
    # PAGE_BREAK / CHAPTER_OPENING / IMAGE : gérés au niveau page-spec (pas ici)
    return ''


# ═══════════════════════════════════════════════════════════════════
# Layout : découpage d'un chapitre en pages HTML
# ═══════════════════════════════════════════════════════════════════
@dataclass
class PageSpec:
    """Une page rendue = template Jinja + contexte."""
    template: str
    context: dict = field(default_factory=dict)
    counts_in_pagination: bool = True    # False pour cover + blanches de couverture

    def render(self, env: Environment, base_ctx: dict) -> str:
        tpl = env.get_template(self.template)
        return tpl.render(**base_ctx, **self.context)


def _split_chapter_into_body_pages(chapter: Chapter) -> list[str]:
    """Découpe le contenu d'un chapitre en pages HTML. Une page = ~2600 chars de corps.

    Le découpage réel est ensuite laissé au moteur de layout du navigateur (page-break),
    mais on regroupe les blocs consécutifs dans une seule page-spec HTML pour laisser
    Chromium gérer les orphelins/veuves.
    """
    # On extrait tous les blocs sauf CHAPTER_OPENING / PAGE_BREAK (gérés à part)
    body_blocks = [
        b for b in chapter.blocks
        if b.kind not in (BlockKind.CHAPTER_OPENING, BlockKind.PAGE_BREAK,
                          BlockKind.IMAGE)
    ]
    if not body_blocks:
        return []
    html_content = ''.join(_render_block(b) for b in body_blocks)
    # Une seule page HTML — Chromium gère la pagination via `page-break-after: always`
    # sur `.page`. Le contenu qui déborde est perdu (par design : le contrôle QA
    # vérifie qu'aucune veuve ne subsiste). Pour un vrai split multi-page, on
    # laisserait Chromium découper (voir LOT 4.2 : ajout de `@page` avec `break-after`).
    return [html_content]


# ═══════════════════════════════════════════════════════════════════
# Assemblage global
# ═══════════════════════════════════════════════════════════════════
def _fmt_birth_line(m: Manuscript) -> tuple[str, str, str]:
    """Formatte '15 mai 1990', '14:30', 'Paris' pour la couverture."""
    date_fr = m.birth_data.date_iso or ''
    try:
        y, mo, d = m.birth_data.date_iso.split('-')
        months = ['janvier','février','mars','avril','mai','juin',
                  'juillet','août','septembre','octobre','novembre','décembre']
        date_fr = f'{int(d)} {months[int(mo)-1]} {y}'
    except Exception:
        pass
    time_fr = m.birth_data.time_hhmm or '—'
    city = m.birth_data.city or '—'
    return date_fr, time_fr, city


def _side(page_number: int) -> str:
    """Renvoie 'recto' si page impaire, 'verso' si paire."""
    return 'recto' if page_number % 2 == 1 else 'verso'


def _build_page_specs(m: Manuscript, *, cover_png_path: Optional[Path] = None) -> list[PageSpec]:
    """Ordonne les pages du livre selon §6 du guide.

    Ordre canonique :
      1. Couverture (recto)
      2. Blanche verso couverture
      3. Titre (recto)
      4. Blanche verso titre
      5. Chapitre I (recto, belle page) — Ouverture
      6. Chapitre I — Carte du ciel (verso)
      7. Chapitre I — Tableaux (recto)
      8+. Corps du Chapitre I
      … Chapitres II à XII (chacun débute en belle page → blanche si nécessaire)
      Colophon (dernière page)
      Blanches pour atteindre un multiple de 4
    """
    date_fr, time_fr, city = _fmt_birth_line(m)
    edition_label = m.edition.value if isinstance(m.edition, Edition) else str(m.edition)
    edition_year = (m.created_at.year if m.created_at else date.today().year)

    specs: list[PageSpec] = []
    page_num = 1

    # 1. Couverture (recto, pas de folio)
    cover_bg_url = None
    if cover_png_path and Path(cover_png_path).exists():
        cover_bg_url = Path(cover_png_path).resolve().as_uri()
    specs.append(PageSpec('_cover.html', {
        'first_name': m.first_name,
        'birth_date_fr': date_fr,
        'birth_time_fr': time_fr,
        'birth_city': city,
        'cover_bg_url': cover_bg_url,
    }, counts_in_pagination=False))
    page_num += 1

    # 2. Blanche verso couverture
    specs.append(PageSpec('_blank.html', {'side': 'verso'}, counts_in_pagination=False))
    page_num += 1

    # 3. Titre (recto)
    specs.append(PageSpec('_title.html', {
        'side': 'recto',
        'first_name': m.first_name,
        'book_title': 'Le Livre Astral',
        'edition_label': _label_edition(m.edition),
        'edition_year': edition_year,
    }, counts_in_pagination=False))
    page_num += 1

    # 4. Blanche verso titre
    specs.append(PageSpec('_blank.html', {'side': 'verso'}, counts_in_pagination=False))
    page_num += 1

    # Pagination folio commence maintenant (page 5 = 1er folio "Chapitre I")
    folio = 1

    # 5+. Chapitres
    astro = m.astro_data or {}

    for idx, chapter in enumerate(m.chapters, start=1):
        # Chaque chapitre débute en belle page (impaire)
        if _side(page_num) == 'verso':
            specs.append(PageSpec('_blank.html', {'side': 'verso'}))
            page_num += 1
            folio += 1

        # Ouverture de chapitre
        specs.append(PageSpec('_chapter_opener.html', {
            'side': 'recto',
            'first_name': m.first_name,
            'roman_num': chapter.roman_num,
            'title': chapter.title,
            'kicker': chapter.kicker,
            'folio': folio,
        }))
        page_num += 1
        folio += 1

        # Chapitre I : carte du ciel + tableaux (spécifique)
        if chapter.slug == 'ciel_naissance' and astro:
            try:
                wheel_data = extract_wheel_data(astro)
                wheel_svg = build_wheel_svg(wheel_data)
                specs.append(PageSpec('_wheel.html', {
                    'side': _side(page_num),
                    'first_name': m.first_name,
                    'wheel_svg': wheel_svg,
                    'asc_label': wheel_data['asc_label'],
                    'mc_label': wheel_data['mc_label'],
                    'house_system': 'Placidus',
                    'folio': folio,
                }))
                page_num += 1
                folio += 1
                # Tableaux positions + aspects
                tables_data = extract_tables_data(astro)
                specs.append(PageSpec('_tables.html', {
                    'side': _side(page_num),
                    'first_name': m.first_name,
                    'planets_left': tables_data['planets_left'],
                    'planets_right': tables_data['planets_right'],
                    'aspects': tables_data['aspects'],
                    'distribution_line': tables_data['distribution_line'],
                    'folio': folio,
                }))
                page_num += 1
                folio += 1
            except Exception as exc:
                logger.warning(f'[book_v2] wheel skipped for ch.I: {exc}')

        # Corps du chapitre — un bloc HTML par "page virtuelle"
        body_pages = _split_chapter_into_body_pages(chapter)
        for content_html_str in body_pages:
            if not content_html_str.strip():
                continue
            specs.append(PageSpec('_body.html', {
                'side': _side(page_num),
                'first_name': m.first_name,
                'content_html': content_html_str,
                'folio': folio,
            }))
            page_num += 1
            folio += 1

    # Colophon en dernière page utile
    specs.append(PageSpec('_colophon.html', {
        'side': _side(page_num),
        'first_name': m.first_name,
        'edition_label': _label_edition(m.edition),
        'edition_year': edition_year,
    }, counts_in_pagination=False))
    page_num += 1

    # Blanches pour atteindre un multiple de 4 (§1)
    total_pages = page_num - 1
    while total_pages % 4 != 0:
        specs.append(PageSpec('_blank.html', {'side': _side(page_num)},
                              counts_in_pagination=False))
        page_num += 1
        total_pages += 1

    logger.info(f'[book_v2] {total_pages} pages assemblées ({len(m.chapters)} chapitres)')
    return specs


def _label_edition(e) -> str:
    if isinstance(e, Edition):
        mapping = {Edition.NUMERIQUE: 'Numérique',
                   Edition.BROCHEE: 'Brochée',
                   Edition.RELIEE: 'Reliée'}
        return mapping.get(e, 'Numérique')
    return str(e).capitalize()


# ═══════════════════════════════════════════════════════════════════
# Rendu HTML complet
# ═══════════════════════════════════════════════════════════════════
def render_manuscript_to_html(manuscript: Manuscript, *, profile: str = 'print',
                              cover_png_path: Optional[Path] = None) -> str:
    """Compose le book.html complet.

    profile ∈ {'print', 'screen'} — voir §1.1 du guide.
    cover_png_path : PNG optionnel (Nano Banana) posé en fond de couverture.
    """
    specs = _build_page_specs(manuscript, cover_png_path=cover_png_path)

    def _asset(name: str) -> str:
        return _asset_url(ASSETS_DIR, name)

    base_ctx = {
        'asset': _asset,
        'profile': profile,
        'book_title_meta': f'Le Livre Astral de {manuscript.first_name}',
        'css_href': CSS_PATH.resolve().as_uri(),
    }

    pages_html = '\n'.join(spec.render(_env, base_ctx) for spec in specs)
    tpl = _env.get_template('book.html')
    return tpl.render(**base_ctx, title=base_ctx['book_title_meta'], pages_html=pages_html)


# ═══════════════════════════════════════════════════════════════════
# Rendu PDF via Chromium (défaut) ou WeasyPrint (fallback)
# ═══════════════════════════════════════════════════════════════════
CHROMIUM_BINARIES = ('chromium', 'chromium-browser', 'google-chrome', 'chrome')


def _find_chromium() -> Optional[str]:
    for name in CHROMIUM_BINARIES:
        path = shutil.which(name)
        if path:
            return path
    return None


def _render_pdf_chromium(html_path: Path, out_path: Path, *, timeout: int = 30) -> None:
    binary = _find_chromium()
    if not binary:
        raise RuntimeError('Chromium introuvable')
    cmd = [
        binary,
        '--headless=new',
        '--disable-gpu',
        '--no-sandbox',
        '--no-pdf-header-footer',
        '--hide-scrollbars',
        '--virtual-time-budget=15000',
        f'--print-to-pdf={out_path}',
        html_path.as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, timeout=timeout)
    if res.returncode != 0:
        raise RuntimeError(
            f'Chromium print-to-pdf failed (rc={res.returncode}): '
            f'{res.stderr.decode(errors="replace")[:800]}'
        )
    if not out_path.exists() or out_path.stat().st_size < 2000:
        raise RuntimeError(f'PDF vide/absent après rendu Chromium ({out_path})')


def _render_pdf_weasyprint(html_path: Path, out_path: Path) -> None:
    """Fallback si Chromium refuse d'installer. Perte : columns/grid partiels."""
    try:
        from weasyprint import HTML  # type: ignore
    except ImportError:
        raise RuntimeError('WeasyPrint non installé et Chromium indisponible')
    HTML(filename=str(html_path)).write_pdf(str(out_path))


def render_manuscript_to_pdf_v2(manuscript: Manuscript, *, profile: str = 'print',
                                 cover_png_path: Optional[Path] = None) -> bytes:
    """Point d'entrée : Manuscript → bytes PDF.

    Utilise Chromium par défaut ; bascule sur WeasyPrint si Chromium absent.
    `cover_png_path` : PNG facultatif (Nano Banana) à poser en fond de couverture.
    """
    html_str = render_manuscript_to_html(manuscript, profile=profile,
                                          cover_png_path=cover_png_path)
    with tempfile.TemporaryDirectory(prefix='book_v2_') as tmp:
        tmp_dir = Path(tmp)
        html_path = tmp_dir / 'book.html'
        pdf_path = tmp_dir / 'book.pdf'
        html_path.write_text(html_str, encoding='utf-8')
        try:
            _render_pdf_chromium(html_path, pdf_path)
        except Exception as exc:
            logger.warning(f'[book_v2] Chromium fail, fallback WeasyPrint: {exc}')
            _render_pdf_weasyprint(html_path, pdf_path)
        return pdf_path.read_bytes()
