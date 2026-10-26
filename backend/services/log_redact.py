"""log_redact — Petits helpers pour éviter les PII en clair dans les logs.

Utilisation :

    from services.log_redact import redact_email, redact_name

    logger.info(f'[kabbale] PDF envoyé à {redact_email(email)}')
    # → [kabbale] PDF envoyé à n***@plume-astrale.fr

Audit RGPD (2026-02-25) : plusieurs loggers logaient `payload.email` ou
`first_name` en clair. On ne supprime pas la traçabilité, on masque juste la
PII identifiable.
"""
from __future__ import annotations

__all__ = ['redact_email', 'redact_name', 'redact_phone', 'redact_birth_date']


def redact_email(email: str) -> str:
    """`alice.wonder@gmail.com` → `a***@gmail.com`

    Garde le 1er caractère du local-part + le domaine complet (utile pour
    diagnostiquer un bounce côté SMTP). Si l'input est vide/invalide, renvoie
    `<empty>` ou `<invalid>` pour que le log reste lisible.
    """
    if not email or not isinstance(email, str):
        return '<empty>'
    e = email.strip().lower()
    if '@' not in e:
        return '<invalid>'
    local, _, domain = e.partition('@')
    if not local or not domain:
        return '<invalid>'
    head = local[0]
    return f'{head}***@{domain}'


def redact_name(name: str) -> str:
    """`Alice` → `A***` ; `Alice Wonder` → `A*** W***`.

    Garde la première lettre de chaque mot (utile pour distinguer plusieurs
    users dans un même log) tout en masquant la PII.
    """
    if not name or not isinstance(name, str):
        return '<empty>'
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return '<empty>'
    return ' '.join(f'{p[0].upper()}***' for p in parts)


def redact_phone(phone: str) -> str:
    """`+33612345678` → `+33******78` (garde les 3 premiers + 2 derniers)."""
    if not phone or not isinstance(phone, str):
        return '<empty>'
    p = ''.join(c for c in phone if c.isdigit() or c == '+')
    if len(p) < 6:
        return '<redacted>'
    return f'{p[:3]}{"*" * (len(p) - 5)}{p[-2:]}'


def redact_birth_date(d: str) -> str:
    """`1990-06-15` → `1990-**-**` (garde l'année pour les stats, masque le jour)."""
    if not d or not isinstance(d, str):
        return '<empty>'
    s = d.strip()[:10]
    if len(s) >= 4 and s[:4].isdigit():
        return f'{s[:4]}-**-**'
    return '<redacted>'
