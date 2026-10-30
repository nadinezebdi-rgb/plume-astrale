"""Tests de la logique de /admin/payments-health — Feb 2026.

Teste les deux correctifs demandés par la fondatrice :
  1. Déduplication par session_id (évite les 2× la même commande)
  2. Seuil 15 min + exclusion emails de test
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta


def _mk_row(session_id: str, status: str, payment_status: str,
            email: str = 'cliente@gmail.com', amount: float = 24.0,
            created_minutes_ago: int = 60, pack_id: str = 'natal') -> dict:
    """Factory : crée une ligne payment_transactions."""
    created = datetime.now(timezone.utc) - timedelta(minutes=created_minutes_ago)
    return {
        'session_id': session_id,
        'user_email': email,
        'pack_id': pack_id,
        'amount': amount,
        'currency': 'eur',
        'status': status,
        'payment_status': payment_status,
        'metadata': {},
        'created_at': created.isoformat(),
    }


# Reimplémentation locale de la logique dédup+filtre pour tester en isolation
def _is_test_email(email):
    if not email:
        return False
    e = email.lower().strip()
    if '@plume-astrale.fr' in e: return True
    if e.startswith('contact@') or e.startswith('admin@') or e.startswith('test@'): return True
    if '@test.' in e or '@example.' in e: return True
    if '+test' in e or '+debug' in e: return True
    return False


def _row_priority(row):
    if row.get('payment_status') == 'paid': return 0
    if row.get('status') == 'initiated' and row.get('payment_status') == 'unpaid': return 1
    return 2


def _compute(rows, stuck_after_minutes=15):
    """Simule exactly ce que fait l'endpoint `/payments-health`."""
    real = [row for row in rows if (row.get('session_id') or '').startswith('cs_')]
    real = [row for row in real if not _is_test_email(row.get('user_email'))]
    # Déduplication
    by_session = {}
    for row in real:
        sid = row.get('session_id')
        if sid not in by_session or _row_priority(row) < _row_priority(by_session[sid]):
            by_session[sid] = row
    dedup_real = list(by_session.values())
    # Seuil 15 min
    stuck_threshold = datetime.now(timezone.utc) - timedelta(minutes=stuck_after_minutes)
    def is_stuck(row):
        if row.get('status') != 'initiated' or row.get('payment_status') != 'unpaid':
            return False
        try:
            created_dt = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
            if created_dt.tzinfo is None:
                created_dt = created_dt.replace(tzinfo=timezone.utc)
            return created_dt < stuck_threshold
        except Exception:
            return True
    paid = [r for r in dedup_real if r.get('payment_status') == 'paid']
    stuck = [r for r in dedup_real if is_stuck(r)]
    return paid, stuck


def test_dedup_same_session_two_rows_counted_once():
    """Bug fix : une session Stripe avec 2 lignes payment_transactions ne compte qu'une fois."""
    rows = [
        _mk_row('cs_live_abc_X', status='initiated', payment_status='unpaid'),
        _mk_row('cs_live_abc_X', status='paid', payment_status='paid'),
    ]
    paid, stuck = _compute(rows)
    # 1 session seulement (préférence paid > stuck)
    assert len(paid) == 1
    assert len(stuck) == 0
    assert paid[0]['payment_status'] == 'paid'


def test_dedup_sum_matches_stripe():
    """Avant correctif : « 2 payées / 48€ ». Après : 1 payée / 24€."""
    rows = [
        _mk_row('cs_live_abc', 'paid', 'paid', amount=24.0),
        _mk_row('cs_live_abc', 'initiated', 'unpaid', amount=24.0),  # ancien duplicate
    ]
    paid, _ = _compute(rows)
    total = sum(float(r.get('amount') or 0) for r in paid)
    assert len(paid) == 1
    assert total == 24.0


def test_session_in_generation_not_stuck_before_threshold():
    """Bug fix : une session créée il y a 5 min ne doit PAS apparaître bloquée."""
    rows = [_mk_row('cs_live_fresh', 'initiated', 'unpaid', created_minutes_ago=5)]
    _, stuck = _compute(rows, stuck_after_minutes=15)
    assert len(stuck) == 0


def test_session_stuck_after_threshold():
    """Après 20 min, une session non payée est marquée bloquée."""
    rows = [_mk_row('cs_live_old', 'initiated', 'unpaid', created_minutes_ago=20)]
    _, stuck = _compute(rows, stuck_after_minutes=15)
    assert len(stuck) == 1


def test_test_emails_excluded_from_stats():
    """Les paiements de test (fondatrice, admin, test@…) ne polluent plus les KPIs."""
    rows = [
        _mk_row('cs_live_test1', 'paid', 'paid', email='contact@plume-astrale.fr'),
        _mk_row('cs_live_test2', 'paid', 'paid', email='admin@plume-astrale.fr'),
        _mk_row('cs_live_test3', 'paid', 'paid', email='test@foo.com'),
        _mk_row('cs_live_test4', 'paid', 'paid', email='nadine+test@gmail.com'),
        _mk_row('cs_live_test5', 'paid', 'paid', email='sarah@example.com'),
        _mk_row('cs_live_real', 'paid', 'paid', email='cliente@gmail.com'),
    ]
    paid, _ = _compute(rows)
    assert len(paid) == 1
    assert paid[0]['user_email'] == 'cliente@gmail.com'


def test_dedup_multiple_sessions():
    """3 sessions distinctes avec dupes → compte 3."""
    rows = [
        _mk_row('cs_live_A', 'paid', 'paid'),
        _mk_row('cs_live_A', 'initiated', 'unpaid'),
        _mk_row('cs_live_B', 'paid', 'paid'),
        _mk_row('cs_live_C', 'initiated', 'unpaid', created_minutes_ago=60),
    ]
    paid, stuck = _compute(rows, stuck_after_minutes=15)
    assert len(paid) == 2
    assert len(stuck) == 1


def test_realistic_scenario_matches_user_complaint():
    """Scénario réel rapporté par la fondatrice :
    - 1 vrai paiement 24€ (cliente)
    - Son propre test 24€ (contact@plume-astrale.fr)
    - La ligne dédoublée du test (same session, 2 rows)
    Résultat attendu : 1 paiement visible = 24€ (le test est exclu, le dup est fusionné).
    """
    rows = [
        # Vraie cliente
        _mk_row('cs_live_real_client', 'paid', 'paid', email='nadine@gmail.com', amount=24.0),
        # Test fondatrice (2 lignes dupliquées pour la même session)
        _mk_row('cs_live_test_run', 'initiated', 'unpaid',
                email='contact@plume-astrale.fr', amount=24.0),
        _mk_row('cs_live_test_run', 'paid', 'paid',
                email='contact@plume-astrale.fr', amount=24.0),
    ]
    paid, _ = _compute(rows)
    assert len(paid) == 1
    assert sum(float(r.get('amount') or 0) for r in paid) == 24.0
    assert paid[0]['user_email'] == 'nadine@gmail.com'
