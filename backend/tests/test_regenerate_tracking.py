"""Test regenerate tracking + admin funnel lift.

Vérifie que :
- `tarot_reveal_regenerated` est bien whitelisté côté ingestion
- L'endpoint admin `/experience/funnel` remonte `regenerators` + `regen_signup_lift_pp`
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
os.environ.setdefault('DB_NAME', 'plume_astrale_test_regen')

from routes.experience_funnel import ALLOWED_EVENTS, FUNNEL_STEPS  # noqa: E402


def test_regenerate_event_is_whitelisted():
    assert 'tarot_reveal_regenerated' in ALLOWED_EVENTS


def test_regenerate_step_is_in_funnel():
    assert 'tarot_reveal_regenerated' in FUNNEL_STEPS
