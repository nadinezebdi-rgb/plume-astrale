"""Analytics — Bloc 1 V3 (Feb 2026)
Tests statiques pour les 4 events manquants + guards perf mobile.
"""
from pathlib import Path

ANALYTICS = Path('/app/frontend/src/lib/analytics.js')
EXPROOT = Path('/app/frontend/src/experience/ExperienceRoot.jsx')
DEVICE = Path('/app/frontend/src/experience/hooks/useDeviceProfile.js')


def test_events_constants_added():
    src = ANALYTICS.read_text()
    for k, v in [
        ('EXP_SCENE1_COMPLETED', 'experience_scene_1_completed'),
        ('EXP_INTENT_VIEWED',     'intent_viewed'),
        ('EXP_TAROT_HOVERED',     'tarot_card_hovered'),
        ('EXP_SOURCE_CAPTURED',   'experience_source_captured'),
    ]:
        assert f"{k}:" in src and f"'{v}'" in src, f'EVENTS.{k} = "{v}" manquant'


def test_experienceroot_emits_new_events():
    src = EXPROOT.read_text()
    for token in (
        'EXP_SCENE1_COMPLETED',
        'EXP_INTENT_VIEWED',
        'EXP_TAROT_HOVERED',
        'EXP_SOURCE_CAPTURED',
    ):
        assert token in src, f'ExperienceRoot n\'émet pas {token}'
    # Le hover doit être débouncé (1× par card_id via ref)
    assert 'hoveredCardsRef' in src, 'Débounce hoveredCardsRef absent — flood analytics'
    # Le scene1_completed doit être guardé pour ne pas ré-émettre
    assert 'scenesTrackedRef' in src, 'Guard scenesTrackedRef absent — émissions répétées'


def test_source_captured_only_when_utm_present():
    """L'event ne doit être émis QUE si des UTM ont été capturés (évite le bruit)."""
    src = EXPROOT.read_text()
    # Cherche le bloc autour d'EXP_SOURCE_CAPTURED
    assert 'Object.keys(captured).length' in src, (
        "Guard 'Object.keys(captured).length > 0' absent — event émis même sans UTM."
    )


def test_device_profile_detects_savedata_and_slow_connection():
    src = DEVICE.read_text()
    assert 'saveData' in src, 'Détection navigator.connection.saveData absente'
    assert 'effectiveType' in src, 'Détection navigator.connection.effectiveType absente'
    # Force le fallback en présence de saveData / 2G-3G
    assert "'2g'" in src or "'3g'" in src, 'Slow-connection thresholds absents'
    assert 'finalReduced' in src or 'reducedMotion || saveData' in src, (
        'Force reducedMotion=true si data-saver absent'
    )
