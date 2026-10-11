"""Contrôles de cohérence entre une session Stripe payée et la transaction enregistrée côté serveur.

La transaction en base (créée au checkout avec le prix calculé serveur) est la source de vérité :
on ne livre un produit que si Stripe confirme un paiement du bon montant, dans la bonne devise.
"""
from typing import Any, Optional, Tuple

PAID_STATUSES = ('paid', 'no_payment_required')


def verify_session_matches_transaction(
    session: dict, tx: Optional[dict]
) -> Tuple[bool, str]:
    """Retourne (ok, raison). `session` = objet checkout.session Stripe, `tx` = ligne payment_transactions."""
    if not tx:
        return False, 'transaction introuvable'
    if session.get('payment_status') not in PAID_STATUSES:
        return False, f"paiement non confirmé ({session.get('payment_status')})"

    amount = float(tx.get('amount') or 0)
    # checkout.py tronque (int) alors que d'autres chemins arrondissent : on accepte les deux.
    expected_cents = {int(amount * 100), round(amount * 100)}
    paid_cents = session.get('amount_total')
    if paid_cents is None or int(paid_cents) not in expected_cents:
        return False, f'montant inattendu (Stripe={paid_cents}, attendu={sorted(expected_cents)})'

    expected_currency = str(tx.get('currency') or '').lower()
    paid_currency = str(session.get('currency') or '').lower()
    if expected_currency and paid_currency != expected_currency:
        return False, f'devise inattendue (Stripe={paid_currency}, attendu={expected_currency})'

    return True, 'ok'


def session_to_dict(data_obj: Any) -> dict:
    return data_obj if isinstance(data_obj, dict) else data_obj.to_dict()
