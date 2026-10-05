"""Regression test — Scene 3 revelations (Feb 2026)

Contexte financier : la révélation générique après le tirage de carte ne
créait pas de tension commerciale ("Cette carte éclaire une partie de votre
question / Mais seule elle ne raconte pas toute l'histoire"). C'était trop
poétique pour convertir.

Fix : 12 phrases (3 cartes × 4 intentions) qui :
  1. Révèlent un fragment SPÉCIFIQUE au contexte du user
  2. Nomment ce qui reste caché (tension)
  3. Pointent vers le service correspondant (promesse)

Ces tests garantissent que le module scene3Revelations.js couvre bien les
12 combinaisons (heart/moon/star × relationship/clarity/self_discovery/
specific_question), que chaque combo est branché dans les 2 renderers
(ExperienceRoot + ExperienceFallback), et que le fallback poétique existe
toujours pour les edge cases.
"""
import re
from pathlib import Path

REVEL = Path('/app/frontend/src/experience/scene3Revelations.js')
EXPROOT = Path('/app/frontend/src/experience/ExperienceRoot.jsx')
FALLBACK = Path('/app/frontend/src/experience/ExperienceFallback.jsx')


CARDS = ('heart', 'moon', 'star')
INTENTS = ('relationship', 'clarity', 'self_discovery', 'specific_question')


def test_all_12_combos_defined():
    """Les 12 combinaisons carte×intent doivent avoir revelation + tension + cta."""
    src = REVEL.read_text()
    for card in CARDS:
        # Bloc de la carte : de "  card: {" jusqu'au "\n  }," de fin
        m = re.search(rf'\n  {card}:\s*\{{(.+?)\n  \}},', src, re.DOTALL)
        assert m, f'Bloc carte "{card}" manquant dans scene3Revelations.js'
        block = m.group(1)
        for intent in INTENTS:
            im = re.search(rf'\n    {intent}:\s*\{{(.+?)\n    \}}', block, re.DOTALL)
            assert im, f'Combo {card}.{intent} manquant dans scene3Revelations.js'
            combo = im.group(1)
            for key in ('revelation', 'tension', 'cta'):
                assert re.search(rf'{key}:\s*[\'"]', combo), (
                    f'Champ "{key}" manquant pour combo {card}.{intent}'
                )


def test_fallback_defined():
    src = REVEL.read_text()
    assert 'SCENE3_FALLBACK' in src, 'SCENE3_FALLBACK absent — edge case non couvert'
    assert 'getScene3Revelation' in src, 'Helper getScene3Revelation absent'


def test_experienceroot_uses_dynamic_revelation():
    """ExperienceRoot doit brancher getScene3Revelation dans la scène 3."""
    src = EXPROOT.read_text()
    assert 'getScene3Revelation' in src, (
        "ExperienceRoot n'importe pas getScene3Revelation — la scène 3 "
        "affiche encore la révélation générique."
    )
    # Data-testid critiques pour QA
    for tid in ('scene-3-revelation', 'scene-3-tension', 'scene-3-continue'):
        assert tid in src, f'data-testid {tid} absent dans ExperienceRoot'
    # Anti-régression : la phrase générique ne doit plus être en dur
    assert 'Cette carte éclaire une partie de votre question' not in src, (
        "Phrase générique encore présente dans ExperienceRoot — "
        "le fix scène 3 n'a pas été appliqué."
    )


def test_experiencefallback_uses_dynamic_revelation():
    """Le fallback (reduced-motion / no WebGL) doit aussi utiliser
    getScene3Revelation, sinon les users mobile bas de gamme voient
    la révélation générique et le tunnel perd sa cohérence."""
    src = FALLBACK.read_text()
    assert 'getScene3Revelation' in src, (
        "ExperienceFallback n'utilise pas getScene3Revelation — "
        "les users en reduced-motion perdent la tension commerciale."
    )
    for tid in ('scene-3-revelation', 'scene-3-tension', 'scene-3-continue'):
        assert tid in src, f'data-testid {tid} absent dans ExperienceFallback'
    assert 'Cette carte a quelque chose à vous montrer' not in src, (
        "Phrase générique du fallback encore présente."
    )


def test_self_discovery_cta_routes_to_theme_natal():
    """Pour l'intent self_discovery, le CTA doit pointer vers le thème natal
    (pas vers un tirage tarot). Vérification narrative + commerciale."""
    src = REVEL.read_text()
    # Extrait tous les blocs self_discovery des 3 cartes
    matches = re.findall(
        r'self_discovery:\s*\{[^{}]*cta:\s*[\'"]([^\'"]+)[\'"]',
        src,
    )
    assert len(matches) == 3, f'Attendu 3 CTA self_discovery, trouvé {len(matches)}'
    for cta in matches:
        assert 'thème natal' in cta.lower(), (
            f'CTA self_discovery ne route pas vers le thème natal: {cta!r}'
        )
