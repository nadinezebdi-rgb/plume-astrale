"""Test suite — Prototype /experience isolé
   Vérifie uniquement le wiring : la route est présente, elle ne casse
   AUCUN autre parcours du site (Navbar/CookieConsent la masquent).
"""
from __future__ import annotations


def test_route_experience_registered_in_app_js():
    with open('/app/frontend/src/App.js') as f:
        code = f.read()
    assert 'path="/experience"' in code, 'Route /experience manquante dans App.js'
    assert 'ExperiencePage' in code
    # Vérifie le lazy loading — pour ne pas alourdir les autres bundles
    with open('/app/frontend/src/pages/Experience.js') as f:
        page_code = f.read()
    assert 'React.lazy' in page_code or 'lazy(' in page_code


def test_navbar_hides_itself_on_experience():
    """La Navbar doit se cacher sur /experience pour préserver l'immersion."""
    with open('/app/frontend/src/components/NavbarV2.js') as f:
        code = f.read()
    assert "location.pathname === '/experience'" in code
    assert 'return null' in code


def test_cookie_consent_hides_itself_on_experience():
    """Le bandeau cookies ne doit pas casser l'effet WOW du prototype."""
    with open('/app/frontend/src/components/CookieConsent.js') as f:
        code = f.read()
    assert "location.pathname === '/experience'" in code
    # useLocation doit être importé
    assert 'useLocation' in code


def test_experience_uses_expected_palette():
    """La palette Nocturne doit être présente dans le CSS du prototype."""
    with open('/app/frontend/src/experience/Experience.css') as f:
        css = f.read()
    for color in ['#070713', '#17102E', '#7657C8', '#D8B76A', '#F4EFE6']:
        assert color in css, f'Couleur palette manquante : {color}'


def test_four_scenes_and_data_testids_present():
    """Les 4 scènes attendues avec leurs data-testids doivent être présentes."""
    with open('/app/frontend/src/experience/ExperienceRoot.jsx') as f:
        code = f.read()
    for testid in ['experience-scene-1', 'experience-scene-2',
                   'experience-scene-3', 'experience-scene-4',
                   'scene-1-cta', 'scene-2-grid',
                   'scene-3-cards', 'scene-4-cta']:
        assert f'data-testid="{testid}"' in code, f'testid manquant : {testid}'


def test_experience_page_has_noindex():
    """La route /experience est un prototype — noindex obligatoire."""
    with open('/app/frontend/src/pages/Experience.js') as f:
        code = f.read()
    assert 'noindex' in code


def test_final_cta_navigates_to_inscription():
    """Le CTA final "Commencer mon voyage" doit rediriger vers /inscription
    (choix utilisateur validé lors de la conception)."""
    with open('/app/frontend/src/experience/ExperienceRoot.jsx') as f:
        code = f.read()
    assert "navigate('/inscription')" in code


def test_fallback_present_for_reduced_motion_and_webgl():
    """Un fallback statique doit exister pour les utilisateurs qui refusent
    les animations ou dont le navigateur n'a pas WebGL."""
    import os
    assert os.path.exists('/app/frontend/src/experience/ExperienceFallback.jsx')
    with open('/app/frontend/src/experience/ExperienceRoot.jsx') as f:
        code = f.read()
    assert 'reducedMotion' in code
    assert 'webglAvailable' in code
    assert 'ExperienceFallback' in code


def test_intent_and_drawn_card_persist_in_store():
    """L'intent choisi + la carte tirée doivent être stockés dans Zustand
    (pour personnaliser le vrai parcours plus tard)."""
    with open('/app/frontend/src/experience/useExperienceStore.js') as f:
        code = f.read()
    assert 'intent' in code
    assert 'drawnCard' in code
    assert 'setIntent' in code
    assert 'setDrawnCard' in code
