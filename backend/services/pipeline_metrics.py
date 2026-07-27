"""
pipeline_metrics — Tracker léger d'événements pipeline pour surveiller la santé
en production (fallbacks GPT vs API v3, timeouts, taux d'erreur).

Écriture append-only dans `/app/backend/logs/pipeline_events.jsonl` — file thread-safe,
rotation manuelle (le fichier peut être archivé/wipé sans risque). Chaque ligne est
un JSON standalone consommable par jq / pandas / dashboard admin.

Utilisation :
    from services.pipeline_metrics import track_pipeline_event
    track_pipeline_event('natal_pdf_generated', source='gpt', tier='ultra', pages=20)
"""
from __future__ import annotations
import json
import logging
import os
import threading
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

_LOG_DIR = '/app/backend/logs'
_LOG_FILE = os.path.join(_LOG_DIR, 'pipeline_events.jsonl')
_LOCK = threading.Lock()

os.makedirs(_LOG_DIR, exist_ok=True)


def track_pipeline_event(event_name: str, **labels: Any) -> None:
    """Log un événement pipeline structuré (JSONL, append-only, thread-safe).

    Args:
        event_name : ex. 'natal_pdf_generated', 'chat_stream_started', etc.
        **labels   : n'importe quels labels sérialisables (source, tier, pages...).

    Ne raise JAMAIS — si le fichier est indisponible, on log via logger.warning
    et on continue silencieusement pour ne pas bloquer un flow métier.
    """
    entry = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'event': event_name,
        **{k: v for k, v in labels.items() if v is not None},
    }
    line = json.dumps(entry, ensure_ascii=False) + '\n'
    try:
        with _LOCK:
            with open(_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(line)
    except Exception as e:
        logger.warning(f'[pipeline_metrics] append failed: {e} | entry={entry}')


def read_recent_events(event_name: str = None, limit: int = 500) -> list:
    """Retourne les N derniers événements (filtrable par nom) pour le dashboard admin."""
    if not os.path.exists(_LOG_FILE):
        return []
    try:
        with _LOCK:
            with open(_LOG_FILE, 'r', encoding='utf-8') as f:
                # tail-N : lire tout (le fichier est petit) puis filtrer + slicer
                lines = f.readlines()[-max(limit * 3, 500):]
        events = []
        for line in reversed(lines):
            try:
                obj = json.loads(line)
                if not event_name or obj.get('event') == event_name:
                    events.append(obj)
                    if len(events) >= limit:
                        break
            except Exception:
                continue
        return events
    except Exception as e:
        logger.warning(f'[pipeline_metrics] read failed: {e}')
        return []


def aggregate_by_label(event_name: str, label_key: str = 'source', limit: int = 5000) -> dict:
    """Retourne un dict { label_value: count } pour un event donné.

    Utilisé par le dashboard admin pour afficher les proportions
    (ex : gpt=87%, gpt_partial=8%, api_v3_only=4%, cache=1%).
    """
    events = read_recent_events(event_name=event_name, limit=limit)
    counts: dict = {}
    for e in events:
        v = str(e.get(label_key) or 'unknown')
        counts[v] = counts.get(v, 0) + 1
    return counts
