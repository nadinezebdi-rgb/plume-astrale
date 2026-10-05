"""GTM Integration — static regression tests (Feb 2026)

Contrat :
  - GTM container ID installé dans public/index.html (script + noscript)
  - Consent Mode v2 defaults poussés INLINE dans <head> AVANT le chargement GTM
  - lib/analytics.js pousse aussi les events au format GTM natif ({event: name, ...})
  - Pas de duplication : les defaults ne sont plus poussés depuis analytics.js
"""
from pathlib import Path

INDEX_HTML = Path('/app/frontend/public/index.html')
ANALYTICS = Path('/app/frontend/src/lib/analytics.js')
ENV = Path('/app/frontend/.env')


def test_gtm_script_installed_in_head():
    src = INDEX_HTML.read_text()
    assert "googletagmanager.com/gtm.js" in src, "GTM <script> tag manquant dans index.html"
    assert "GTM-NQFXFLRR" in src, "Container ID GTM-NQFXFLRR manquant"


def test_gtm_noscript_installed_after_body():
    src = INDEX_HTML.read_text()
    # Le noscript doit exister
    assert "googletagmanager.com/ns.html?id=GTM-NQFXFLRR" in src, "GTM <noscript> manquant"
    # Le noscript doit être APRÈS <body>
    body_idx = src.find("<body>")
    ns_idx = src.find("googletagmanager.com/ns.html")
    assert body_idx > 0 and ns_idx > body_idx, "GTM <noscript> doit être après <body>"


def test_consent_defaults_before_gtm_script():
    """Order critical : consent defaults DOIT être poussé AVANT gtm.js."""
    src = INDEX_HTML.read_text()
    default_idx = src.find("consent', 'default'")
    gtm_idx = src.find("googletagmanager.com/gtm.js")
    assert default_idx > 0, "Consent Mode v2 defaults inline absent"
    assert gtm_idx > 0
    assert default_idx < gtm_idx, (
        "Consent defaults doit être poussé AVANT le script GTM — "
        "sinon GTM peut charger des tags analytics avant le denied."
    )
    # Les 4 signaux critiques
    for signal in ('ad_storage', 'analytics_storage', 'ad_user_data', 'ad_personalization'):
        assert signal in src[:gtm_idx], f'Signal Consent Mode v2 {signal} absent avant GTM'


def test_analytics_no_longer_pushes_defaults():
    """Anti-doublon : les defaults sont désormais dans index.html uniquement."""
    src = ANALYTICS.read_text()
    assert 'pushConsentDefaults' not in src, (
        "pushConsentDefaults() encore présent dans analytics.js — "
        "duplication avec index.html."
    )
    # pushConsentGranted() DOIT rester (déclenché après acceptation cookies)
    assert 'pushConsentGranted' in src, "pushConsentGranted() manquant — l'update après consent est perdu"


def test_events_pushed_in_gtm_native_format():
    """event() doit pousser {event: name, ...} pour les Custom Event Triggers GTM."""
    src = ANALYTICS.read_text()
    assert 'window.dataLayer.push({ event: name' in src, (
        "Push GTM-native ({event: name, ...}) manquant dans event()."
    )
    # pageView : push GTM natif
    assert "event: 'page_view'" in src, "Push GTM natif 'page_view' manquant"
    # revenue : push GTM natif e-commerce
    assert "event: 'purchase'" in src, "Push GTM natif 'purchase' manquant"
    assert 'ecommerce:' in src, "Structure e-commerce GTM manquante dans revenue()"


def test_env_has_gtm_id():
    src = ENV.read_text()
    assert 'REACT_APP_GTM_ID=GTM-NQFXFLRR' in src, (
        "REACT_APP_GTM_ID absent de .env — traçabilité du container ID cassée."
    )
