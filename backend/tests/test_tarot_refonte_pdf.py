# Tests refonte page Tarot : endpoints marseille / celtique / pdf
import os
import re
import time
import unicodedata
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

SLUGS = {
    'mat', 'bateleur', 'papesse', 'imperatrice', 'empereur', 'pape', 'amoureux', 'chariot',
    'justice', 'hermite', 'roue_de_fortune', 'force', 'pendu', 'arcane_sans_nom', 'temperance',
    'diable', 'maison_dieu', 'etoile', 'lune', 'soleil', 'jugement', 'monde',
}


def _norm(s):
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    s = re.sub(r'[^a-z0-9_]', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return re.sub(r'^(les|le|la|l)_', '', s)


@pytest.fixture(scope='module')
def marseille():
    t = time.time()
    r = requests.post(f"{BASE_URL}/api/tarot/marseille",
                      json={'question': 'TEST_ Vais-je trouver ma voie ?', 'domaine': 'travail'}, timeout=120)
    print(f"marseille took {time.time()-t:.1f}s")
    assert r.status_code == 200, r.text[:300]
    return r.json()


@pytest.fixture(scope='module')
def celtique():
    t = time.time()
    r = requests.post(f"{BASE_URL}/api/tarot/celtique",
                      json={'question': 'TEST_ Mon projet va-t-il aboutir ?', 'domaine': 'general'}, timeout=120)
    print(f"celtique took {time.time()-t:.1f}s")
    assert r.status_code == 200, r.text[:300]
    return r.json()


# Marseille
def test_marseille_structure(marseille):
    assert marseille['success'] is True
    d = marseille['data']
    assert len(d['cartes']) == 3
    assert isinstance(d.get('synthese'), dict)
    assert isinstance(d.get('conseil_final'), str) and d['conseil_final']
    for c in d['cartes']:
        for k in ('nom', 'orientation', 'interpretation', 'mots_cles', 'element', 'planete'):
            assert k in c, f"missing {k} in {c.keys()}"
        assert c['orientation'] in ('droit', 'renverse'), c['orientation']
        assert _norm(c['nom']) in SLUGS, f"nom non mappé vers Supabase: {c['nom']}"


# Celtique
def test_celtique_structure(celtique):
    assert celtique['success'] is True
    d = celtique['data']
    assert len(d['cartes']) == 10
    a = d['analyse']
    for k in ('energie_globale', 'cartes_droites', 'cartes_renversees', 'element_dominant',
              'situation_actuelle', 'obstacle_principal', 'fondement', 'resultat_probable',
              'synthese_finale', 'conseil_action'):
        assert k in a, f"missing {k}"
    assert 'carte' in a['situation_actuelle'] and 'message' in a['situation_actuelle']
    for c in d['cartes']:
        assert _norm(c['nom']) in SLUGS, f"nom non mappé: {c['nom']}"


# PDF
def _pdf(tp, data, question='Ma question ?'):
    t = time.time()
    r = requests.post(f"{BASE_URL}/api/tarot/pdf",
                      json={'type': tp, 'question': question, 'domaine': 'general',
                            'prenom': 'TEST_Camille', 'data': data}, timeout=120)
    print(f"pdf {tp} took {time.time()-t:.1f}s size={len(r.content)}")
    return r


def test_pdf_marseille(marseille):
    r = _pdf('marseille', marseille['data'])
    assert r.status_code == 200, r.text[:300]
    assert r.headers['content-type'].startswith('application/pdf')
    assert r.content.startswith(b'%PDF-1.4')
    assert 500_000 < len(r.content) < 8_000_000


def test_pdf_celtique(celtique):
    r = _pdf('celtique', celtique['data'])
    assert r.status_code == 200, r.text[:300]
    assert r.headers['content-type'].startswith('application/pdf')
    assert r.content.startswith(b'%PDF-1.4')
    assert len(r.content) > 500_000


def test_pdf_empty_data():
    r = requests.post(f"{BASE_URL}/api/tarot/pdf", json={'type': 'marseille', 'data': {}}, timeout=30)
    assert r.status_code == 400
    assert 'Données du tirage manquantes' in r.json()['detail']


def test_pdf_no_cards():
    r = requests.post(f"{BASE_URL}/api/tarot/pdf", json={'type': 'celtique', 'data': {'cartes': []}}, timeout=30)
    assert r.status_code == 400


def test_pdf_special_chars_question(marseille):
    # Question avec caractères XML (<, &) — ReportLab Paragraph peut crasher
    r = _pdf('marseille', marseille['data'], question='Amour & travail <vraiment> ?')
    assert r.status_code == 200, r.text[:300]
