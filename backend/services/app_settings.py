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


# ═══════════════════════════════════════════════════════════════
# Compteurs de coût LLM (par mois, par usage)
# ═══════════════════════════════════════════════════════════════
# Modèle de coût simple : on compte les appels réussis par mois et par usage
# (report_ai, chat_support, ...). Estimation coût en € : nb_calls × tarif_moyen.
# Le tarif est un ordre de grandeur — GPT-5.4 via Emergent LLM ≈ 0.008 €/appel
# report (long), 0.001 €/appel chat (court). Ajustable via `LLM_COST_TARIFF`.

LLM_COST_TARIFF = {
    'report_ai': 0.008,   # ~1800 tokens output, appel long
    'chat_support': 0.001,
    # Sora 2 video generation — coût par seconde de vidéo
    'sora_2': 0.10,       # sora-2 : $0.10/s
    'sora_2_pro': 0.30,   # sora-2-pro : $0.30/s
    # OpenAI TTS — coût par 1000 caractères
    'tts': 0.015,         # tts-1 : $15/M chars
    'default': 0.003,
}


def _current_month() -> str:
    """YYYY-MM UTC."""
    return datetime.now(timezone.utc).strftime('%Y-%m')


def record_llm_call(usage: str, tokens_estimate: int = 0, units: float = 0.0) -> None:
    """Incrémente le compteur pour le mois en cours.

    usage ∈ {'report_ai', 'chat_support', 'sora_2', 'sora_2_pro', 'tts', ...}.
    - tokens_estimate : nb tokens output (informatif, non facturé ici).
    - units : quantité facturable (sec pour Sora, chars pour TTS, ignoré pour LLM
      texte où le coût est calculé par appel via `LLM_COST_TARIFF[usage]`).
    Ne lève jamais.
    """
    try:
        with _LOCK:
            data = _load()
            counters = data.get('llm_usage') or {}
            month = _current_month()
            month_data = counters.get(month) or {}
            u = month_data.get(usage) or {'calls': 0, 'tokens': 0, 'units': 0.0}
            u['calls'] = int(u.get('calls', 0)) + 1
            u['tokens'] = int(u.get('tokens', 0)) + int(tokens_estimate or 0)
            u['units'] = float(u.get('units', 0.0)) + float(units or 0.0)
            month_data[usage] = u
            counters[month] = month_data
            # Cap à 12 mois
            if len(counters) > 12:
                for k in sorted(counters.keys())[:len(counters) - 12]:
                    counters.pop(k, None)
            data['llm_usage'] = counters
            _CACHE.update(data)  # type: ignore
            _save()
    except Exception as e:
        logger.warning(f'[app_settings] record_llm_call fail: {e}')


def get_llm_usage(months: int = 3) -> Dict[str, Any]:
    """Retourne les stats LLM des N derniers mois + total mois en cours.

    Structure :
    {
        'current_month': '2026-08',
        'current': {'total_calls': 42, 'total_cost_eur': 0.336, 'by_usage': {...}},
        'history': [{month:'2026-06', total_calls:..., total_cost_eur:...}, ...],
        'budget_eur': 30.0,
        'tariff': LLM_COST_TARIFF,
    }
    """
    with _LOCK:
        counters = (_load().get('llm_usage') or {}).copy()
    all_months = sorted(counters.keys())
    current_month = _current_month()

    def _month_summary(m: str) -> Dict[str, Any]:
        md = counters.get(m) or {}
        by_usage = {}
        total_calls = 0
        total_cost = 0.0
        for u, stats in md.items():
            calls = int(stats.get('calls', 0))
            units = float(stats.get('units', 0.0))
            tariff = LLM_COST_TARIFF.get(u, LLM_COST_TARIFF['default'])
            # Sora / TTS : coût = tariff × units (secondes ou milliers de chars).
            # LLM texte : coût = tariff × calls (1 tariff = 1 appel moyen).
            if u in ('sora_2', 'sora_2_pro'):
                cost = round(units * tariff, 4)
            elif u == 'tts':
                cost = round((units / 1000.0) * tariff, 4)  # tariff = $ per 1k chars
            else:
                cost = round(calls * tariff, 4)
            by_usage[u] = {
                'calls': calls, 'units': units,
                'cost_eur': cost, 'tariff_eur': tariff,
            }
            total_calls += calls
            total_cost += cost
        return {
            'month': m,
            'total_calls': total_calls,
            'total_cost_eur': round(total_cost, 4),
            'by_usage': by_usage,
        }

    history = [_month_summary(m) for m in all_months[-months:] if m != current_month]
    current = _month_summary(current_month)
    budget = float(_load().get('llm_budget_eur') or 30.0)

    return {
        'current_month': current_month,
        'current': current,
        'history': history,
        'budget_eur': budget,
        'tariff': LLM_COST_TARIFF,
    }


def set_llm_budget(budget_eur: float) -> None:
    with _LOCK:
        data = _load()
        data['llm_budget_eur'] = max(0.0, float(budget_eur))
        _CACHE.update(data)  # type: ignore
        _save()
