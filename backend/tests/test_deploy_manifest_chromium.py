"""Deployment manifest — Chromium + fonts pour book_engine_v2 print (Feb 2026)

Contexte : le PDF Thème Natal via book_engine_v2 utilise Chromium en subprocess
(`--print-to-pdf`) pour rendre le HTML print blanc. En prod le pod runtime
n'avait NI Chromium NI WeasyPrint installés → fallback natal_pdf_v2 dark à
chaque génération. Bug client "j'ai reçu l'ancien visuel malgré le prix".

Ces tests garantissent qu'un futur agent ne supprime pas les deps critiques.
"""
from pathlib import Path

MANIFEST = Path('/app/.emergent/system_deps.txt')


def test_manifest_exists():
    assert MANIFEST.exists(), '.emergent/system_deps.txt supprimé — build prod cassé'


def test_manifest_installs_chromium():
    """book_engine_v2 renderer utilise Chromium en subprocess : must be present."""
    src = MANIFEST.read_text()
    assert 'chromium' in src, (
        'chromium absent de .emergent/system_deps.txt — le renderer book_engine_v2 '
        'ne trouvera pas de binaire en prod et fallback en dark.'
    )


def test_manifest_installs_fonts_for_chromium_rendering():
    """Chromium sans fonts liberation → fallback ugly system font → PDF crade."""
    src = MANIFEST.read_text()
    assert 'fonts-liberation' in src, 'fonts-liberation absent — rendu Cormorant fallback ugly'
    # Fonts noto pour glyphes Unicode (astro glyphes ♎♏♓)
    assert 'fonts-noto' in src, 'fonts-noto absent — glyphes astro possiblement carrés'


def test_renderer_still_uses_chromium_binaries():
    """Anti-régression : le renderer cherche bien 'chromium' via shutil.which."""
    renderer_src = Path('/app/backend/services/book_engine_v2/renderer.py').read_text()
    assert "'chromium'" in renderer_src, (
        "Le renderer ne cherche plus 'chromium' — désynchronisation avec system_deps.txt"
    )
    assert '_find_chromium' in renderer_src
    # Le flag --no-sandbox est requis pour tourner en pod K8s (pas de user namespace)
    assert '--no-sandbox' in renderer_src, (
        "Flag --no-sandbox retiré : Chromium ne pourra pas démarrer dans le pod prod."
    )
