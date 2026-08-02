"""
App-level settings persistes sur disque (survive au restart supervisor).

Utilise pour :
  - forced_j30_variant : bascule 100% sur une variante A/B J+30
  - alerts_history : liste des alertes envoyees (cap 30)
"""
from __future__ import annotations
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from threading import Lock

logger = logging.getLogger(__name__)

_STATE_DIR = '/app/backend/.state'
_STATE_FILE = os.path.join(_STATE_DIR, 'app_settings.json')
_LOCK = Lock()
_CACHE: Optional[Dict[str, Any]] = None


def _ensure_dir() -> None:
    try:
        os.makedirs(_STATE_DIR, exist_ok=True)
    except Exception as e:
        logger.warning(f'[app_settings] mkdir fail: {e}')


def _load() -> Dict[str, Any]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    _ensure_dir()
    try:
        with open(_STATE_FILE, 'r', encoding='utf-8') as f:
            _CACHE = json.load(f)
    except FileNotFoundError:
        _CACHE = {}
    except Exception as e:
        logger.warning(f'[app_settings] load fail: {e}')
        _CACHE = {}
    return _CACHE


def _save() -> None:
    _ensure_dir()
    try:
        with open(_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(_CACHE or {}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f'[app_settings] save fail: {e}')


def get_setting(key: str, default: Any = None) -> Any:
    with _LOCK:
        return _load().get(key, default)


def set_setting(key: str, value: Any) -> None:
    with _LOCK:
        _load()
        _CACHE[key] = value  # type: ignore
        _save()


# ═══════════════════════════════════════════════════════════════
# Historique des alertes envoyees
# ═══════════════════════════════════════════════════════════════

def log_alert(kind: str, title: str, details: Optional[str] = None,
              channels: Optional[List[str]] = None) -> None:
    """Append une alerte dans l'historique (cap 30 entrees)."""
    with _LOCK:
        data = _load()
        history = data.get('alerts_history') or []
        history.append({
            'kind': kind,
            'title': title[:200],
            'details': (details or '')[:400],
            'channels': channels or [],
            'at': datetime.now(timezone.utc).isoformat(),
        })
        data['alerts_history'] = history[-30:]
        _CACHE.update(data)  # type: ignore
        _save()


def get_alerts_history() -> List[Dict[str, Any]]:
    with _LOCK:
        return list(_load().get('alerts_history') or [])
