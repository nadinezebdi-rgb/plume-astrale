"""ctaClick coverage + Perf lazy Scene04Feather (Feb 2026)

Vérifie que :
  - Les CTA majeurs émettent ctaClick() avec cta_name + destination
  - Scene04Feather est lazy-loaded (React.lazy) et monté conditionnellement
"""
from pathlib import Path

HOMEPAGE = Path('/app/frontend/src/pages/Homepage.js')
EXPROOT = Path('/app/frontend/src/experience/ExperienceRoot.jsx')
SPLASH = Path('/app/frontend/src/experience/WelcomeSplash.jsx')
CANVAS = Path('/app/frontend/src/experience/ExperienceCanvas.jsx')


def test_homepage_ctas_emit_ctaclick():
    src = HOMEPAGE.read_text()
    assert 'ctaClick' in src, 'ctaClick non importé dans Homepage.js'
    # 3 CTA majeurs instrumentés : Feuilleter, Détails livre, Voir bibliothèque
    for label in ('Feuilleter', 'Détails livre', 'Voir toute la bibliothèque'):
        assert label in src, f'ctaClick "{label}" absent de Homepage.js'


def test_experience_final_cta_emits_ctaclick():
    src = EXPROOT.read_text()
    assert 'ctaClick' in src, 'ctaClick non importé dans ExperienceRoot.jsx'
    assert "'Commencer mon voyage'" in src, "ctaClick 'Commencer mon voyage' absent"
    assert "'experience_scene_4_feather'" in src, "cta_location scene_4_feather absent"


def test_welcomesplash_primary_secondary_emit_ctaclick():
    src = SPLASH.read_text()
    assert 'ctaClick' in src, 'ctaClick non importé dans WelcomeSplash.jsx'
    # Le label est passé dynamiquement — vérifie la signature
    assert "'welcome_splash'" in src, "cta_location welcome_splash absent"


def test_scene04feather_is_lazy_loaded():
    """Perf : Scene04Feather doit être React.lazy + monté conditionnellement."""
    src = CANVAS.read_text()
    # Pas d'import synchrone
    assert "import Scene04Feather from './scenes/Scene04Feather'" not in src, (
        "Scene04Feather encore importée en synchrone — le lazy chunk ne se crée pas."
    )
    # Import lazy
    assert 'lazy(() => import' in src and 'Scene04Feather' in src, (
        'Scene04Feather doit être chargée via React.lazy(() => import(...))'
    )
    # Rendu conditionnel : shouldMountFeather
    assert 'shouldMountFeather' in src, (
        'Scene04 doit être conditionnellement rendue via shouldMountFeather.'
    )
    assert 'currentScene >= 3' in src, (
        'Trigger conditionnel currentScene >= 3 absent — Scene04 se monte trop tôt.'
    )


def test_suspense_boundary_still_wraps_stage():
    """R3F Suspense fallback null → aucun flash visuel pendant le chunk fetch."""
    src = CANVAS.read_text()
    assert 'Suspense' in src, 'Boundary Suspense retirée par erreur'
    assert 'fallback={null}' in src, 'Suspense fallback null retiré — risque de flash'
