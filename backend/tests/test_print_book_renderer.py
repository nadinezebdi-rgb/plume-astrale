"""Layout regression: long prose must survive pagination and Lulu export."""
import io
from types import SimpleNamespace
import pytest
from pypdf import PdfReader
from reportlab.lib.units import mm
from services.book_engine_shared.domain import Chapter, ChapterBlock, BlockKind
from services.print_book_renderer import render_book_pdf, lulu_interior, lulu_cover


def manuscript():
    # Deliberately exceeds the former fixed-height blocks, with a unique tail.
    paragraphs = [f'PARAGRAPHE{i:03d} ' + ('Une phrase de lecture longue, avec des accents et une réflexion personnelle. ' * 24) + f' FIN{i:03d}' for i in range(44)]
    return SimpleNamespace(first_name='Élodie Exemple', astro_data={}, chapters=[
        Chapter(slug='natal_preface', title='Introduction', blocks=[ChapterBlock(BlockKind.PARAGRAPH, {'text':'Comment lire ce livre et revenir aux chapitres.'})]),
        Chapter(slug='long',title='Votre chapitre personnel',blocks=[ChapterBlock(BlockKind.PARAGRAPH,{'text':p}) for p in paragraphs])])


@pytest.fixture(scope='module')
def reading():
    return render_book_pdf(manuscript())


def test_all_paragraph_ends_survive_and_sections_are_ordered(reading):
    reader=PdfReader(io.BytesIO(reading))
    text='\n'.join(page.extract_text() for page in reader.pages)
    for i in range(44):
        assert text.count(f'FIN{i:03d}') == 1
    assert text.index('Préface') < text.index('Sommaire') < text.index('Comment lire ton thème')
    assert (len(reader.pages)-2)%2 == 0


def test_lulu_is_distinct_bleed_interior_and_text_survives(reading):
    reader=PdfReader(io.BytesIO(reading))
    interior=PdfReader(io.BytesIO(lulu_interior(reading)))
    assert len(interior.pages)==len(reader.pages)-2
    page=interior.pages[0]
    assert float(page.mediabox.width)/mm == pytest.approx(154.35)
    assert float(page.mediabox.height)/mm == pytest.approx(216.35)
    assert float(page.trimbox.width)/mm == pytest.approx(148)
    assert 'FIN043' in '\n'.join(p.extract_text() for p in interior.pages)
    for p in interior.pages:
        fonts = p['/Resources'].get('/Font')
        for ref in (fonts.get_object().values() if fonts else []):
            font=ref.get_object()
            descriptor=font.get('/FontDescriptor')
            assert descriptor and descriptor.get_object().get('/FontFile2')


def test_legacy_pdf_rejected_and_cover_dimensions_exact(reading):
    from pypdf import PdfWriter
    stream=io.BytesIO(); writer=PdfWriter();writer.add_blank_page(100,100);writer.write(stream)
    with pytest.raises(ValueError,match='Ancien PDF'):
        lulu_interior(stream.getvalue())
    cover=lulu_cover(manuscript(),width_mm=320,height_mm=230,
        front_box_mm=(164,10,148,210),back_box_mm=(8,10,148,210))
    pages=PdfReader(io.BytesIO(cover)).pages
    assert len(pages)==1
    assert float(pages[0].mediabox.width)/mm == pytest.approx(320)
    assert 'Élodie Exemple' in pages[0].extract_text()


@pytest.mark.parametrize('interior_pages', [42, 150])
def test_short_and_long_book_page_ranges(interior_pages):
    # Explicit manuscript page breaks simulate different editorial lengths;
    # the production renderer itself never pads a book to reach this range.
    m=manuscript()
    blocks=[]
    for number in range(interior_pages-6):
        if blocks:
            blocks.append(ChapterBlock(BlockKind.PAGE_BREAK,{}))
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH,{
            'text': f'PAGE{number:03d} Une réflexion complète à conserver dans cette édition.'}))
    m.chapters[1].blocks=blocks
    reading=render_book_pdf(m)
    interior=PdfReader(io.BytesIO(lulu_interior(reading)))
    assert len(interior.pages)==interior_pages
    text='\n'.join(page.extract_text() for page in interior.pages)
    for number in range(interior_pages-6):
        assert text.count(f'PAGE{number:03d}')==1
