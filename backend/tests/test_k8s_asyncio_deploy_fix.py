"""Regression test — K8s deploy fix (Feb 2026)

Bug : la génération du daily horoscope (12 PDFs ReportLab séquentiels) bloquait
l'event loop asyncio pendant ~60-90s. La liveness probe `/health` de Kubernetes
timeoutait → le pod redémarrait en boucle → deploy KO.

Fix : wrapper les appels CPU-bound `build_pdf_for_signe` dans `asyncio.to_thread`
pour offloader le thread pool et garder l'event loop réactif.

Ces tests garantissent qu'un futur refactor ne réintroduira PAS le blocage.
"""
import ast
import os
import sys

sys.path.insert(0, '/app/backend')
os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
os.environ.setdefault('DB_NAME', 'test_db')

BUILD_SCRIPT = '/app/backend/scripts/build_daily_horoscope.py'


def _load_module_ast():
    with open(BUILD_SCRIPT) as f:
        return ast.parse(f.read())


def test_build_pdf_for_signe_is_wrapped_in_to_thread():
    """
    `build_pdf_for_signe` étant synchrone + CPU/IO bloquant (ReportLab + HTTP),
    tous ses appels DOIVENT être wrapped dans `asyncio.to_thread` sinon on
    reproduit le crash liveness probe K8s.
    """
    src = open(BUILD_SCRIPT).read()

    # Compte total d'appels bruts à build_pdf_for_signe (dans le code, pas les imports/comments)
    tree = ast.parse(src)
    all_calls = []
    to_thread_wrapped = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Détecte build_pdf_for_signe(...)
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id == 'build_pdf_for_signe':
                all_calls.append(node)
            elif (
                isinstance(fn, ast.Attribute)
                and isinstance(fn.value, ast.Name)
                and fn.value.id == 'asyncio'
                and fn.attr == 'to_thread'
            ):
                # asyncio.to_thread(build_pdf_for_signe, ...)
                if node.args and isinstance(node.args[0], ast.Name):
                    if node.args[0].id == 'build_pdf_for_signe':
                        to_thread_wrapped.append(node)

    # `all_calls` compte aussi ceux passés comme argument à asyncio.to_thread
    # (build_pdf_for_signe en position ast.Name). On veut vérifier qu'aucun
    # appel direct DIRECT au sens `build_pdf_for_signe(...)` n'existe.
    direct_calls = [
        c for c in all_calls
        if not any(
            c is (parent.args[0] if parent.args else None)
            for parent in to_thread_wrapped
        )
    ]

    # Filtrage manuel : un ast.Call direct est un vrai appel bloquant.
    # Tous les usages actuels de la fonction doivent être via to_thread.
    assert len(direct_calls) == 0, (
        f'{len(direct_calls)} appel(s) direct(s) à build_pdf_for_signe détecté(s). '
        f'Cela va rebloquer l\'event loop et faire crasher /health en prod. '
        f'Utiliser: await asyncio.to_thread(build_pdf_for_signe, ...)'
    )
    assert len(to_thread_wrapped) >= 2, (
        f'Attendu au moins 2 appels wrappés via asyncio.to_thread '
        f'(fallback + branche enrichie), trouvé {len(to_thread_wrapped)}'
    )


def test_deploy_fix_comment_present():
    """Un commentaire explicatif doit être présent au-dessus de l'appel critique
    pour éviter qu'un futur agent ne le supprime par mégarde."""
    src = open(BUILD_SCRIPT).read()
    assert 'DEPLOY FIX' in src, (
        "Commentaire 'DEPLOY FIX' manquant. Il documente pourquoi asyncio.to_thread "
        "est requis (liveness probe K8s)."
    )
    assert 'liveness probe' in src.lower() or 'to_thread' in src, (
        'Justification technique manquante dans le commentaire.'
    )
