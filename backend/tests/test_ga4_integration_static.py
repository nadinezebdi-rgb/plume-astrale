"""GA4 Integration — static regression tests (Feb 2026)

L'user a demandé une intégration GA4 propre :
  - Env var REACT_APP_GA4_ID (jamais hardcodé)
  - Google Consent Mode v2 (defaults denied, granted post-consent)
  - Events GA4 standards : page_view, sign_up_start, sign_up, login, cta_click,
    view_item, begin_checkout, purchase
  - Anti-PII (aucun email/nom/token envoyé)
  - Dédup purchase (client + backend)
  - RouteTracker unique source de page_view (send_page_view=false sur config)

Ces tests garantissent qu'aucun refactor futur ne casse ces invariants.
"""
from pathlib import Path

ANALYTICS = Path('/app/frontend/src/lib/analytics.js')
REGISTER = Path('/app/frontend/src/pages/Register.js')
LOGIN = Path('/app/frontend/src/pages/Login.js')
ROUTETRACKER = Path('/app/frontend/src/components/RouteTracker.js')
ENV = Path('/app/frontend/.env')


def test_env_declares_ga4_placeholder():
    """REACT_APP_GA4_ID doit exister dans .env pour que l'user puisse renseigner."""
    src = ENV.read_text()
    assert 'REACT_APP_GA4_ID=' in src, (
        'REACT_APP_GA4_ID manquant dans frontend/.env — impossible d\'activer GA4.'
    )


def test_analytics_never_hardcodes_ga4_id():
    """Aucun ID GA4 hardcodé (pattern G-XXXXXXXXXX) dans le code."""
    import re
    for p in Path('/app/frontend/src').rglob('*.js'):
        src = p.read_text()
        # Faux positifs : le pattern doit être un vrai ID GA4 (G-<8+ chars alphanum>)
        matches = re.findall(r"['\"]G-[A-Z0-9]{6,}['\"]", src)
        assert not matches, (
            f"ID GA4 hardcodé dans {p}: {matches}. Doit venir de process.env.REACT_APP_GA4_ID"
        )


def test_consent_mode_v2_defaults_denied():
    src = ANALYTICS.read_text()
    assert 'pushConsentDefaults' in src, 'Consent Mode v2 defaults absents'
    for signal in ('ad_storage', 'analytics_storage', 'ad_user_data', 'ad_personalization'):
        assert signal in src, f'Signal Consent Mode v2 manquant : {signal}'
    # Defaults doivent être denied
    assert "ad_storage: 'denied'" in src, 'ad_storage default doit être denied'
    assert "analytics_storage: 'denied'" in src, 'analytics_storage default doit être denied'
    # Update on accept
    assert 'pushConsentGranted' in src, 'Update consent (granted) manquant'
    assert "'update'" in src or '"update"' in src, "gtag('consent', 'update', …) absent"


def test_page_view_is_single_source_of_truth():
    """RouteTracker doit être la SEULE source de page_view GA4 (send_page_view=false)."""
    a = ANALYTICS.read_text()
    assert 'send_page_view: false' in a, (
        "gtag('config', GA, { send_page_view: false }) manquant — "
        "double comptage page_view garanti à l'init + navigation SPA."
    )
    # pageView() doit émettre un event 'page_view' explicite (pas config())
    assert "gtag('event', 'page_view'" in a, (
        "pageView() doit émettre gtag('event', 'page_view', …) — "
        "l'ancien 'config()' produisait un double hit."
    )
    r = ROUTETRACKER.read_text()
    assert 'pageView' in r, 'RouteTracker n\'appelle pas pageView()'


def test_ga4_event_mapping_covers_standards():
    src = ANALYTICS.read_text()
    assert 'GA4_EVENT_MAP' in src, 'GA4_EVENT_MAP absent'
    # Chaque event standard GA4 requis par la spec V3 doit être mappé
    required = [
        ("signup_started", "sign_up_start"),
        ("signup_completed", "sign_up"),
        ("login", "login"),
        ("credit_purchase", "purchase"),
        ("kabbale_checkout", "begin_checkout"),
        ("bundle_click", "view_item"),
    ]
    for src_name, ga4_name in required:
        assert f"{src_name}:" in src and ga4_name in src, (
            f"Mapping GA4 manquant : {src_name} → {ga4_name}"
        )


def test_pii_sanitizer_present():
    src = ANALYTICS.read_text()
    assert 'sanitizeProps' in src, 'sanitizeProps() absent — risque envoi PII à GA4'
    assert 'PII_KEYS' in src, 'PII_KEYS absent'
    # Clés critiques
    for k in ('email', 'password', 'token', 'prenom', 'phone'):
        assert f"'{k}'" in src, f"PII_KEYS ne bloque pas '{k}'"


def test_cta_click_helper_exposed():
    src = ANALYTICS.read_text()
    assert 'export function ctaClick' in src, 'Helper ctaClick() absent'
    assert 'cta_name' in src, "Paramètre 'cta_name' absent"
    assert 'page_location' in src, "Paramètre 'page_location' absent"
    # Constante EVENTS.CTA_CLICK
    assert 'CTA_CLICK:' in src, 'EVENTS.CTA_CLICK absent'


def test_signup_start_helper_and_register_emits_it():
    a = ANALYTICS.read_text()
    assert 'export function signUpStart' in a, 'signUpStart() absent de analytics.js'
    assert 'pa_signup_start_tracked' in a, 'Guard sessionStorage sign_up_start absent'
    r = REGISTER.read_text()
    assert 'signUpStart' in r, 'Register.js n\'émet pas signUpStart()'


def test_login_uses_standard_login_event():
    src = LOGIN.read_text()
    assert 'EVENTS.LOGIN' in src, 'Login.js n\'utilise pas EVENTS.LOGIN (event standard GA4)'
    assert 'login_success' not in src, (
        "Login.js émet encore 'login_success' au lieu de 'login' — "
        "GA4 ne reconnaîtra pas comme event standard."
    )


def test_revenue_purchase_dedup_and_ecommerce_structure():
    src = ANALYTICS.read_text()
    # transaction_id GA4 (dedup native)
    assert 'transaction_id' in src, 'transaction_id (dédup GA4 native) absent de revenue()'
    # items[] structure e-commerce GA4
    assert 'items' in src and 'item_id' in src and 'item_name' in src, (
        'Structure items[] e-commerce absente de revenue()'
    )
    # Dédup Meta CAPI existante
    assert 'eventID' in src, 'eventID (dédup Meta CAPI) supprimé par erreur'


def test_credit_success_page_dedups_purchase():
    """Le success page ne doit tirer revenue() qu'une fois par session_id."""
    src = Path('/app/frontend/src/pages/CreditSuccess.js').read_text()
    assert 'pa_purchase_tracked_' in src, (
        'Dédup client sessionStorage absente de CreditSuccess.js — '
        'un refresh de la page success re-tirerait purchase.'
    )
