"""Regression test — Tunnel de conversion /experience -> /inscription (Feb 2026)

Contexte financier (analyse investisseur) :
  Le tunnel Preview V2 immersif -> inscription cassait la narration parce que
  /inscription arrivait vierge (form technique apres 90s d'experience emotionnelle).
  Perte de tension commerciale -> drop-off a l'etape la plus critique du funnel.

Fix : Register.js lit intent + card + welcome des query params ET du sessionStorage,
      affiche un bandeau de rappel visuel ("Votre carte / Votre intention / 20 credits offerts")
      et propage ces valeurs vers /mon-accueil apres inscription (survit a sessionStorage flushe).

Ces tests garantissent la non-regression sur le contrat implicite :
  - Register.js importe INTENT_CONFIG, readIntent, readDrawnCard, readUtm
  - Register.js expose les data-testid utilises par le funnel : register-experience-recall,
    register-recall-card, register-recall-intent, register-recall-gift
  - Register.js propage intent + exp_card dans la redirection vers /mon-accueil
  - Le miroir EXP_CARDS de Register reste synchronise avec ExperienceRoot.CARDS
"""
import re
from pathlib import Path

REGISTER = Path('/app/frontend/src/pages/Register.js')
EXPROOT = Path('/app/frontend/src/experience/ExperienceRoot.jsx')
INTENT_CONFIG = Path('/app/frontend/src/experience/intentConfig.js')


def test_register_imports_experience_context_helpers():
    src = REGISTER.read_text()
    for helper in ('INTENT_CONFIG', 'readIntent', 'readDrawnCard', 'readUtm'):
        assert helper in src, (
            f"Register.js n'importe pas '{helper}' — le tunnel de conversion "
            f"ne peut plus rappeler le contexte de /experience."
        )
    assert "from '@/experience/intentConfig'" in src, (
        "Import depuis '@/experience/intentConfig' manquant dans Register.js"
    )


def test_register_experience_recall_testids_present():
    src = REGISTER.read_text()
    required = [
        'register-experience-recall',
        'register-recall-card',
        'register-recall-intent',
        'register-recall-gift',
    ]
    missing = [t for t in required if t not in src]
    assert not missing, (
        f'data-testid manquants dans Register.js: {missing}. '
        f'Ils sont utilises par les tests Playwright du tunnel de conversion.'
    )


def test_register_propagates_intent_and_card_post_signup():
    src = REGISTER.read_text()
    assert "navigate(`/mon-accueil?" in src, (
        "Register.js ne construit plus dynamiquement l'URL /mon-accueil — "
        "l'intent et la carte ne survivront pas a un sessionStorage flushe."
    )
    assert "p.set('intent'" in src, "Propagation de 'intent' absente"
    assert "p.set('exp_card'" in src, "Propagation de 'exp_card' absente"
    assert 'readUtm()' in src, "UTM non propages — perte d'attribution Meta Ads"


def test_exp_cards_mirror_stays_in_sync_with_experience_root():
    reg_src = REGISTER.read_text()
    exp_src = EXPROOT.read_text()

    exp_ids = set(re.findall(r"\{\s*id:\s*'([^']+)'", exp_src))
    # Isole les IDs déclarés dans le miroir Register.EXP_CARDS
    m = re.search(r'const\s+EXP_CARDS\s*=\s*\{(.+?)\n\};', reg_src, re.DOTALL)
    assert m, 'EXP_CARDS non trouvee dans Register.js'
    reg_ids = set(re.findall(r'\b(\w+):\s*\{\s*glyph', m.group(1)))

    exp_card_ids = {'heart', 'moon', 'star'}
    assert exp_card_ids.issubset(exp_ids), (
        f"ExperienceRoot.CARDS ne contient plus les 3 cartes attendues: {exp_ids}"
    )
    assert exp_card_ids.issubset(reg_ids), (
        f"Register.EXP_CARDS ne contient plus les 3 cartes attendues: {reg_ids}. "
        f"Un user tirant une carte manquante verrait 'undefined' dans le bandeau."
    )


def test_intent_config_covers_all_experience_intents():
    intent_src = INTENT_CONFIG.read_text()
    exp_src = EXPROOT.read_text()

    exp_intents = set(re.findall(r"\{\s*id:\s*'(relationship|clarity|self_discovery|specific_question)'", exp_src))
    assert exp_intents == {'relationship', 'clarity', 'self_discovery', 'specific_question'}, (
        f"ExperienceRoot.INTENTS a change — attendu 4 intents, trouve: {exp_intents}"
    )
    for it in exp_intents:
        assert re.search(rf"{it}:\s*\{{[^}}]*splashTitle", intent_src), (
            f"INTENT_CONFIG.{it}.splashTitle manquant"
        )
        assert re.search(rf"{it}:\s*\{{(?:[^{{}}]|\{{[^}}]*\}})*primary", intent_src), (
            f"INTENT_CONFIG.{it}.primary manquant"
        )
