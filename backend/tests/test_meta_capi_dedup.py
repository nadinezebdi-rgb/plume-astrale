"""Tests de non-régression sur le tracking Meta (statiques, sans réseau)."""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def test_wallet_service_n_envoie_plus_de_capi():
    src = _read('backend/services/wallet_service.py')
    assert 'send_capi_event(' not in src


def test_purchase_capi_envoie_event_id_et_matching():
    src = _read('backend/services/capi_purchase.py')
    m = re.search(r'ok = await send_capi_event\(.*?\n    \)', src, re.S)
    assert m, 'appel send_capi_event introuvable'
    body = m.group(0)
    for champ in ('event_id=', 'client_ip=', 'client_user_agent=', 'fbp=', 'fbc='):
        assert champ in body, f'{champ} manquant'


def test_valeur_purchase_basee_sur_stripe():
    src = _read('backend/services/capi_purchase.py')
    assert "sd.get('amount_total')" in src
    assert 'amount * 0.9' not in src
    assert 'amount * 0.9' not in _read('backend/server.py')
    assert 'amount * 0.9' not in _read('backend/services/wallet_service.py')


def test_capi_appele_sur_les_deux_chemins():
    src = _read('backend/server.py')
    assert src.count('track_purchase_once(') >= 2


def test_consommation_credits_nest_pas_achat():
    analytics = _read('frontend/src/lib/analytics.js')
    assert "credits_spent:" in analytics


def test_attribution_respecte_consentement():
    analytics = _read('frontend/src/lib/analytics.js')
    m = re.search(r'export function getCapiAttribution.*?\n}', analytics, re.S)
    assert m
    assert "if (getConsent() !== 'accepted') return {};" in m.group(0)


def test_hook_place_avant_routage_produit():
    src = _read('backend/server.py')
    hook = src.index('track_purchase_once')
    branche = src.index("md.get('kind') == 'synastrie_oneshot'")
    assert hook < branche


def test_idempotence_via_verrou_conditionnel():
    src = _read('backend/services/capi_purchase.py')
    assert ".is_('capi_sent_at', 'null')" in src
    assert "update({'capi_sent_at': now})" in src


def test_verrou_relache_si_echec():
    src = _read('backend/services/capi_purchase.py')
    assert 'def _release' in src
    assert '_release, session_id' in src


def test_attribution_table_dediee():
    src = _read('backend/middleware/meta_attribution.py')
    assert 'checkout_attribution' in src
    assert 'payment_transactions' not in src


def test_middleware_couvre_checkouts():
    src = _read('backend/middleware/meta_attribution.py')
    assert "'/checkout' in request.url.path" in src


def test_middleware_enregistre():
    assert 'meta_attribution_middleware' in _read('backend/server.py')


def test_interceptor_frontend():
    src = _read('frontend/src/lib/metaAttribution.js')
    assert 'axios.interceptors.request.use' in src
    assert "url.includes('/checkout')" in src
    assert 'if (!eventId) return config;' in src
    assert 'installMetaAttribution' in _read('frontend/src/index.js')


def test_migration_sql():
    sql = _read('supabase/checkout_attribution_migration.sql')
    assert 'create table if not exists public.checkout_attribution' in sql
    assert 'capi_sent_at' in sql
    assert 'enable row level security' in sql


def test_defense_en_profondeur_table_manquante():
    """Le middleware doit warn au lieu de crasher si la migration n'a pas tourné."""
    src = _read('backend/middleware/meta_attribution.py')
    assert '_TABLE_MISSING_WARNED' in src
    assert 'introuvable' in src
