"""Tests pour services/book_engine/ — dataclasses + document.

Verrouille :
  - Sérialisation Manuscript ↔ dict (round-trip)
  - Rendu d'un chapitre pilote en PDF valide (≥ 2 pages, ≥ 1 Ko)
  - Embed des polices (Cormorant, Cinzel, Allura) dans le PDF final
"""
from __future__ import annotations
import io
import pytest
from services.book_engine import (
    Manuscript, Chapter, ChapterBlock, BlockKind,
    BirthData, Edition,
)
from services.book_engine.document import render_manuscript_to_pdf


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════
@pytest.fixture
def sample_birth() -> BirthData:
    return BirthData(
        date_iso='1990-05-15', time_hhmm='06:42',
        city='Marseille', country_code='FR',
        latitude=43.2965, longitude=5.3698,
    )


@pytest.fixture
def sample_chapter() -> Chapter:
    """Chapitre pilote : Chapitre IV — Votre façon d'aimer.

    Structure minimale mais représentative :
      - CHAPTER_OPENING (page droite, plume, tag, titre, kicker manuscrit)
      - PAGE_BREAK
      - H2 + PARAGRAPH_DROPCAP + PARAGRAPH x2  (page suivante)
    """
    return Chapter(
        slug='ta_facon_aimer',
        title="Votre façon d'aimer",
        kicker='Ce que Vénus murmure de vous…',
        roman_num='IV',
        order=4,
        blocks=[
            ChapterBlock(BlockKind.CHAPTER_OPENING, {
                'title': "Votre façon d'aimer",
                'kicker': 'Ce que Vénus murmure de vous…',
                'roman_num': 'IV',
            }),
            ChapterBlock(BlockKind.PAGE_BREAK, {}),
            ChapterBlock(BlockKind.H2, {'text': 'Le langage secret de votre Vénus'}),
            ChapterBlock(BlockKind.PARAGRAPH_DROPCAP, {
                'text': (
                    "Vous n'aimez pas comme la plupart des gens de votre âge. Là où beaucoup "
                    "cherchent la certitude, vous êtes attirée par ce qui vibre — par ce qui "
                    "pourrait ne pas rester. Votre Vénus est en Poissons, rétrograde (11° 08′), "
                    "et c'est cette particularité — que seuls quelques thèmes de votre "
                    "génération portent — qui donne à votre rapport amoureux son grain "
                    "si singulier."
                ),
            }),
            ChapterBlock(BlockKind.PARAGRAPH, {
                'text': (
                    "Rétrograde ne veut pas dire défaillante. Cela signifie que Vénus, chez "
                    "vous, a appris à faire un pas en arrière avant de tendre la main. Vous "
                    "rencontrez quelqu'un, et il y a un temps de silence intérieur — quelques "
                    "semaines, parfois plus — avant que quelque chose s'ouvre."
                ),
            }),
        ],
    )


@pytest.fixture
def sample_manuscript(sample_birth, sample_chapter) -> Manuscript:
    return Manuscript(
        session_id='cs_test_pilot',
        user_email='alexandra@example.com',
        first_name='Alexandra',
        birth_data=sample_birth,
        edition=Edition.NUMERIQUE,
        chapters=[sample_chapter],
    )


# ═══════════════════════════════════════════════════════════════
# Sérialisation dataclasses
# ═══════════════════════════════════════════════════════════════
def test_birth_data_no_birth_time_flag():
    with_time = BirthData(date_iso='1990-05-15', time_hhmm='06:42', city='Marseille')
    without_time = BirthData(date_iso='1990-05-15', time_hhmm=None, city='Marseille')
    assert with_time.no_birth_time is False
    assert without_time.no_birth_time is True
    # Placeholder 12:00 (heure inconnue par convention) → considéré comme absent
    assert BirthData(date_iso='x', time_hhmm='12:00', city='x').no_birth_time is True


def test_chapter_roundtrip(sample_chapter):
    d = sample_chapter.to_dict()
    c2 = Chapter.from_dict(d)
    assert c2.slug == sample_chapter.slug
    assert c2.title == sample_chapter.title
    assert c2.kicker == sample_chapter.kicker
    assert c2.roman_num == sample_chapter.roman_num
    assert len(c2.blocks) == len(sample_chapter.blocks)
    assert c2.blocks[0].kind == BlockKind.CHAPTER_OPENING
    assert c2.blocks[3].kind == BlockKind.PARAGRAPH_DROPCAP


def test_manuscript_roundtrip(sample_manuscript):
    d = sample_manuscript.to_dict()
    m2 = Manuscript.from_dict(d)
    assert m2.first_name == 'Alexandra'
    assert m2.user_email == 'alexandra@example.com'
    assert m2.edition == Edition.NUMERIQUE
    assert m2.birth_data.no_birth_time is False
    assert m2.chapters[0].slug == 'ta_facon_aimer'


# ═══════════════════════════════════════════════════════════════
# Rendu PDF
# ═══════════════════════════════════════════════════════════════
def test_render_pilot_chapter_produces_valid_pdf(sample_manuscript):
    pdf_bytes = render_manuscript_to_pdf(sample_manuscript)
    assert pdf_bytes.startswith(b'%PDF-')
    assert len(pdf_bytes) > 5000  # > 5 Ko (chapitre pilote 2 pages minimum)


def test_render_embeds_allura_font(sample_manuscript):
    """La police manuscrite doit être embarquée dans le PDF final."""
    from pypdf import PdfReader
    pdf_bytes = render_manuscript_to_pdf(sample_manuscript)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    fonts_seen = set()
    for page in reader.pages:
        if '/Resources' in page and '/Font' in page['/Resources']:
            for fref in page['/Resources']['/Font'].values():
                try:
                    fobj = fref.get_object()
                    if '/BaseFont' in fobj:
                        fonts_seen.add(str(fobj['/BaseFont']))
                except Exception:
                    pass
    # Allura doit être embarquée pour préserver le rendu manuscrit chez Lulu
    has_allura = any('Allura' in f for f in fonts_seen)
    has_cormorant = any('Cormorant' in f for f in fonts_seen)
    assert has_allura, f'Allura not embedded. Fonts seen: {fonts_seen}'
    assert has_cormorant, f'Cormorant not embedded. Fonts seen: {fonts_seen}'


def test_render_pilot_creates_at_least_two_pages(sample_manuscript):
    """Un chapitre pilote avec CHAPTER_OPENING + PAGE_BREAK + corps doit
    donner au minimum 2 pages physiques."""
    from pypdf import PdfReader
    pdf_bytes = render_manuscript_to_pdf(sample_manuscript)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) >= 2
