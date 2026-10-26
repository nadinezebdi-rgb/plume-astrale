# Audit RGPD — Logs applicatifs (2026-02-25)

## Résumé exécutif

| Métrique | Avant | Après |
|---|---|---|
| Emails en clair dans les logs | **45** | 0 |
| Noms en clair | 0 | 0 |
| Dates de naissance en clair | 0 | 0 |
| Numéros de téléphone en clair | 0 | 0 |
| Adresses complètes | 1 (country_code uniquement, non PII) | 1 |
| **TOTAL fuites PII** | **46** | **1 (non critique)** |

## Fix mis en place

### Nouveau helper `services/log_redact.py`

Quatre fonctions pures et testées (31/31 tests passent) :

```python
redact_email('alice.wonder@gmail.com') → 'a***@gmail.com'
redact_name('Alice Wonder')            → 'A*** W***'
redact_phone('+33612345678')           → '+33*******78'
redact_birth_date('1990-06-15')        → '1990-**-**'
```

Garde-fou : les entrées vides/invalides retournent `<empty>` / `<invalid>` / `<redacted>`, jamais la PII brute.

### 31 fichiers patchés

Les 45 lignes `logger.X(f'...{email}...')` ont été transformées en `logger.X(f'...{redact_email(email)}...')`. L'import `from services.log_redact import redact_email` a été ajouté automatiquement.

Fichiers touchés : voir `/app/docs/audit/rgpd_pii_logs_2026_02.txt` pour la liste complète.

### Avantages

- **Diagnostic préservé** : on garde le domaine SMTP (`@gmail.com`) pour debugguer les bounces, et la première lettre pour distinguer plusieurs users dans un même thread de logs.
- **Zéro perte de traçabilité** côté session (session_id, token_id reste intact).
- **Conforme GDPR Article 5(1)(c)** : minimisation des données traitées.

## Reste à faire (hors scope ce lot)

- **1 ligne non critique restante** : `lulu_client.py:93` logue le `country_code` d'une adresse (ex. `FR`, `US`). C'est une donnée géographique agrégée, pas une PII identifiante. OK à garder pour le monitoring Lulu Print API.
- **Audit des services externes** : vérifier que Resend, Stripe, Sentry (si utilisé) ne reçoivent pas des emails en clair dans les tags/breadcrumbs. À inspecter dans un prochain lot.
- **Rotation des logs** : les logs supervisor sous `/var/log/supervisor/backend.*.log` contiennent potentiellement l'historique AVANT ce patch. Vérifier la rotation et la rétention (90 jours max recommandé RGPD).
- **DPIA formelle** : documenter l'analyse d'impact (template CNIL) pour les 3 traitements principaux : signup, génération PDF, envois Resend.

## Commande de vérification continue

```bash
# À ajouter dans la CI pour empêcher la régression :
cd /app/backend && python3 -c "
import re
from pathlib import Path
pattern = re.compile(r'(logger|logging)\.\w+.*?\{(payload\.)?(email|user_email|to_email|admin_email|recipient_email)[\}:!]')
hits = []
for py in Path('.').rglob('*.py'):
    if '__pycache__' in str(py) or '/tests/' in str(py) or 'log_redact' in py.name:
        continue
    for i, l in enumerate(py.read_text().splitlines(), 1):
        if pattern.search(l) and 'redact_email' not in l:
            hits.append(f'{py}:{i}')
if hits:
    print('PII leaks detected:', hits)
    exit(1)
print('OK: no email leak')
"
```
