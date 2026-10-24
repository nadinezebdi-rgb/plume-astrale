"""Tests de régression pour le renderer vidéo Reels (15s MP4) et son endpoint.

- Vérifie que l'HTML autonome généré contient bien les segments clés (titre,
  cartes, conseil, CTA) et respecte les timings keyframes.
- Vérifie le mapping format → dimensions.
- (optionnel) Vérifie l'endpoint via la base de données locale si un tirage
  partagé existe — sinon skip, pour éviter de bloquer la CI dans les envs
  vides.
"""
from __future__ import annotations
import re
import pytest

from services.reels_video_renderer import (
    _build_html,
    _FORMATS,
    _DURATION_S,
    _FPS,
    TYPE_LABELS,
    DOMAINE_LABELS,
    render_reels_video,
)


SAMPLE_DOC = {
    'share_id': 'abcdef012345',
    'first_name': 'Clara',
    'type': 'marseille',
    'domaine': 'amour',
    'question': 'Vais-je trouver un amour sincère cette année ?',
    'data': {
        'cartes': [
            {'nom': "L'Étoile", 'position': 'Passé', 'orientation': 'droite', 'is_major': True, 'symbole': '✧'},
            {'nom': "L'Amoureux", 'position': 'Présent', 'orientation': 'renverse', 'is_major': True, 'symbole': '♥'},
            {'nom': 'Le Monde', 'position': 'Avenir', 'orientation': 'droite', 'is_major': True, 'symbole': '◉'},
        ],
        'synthese': {
            'tendance_generale': 'Ouverture du cœur',
            'fil_conducteur': "L'Étoile éclaire votre passé.",
        },
        'conseil_final': "Laissez-vous aimer sans forcer, votre cœur est déjà prêt.",
    },
}


# ─── Constantes de contrat ─────────────────────────────────────────────

def test_duration_contract_15s():
    """Le contrat produit est 15s @ 30 fps — ne pas changer sans mise à jour UI."""
    assert _DURATION_S == 15
    assert _FPS == 30


def test_formats_registered():
    """Les deux formats offerts aux utilisateurs doivent être présents."""
    assert 'vertical' in _FORMATS
    assert 'square' in _FORMATS
    assert _FORMATS['vertical'] == {'w': 1080, 'h': 1920}
    assert _FORMATS['square'] == {'w': 1080, 'h': 1080}


def test_type_and_domaine_labels():
    """Les labels affichés doivent couvrir les enums backend."""
    for t in ('marseille', 'celtique', 'complet'):
        assert t in TYPE_LABELS
    for d in ('amour', 'travail', 'argent', 'sante', 'spirituel', 'general'):
        assert d in DOMAINE_LABELS


# ─── HTML template ─────────────────────────────────────────────────────

@pytest.mark.parametrize('fmt', ['vertical', 'square'])
def test_build_html_has_sections(fmt):
    """L'HTML doit contenir toutes les sections visuelles clés."""
    html = _build_html(SAMPLE_DOC, fmt)
    assert '<!DOCTYPE html>' in html
    # Intro
    assert 'Le tirage de' in html
    assert 'Clara' in html
    assert 'TIRAGE MARSEILLE' in html.upper() or 'Tirage Marseille' in html
    assert 'Amour &amp; Relations' in html
    assert 'Vais-je trouver un amour' in html
    # Cards section
    assert 'LES ARCANES' in html.upper() or 'arcanes révélés' in html.lower()
    for c in SAMPLE_DOC['data']['cartes']:
        assert c['nom'].replace("'", '&#x27;') in html or c['nom'] in html
    # Conseil
    assert 'Conseil des Arcanes' in html or 'Fil conducteur' in html
    # CTA
    assert 'plume-astrale.fr' in html


def test_build_html_renverse_card_class():
    """Une carte renversée reçoit la classe `card-rev`."""
    html = _build_html(SAMPLE_DOC, 'vertical')
    # L'Amoureux est en orientation 'renverse' dans SAMPLE_DOC
    assert 'card-rev' in html


def test_build_html_dimensions_match_format():
    """La CSS doit encoder les bonnes dimensions pour chaque format."""
    html_v = _build_html(SAMPLE_DOC, 'vertical')
    html_s = _build_html(SAMPLE_DOC, 'square')
    assert 'width: 1080px' in html_v
    assert 'height: 1920px' in html_v
    assert 'width: 1080px' in html_s
    assert 'height: 1080px' in html_s


def test_build_html_fallback_bad_format():
    """Un format inconnu doit retomber sur 'vertical' sans crasher."""
    html = _build_html(SAMPLE_DOC, 'portrait-weird')
    # fallback → 1920
    assert 'height: 1920px' in html


def test_build_html_handles_minor_arcana():
    """Les arcanes mineurs utilisent rang+suite plutôt qu'un gros symbole d'arcane majeur."""
    doc = {
        **SAMPLE_DOC,
        'data': {
            **SAMPLE_DOC['data'],
            'cartes': [
                {'nom': 'As de Coupe', 'position': 'Oui', 'orientation': 'droite',
                 'is_major': False, 'rang': 'As', 'suite': 'Coupes',
                 'symbole': '♥', 'couleur': '#AA0000'},
            ],
        },
    }
    html = _build_html(doc, 'square')
    assert 'card-art-minor' in html
    assert 'de Coupes' in html


def test_build_html_no_question_safe():
    """Un tirage sans question doit afficher le fallback sans HTML malformé."""
    doc = {**SAMPLE_DOC, 'question': ''}
    html = _build_html(doc, 'vertical')
    assert 'arcanes vont parler' in html.lower()


def test_build_html_escapes_user_input():
    """Les champs utilisateurs doivent être échappés (XSS protection).

    Le filtre `html.escape` ne touche pas aux lettres (donc `onerror=alert`
    reste dans la string) mais échappe `<` et `>`, ce qui neutralise les
    balises actives.
    """
    doc = {
        **SAMPLE_DOC,
        'first_name': '<script>alert(1)</script>',
        'question': '"><img src=x onerror=alert(1)>',
    }
    html = _build_html(doc, 'vertical')
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html
    # Les balises injectées restent inertes car les < sont encodés
    assert '<img src=x' not in html
    assert '&lt;img src=x' in html


# ─── Timing keyframes ─────────────────────────────────────────────────

def test_html_contains_15s_animation_duration():
    """Les animations CSS doivent tourner sur 15 s."""
    html = _build_html(SAMPLE_DOC, 'vertical')
    assert '15s' in html  # pour les keyframes principales


def test_cards_staggered_across_timeline():
    """Chaque carte doit avoir un --card-start distinct, échelonné dans la phase cartes."""
    html = _build_html(SAMPLE_DOC, 'vertical')
    # On ne lit que les valeurs inline style (pas la règle CSS par défaut
    # qui définit --card-start:0s dans un bloc @keyframes).
    starts = re.findall(r'style="[^"]*--card-start:\s*([\d.]+)s', html)
    assert len(starts) == 3
    starts_f = [float(s) for s in starts]
    assert all(2.5 <= s <= 11.5 for s in starts_f), f'starts out of range: {starts_f}'
    # Les starts doivent être strictement croissants (révélation séquentielle)
    assert starts_f == sorted(starts_f)
    assert starts_f[0] < starts_f[1] < starts_f[2]


# ─── Rendu complet (lourd — skippable) ─────────────────────────────────

@pytest.mark.slow
@pytest.mark.asyncio
async def test_render_vertical_mp4_e2e():
    """E2E : Playwright + ffmpeg produisent un vrai MP4 valide (lent, ~25s)."""
    mp4 = await render_reels_video(SAMPLE_DOC, 'vertical')
    assert isinstance(mp4, bytes)
    assert len(mp4) > 100_000, f'MP4 trop petit : {len(mp4)} bytes'
    # Signature ISO BMFF (MP4) : "ftyp" dans les 32 premiers bytes
    assert b'ftyp' in mp4[:64], 'Pas une signature MP4 valide'


@pytest.mark.slow
@pytest.mark.asyncio
async def test_render_square_mp4_e2e():
    """E2E : format carré 1:1 valide (lent, ~20s)."""
    mp4 = await render_reels_video(SAMPLE_DOC, 'square')
    assert len(mp4) > 100_000
    assert b'ftyp' in mp4[:64]
