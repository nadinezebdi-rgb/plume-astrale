"""Génère le PDF échantillon public du Thème Natal — SANS filigrane.

Depuis Feb 2026 (demande fondatrice), l'aperçu public ne porte plus de filigrane
« EXTRAIT » ni de bandeau bas « non commercialisable ». Le PDF produit est le
Thème Natal personnalisé configuré, livré tel qu'il sera dans l'édition payante.

Usage: python3 -m backend.scripts.add_sample_watermark
Sortie: /app/frontend/public/demos/theme-natal-sample.pdf

Note : le nom du script est conservé pour éviter de casser les hooks CI/CD,
mais sa logique a changé — il n'ajoute plus de filigrane.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT_PATH = Path('/app/frontend/public/demos/theme-natal-sample.pdf')


def regenerate_source_pdf() -> bytes:
    """Regénère le PDF échantillon avec le moteur V2 configuré."""
    os.environ['USE_V2_NATAL_ENGINE'] = '1'
    from routes.admin_preview_v3 import _demo_data  # noqa: WPS433
    from services.natal_pdf_adapter import generate_manuscrit_pdf  # noqa: WPS433

    d = _demo_data('Amélie')
    return generate_manuscrit_pdf(
        user_data=d['user_data'],
        planets_data=d['planets_data'],
        aspects_raw=d['aspects_raw'],
        house_cusps_raw=d['cusps_raw'],
    )


def main() -> None:
    print('[sample] régénération du PDF échantillon Thème Natal (sans filigrane)…')
    pdf = regenerate_source_pdf()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(pdf)
    print(f'[sample] écrit {len(pdf):,} bytes → {OUT_PATH}')


if __name__ == '__main__':
    main()
