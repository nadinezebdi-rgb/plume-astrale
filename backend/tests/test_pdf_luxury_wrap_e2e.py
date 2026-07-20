"""
E2E validation of pdf_luxury_wrap for Kabbale + Astrocarto.

Verifies that the same code path called by the Stripe webhook worker
(generate_*_pdf_luxury) produces a valid multi-page PDF without
BytesIO/pypdf stream errors.
"""
import io
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.pdf_luxury_wrap import (  # noqa: E402
    generate_kabbale_pdf_luxury,
    generate_astrocartographie_pdf_luxury,
)


def _assert_valid_pdf(pdf_bytes: bytes, min_pages: int, min_size_kb: int, label: str) -> int:
    from pypdf import PdfReader
    assert pdf_bytes, f'{label}: PDF vide'
    assert pdf_bytes[:4] == b'%PDF', f'{label}: header PDF invalide'
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = len(reader.pages)
    size_kb = len(pdf_bytes) // 1024
    assert pages >= min_pages, f'{label}: {pages} pages < {min_pages}'
    assert size_kb >= min_size_kb, f'{label}: {size_kb}KB < {min_size_kb}KB'
    print(f'  OK {label}: {pages} pages, {size_kb} KB')
    return pages


def test_kabbale_wrapper():
    """Kabbale: legacy inner + luxury cover (3p) + luxury ending (2p)."""
    tree = {
        'data': {
            'sephiroth': {
                'kether': {'name': 'Kether', 'meaning': 'La Couronne', 'score': 82},
                'chokmah': {'name': 'Chokmah', 'meaning': 'Sagesse', 'score': 74},
                'binah': {'name': 'Binah', 'meaning': 'Compréhension', 'score': 68},
                'chesed': {'name': 'Chesed', 'meaning': 'Miséricorde', 'score': 71},
                'geburah': {'name': 'Geburah', 'meaning': 'Rigueur', 'score': 65},
                'tiphareth': {'name': 'Tiphareth', 'meaning': 'Beauté', 'score': 88},
                'netzach': {'name': 'Netzach', 'meaning': 'Victoire', 'score': 70},
                'hod': {'name': 'Hod', 'meaning': 'Splendeur', 'score': 62},
                'yesod': {'name': 'Yesod', 'meaning': 'Fondation', 'score': 78},
                'malkuth': {'name': 'Malkuth', 'meaning': 'Royaume', 'score': 55},
            },
            'daat': {'name': 'Daat', 'active': True, 'meaning': 'Connaissance'},
            'paths': [
                {'from': 'kether', 'to': 'chokmah', 'name': 'Aleph'},
                {'from': 'kether', 'to': 'binah', 'name': 'Beth'},
            ],
            'pillar_balance': {'mercy': 72, 'severity': 65, 'mildness': 78},
            'dominant_sephirah': 'Tiphareth',
            'spiritual_focus': 'Rayonner ta beauté intérieure',
            'synthesis': (
                'Ton Arbre de Vie révèle un axe central très puissant autour '
                'de Tiphareth. Tu portes une lumière que le monde attend.'
            ),
        }
    }
    pdf = generate_kabbale_pdf_luxury(
        first_name='Sophie',
        birth_date_iso='1990-06-15',
        tree_of_life=tree,
    )
    pages = _assert_valid_pdf(pdf, min_pages=5, min_size_kb=100, label='Kabbale luxury')

    Path('/tmp/kabbale_luxury_e2e.pdf').write_bytes(pdf)
    print(f'  → /tmp/kabbale_luxury_e2e.pdf ({pages} pages)')


def test_astrocarto_wrapper():
    """Astrocarto: legacy inner + luxury cover (3p) + luxury ending (2p)."""
    chosen = [
        {
            'city': 'Lisbonne', 'country': 'Portugal', 'country_code': 'PT',
            'raw': {'planetary_lines': ['Venus-MC', 'Jupiter-ASC']},
            'enriched': {
                'why': 'La ligne Vénus t\'y attend pour révéler ta douceur.',
                'promise': 'Amour, art, lenteur solaire.',
                'ambiance': 'Chaleureuse et créative',
                'career': 'Arts, design, écriture',
                'love': 'Rencontres profondes',
                'spiritual': 'Retour au corps',
                'body': 'Détente, sommeil profond',
                'advice_solena': 'Prends au moins 3 semaines pour y respirer.',
            },
            'nearby_lines': [{'planet': 'Venus', 'line_type': 'MC'}],
        },
        {
            'city': 'Bali', 'country': 'Indonésie', 'country_code': 'ID',
            'raw': {'planetary_lines': ['Neptune-IC']},
            'enriched': {
                'why': 'Neptune t\'y invite au rêve conscient.',
                'promise': 'Éveil spirituel, guérison de l\'enfance.',
                'ambiance': 'Mystique et douce',
                'career': 'Coaching, thérapies',
                'love': 'Amour karmique',
                'spiritual': 'Ouverture du 3e œil',
                'body': 'Guérison profonde',
                'advice_solena': 'Écoute tes rêves dès la 1ère nuit.',
            },
            'nearby_lines': [{'planet': 'Neptune', 'line_type': 'IC'}],
        },
        {
            'city': 'Kyoto', 'country': 'Japon', 'country_code': 'JP',
            'raw': {'planetary_lines': ['Saturne-DC']},
            'enriched': {
                'why': 'Saturne t\'y forge une discipline juste.',
                'promise': 'Structure, rigueur créative.',
                'ambiance': 'Précise et silencieuse',
                'career': 'Recherche, artisanat',
                'love': 'Partenariat solide',
                'spiritual': 'Méditation zen',
                'body': 'Endurance',
                'advice_solena': 'Impose-toi un rituel matinal.',
            },
            'nearby_lines': [{'planet': 'Saturne', 'line_type': 'DC'}],
        },
    ]
    bonus = [
        {
            'city': 'Marrakech', 'country': 'Maroc',
            'enriched': {
                'why': 'Le Soleil t\'y attend pour rayonner.',
                'promise': 'Confiance en toi, exposition publique.',
            },
            'nearby_lines': [],
        },
        {
            'city': 'Reykjavik', 'country': 'Islande',
            'enriched': {
                'why': 'Uranus t\'y libère d\'une prison intérieure.',
                'promise': 'Rupture bénéfique, renaissance.',
            },
            'nearby_lines': [],
        },
    ]
    pdf = generate_astrocartographie_pdf_luxury(
        first_name='Léa',
        birth_date_iso='1988-11-03',
        map_svg=None,
        chosen_cities=chosen,
        bonus_cities=bonus,
        synthesis_text=(
            'Ton triangle géographique — Lisbonne, Bali, Kyoto — dessine '
            'une trajectoire de renaissance. Vénus t\'ouvre, Neptune te '
            'guérit, Saturne te structure.'
        ),
        lines_data=[
            {'planet': 'Venus', 'line_type': 'MC'},
            {'planet': 'Neptune', 'line_type': 'IC'},
        ],
    )
    pages = _assert_valid_pdf(pdf, min_pages=5, min_size_kb=150, label='Astrocarto luxury')

    Path('/tmp/astrocarto_luxury_e2e.pdf').write_bytes(pdf)
    print(f'  → /tmp/astrocarto_luxury_e2e.pdf ({pages} pages)')


if __name__ == '__main__':
    print('▶ Test 1: Kabbale luxury wrap')
    test_kabbale_wrapper()
    print('▶ Test 2: Astrocarto luxury wrap')
    test_astrocarto_wrapper()
    print('\n✓ Tous les tests E2E du wrapper luxe passent.')
