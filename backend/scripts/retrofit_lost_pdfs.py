"""
RATTRAPAGE v2 — Renvoi automatique des PDFs / emails d'excuse pour tous les
clients bloqués par le bug SENDER_EMAIL=onboarding@resend.dev (avant le 01/02/2026).

Deux cas de figure gérés :

CAS A : produits Kabbale / Pack Karmique
────────────────────────────────────────
La transaction EST en DB avec les birth_data → on peut regénérer le PDF et
renvoyer l'email automatiquement. Idempotent : on saute si pdf_path ET email_sent_at
sont déjà positionnés.

CAS B : produits Numérologie / Karma / Fenêtre
──────────────────────────────────────────────
La transaction N'EST PAS en DB (bug .insert sans .execute) → on n'a pas les
données de naissance. On insère la tx manquante + on envoie un email d'excuse
demandant les infos au client.

Usage (depuis /app/backend) :
    python scripts/retrofit_lost_pdfs.py            # dry-run : liste les clients touches
    python scripts/retrofit_lost_pdfs.py --send     # execute (regenerations + emails)
    python scripts/retrofit_lost_pdfs.py --send --only kabbale,pack_karmique  # filtrer

⚠️ À lancer en PROD (Railway) : la clé Stripe locale est un placeholder Emergent.
"""
import asyncio
import os
import sys
from datetime import datetime, timezone

import httpx
import stripe

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

from services.supabase_client import get_admin_client  # noqa: E402

# Produits gérés par le rattrapage
# kind → (label FR, prix affichable, stratégie)
#   strategy = 'regenerate' : PDF/email regénérés depuis les données en DB
#   strategy = 'apology'    : email d'excuse demandant les infos manquantes
KINDS = {
    'kabbale_arbre_de_vie':    ('Ton Arbre de Vie Kabbalistique', '39€', 'regenerate'),
    'pack_karmique_kabbale':   ('Pack Karmique + Kabbale',        '89€', 'regenerate'),
    'compatibilite_ultime':    ('Compatibilité Ultime',           '29,99€', 'regenerate'),
    'numerologie_code':         ('Code Numérologique',             '19€', 'apology'),
    'karma_destin_analysis':    ('Analyse Karmique & Destinée',    '24€', 'apology'),
    'fenetre_rencontre_avancee':('Fenêtres de Rencontre Avancées', '29€', 'apology'),
}

APOLOGY_HTML = """
<div style="max-width:560px;margin:0 auto;font-family:Georgia,serif;color:#333;">
  <h2 style="color:#AA7C11;">✦ Plume Astrale — ton document t'attend</h2>
  <p>Bonjour{name_part},</p>
  <p>Tu as commandé <strong>{product}</strong> ({price}) sur plume-astrale.fr — et suite à un
  incident technique de notre côté, ton document ne t'a jamais été livré. Toutes nos excuses,
  sincèrement.</p>
  <p><strong>Pour recevoir ton document sous 24h</strong>, réponds simplement à cet email avec :</p>
  <ul>
    <li>Ta date de naissance</li>
    <li>Ton heure de naissance (si tu la connais)</li>
    <li>Ta ville de naissance</li>
  </ul>
  <p>Nous générerons ton rapport en priorité et te l'enverrons directement.</p>
  <p>Avec toute notre attention,<br><em>— Soléna, Plume Astrale</em></p>
</div>
"""


def _has_been_delivered(md: dict) -> bool:
    """Un client est considéré livré si pdf_path ET email_sent_at sont positionnés."""
    return bool(md.get('pdf_path')) and bool(md.get('email_sent_at'))


async def _regenerate(session_id: str, kind: str) -> str:
    """Cas A : déclenche le handler produit → PDF + email (idempotent).
    Reset pdf_path/email_sent_at avant l'appel pour forcer le re-traitement
    (les handlers skip early quand pdf_path est déjà positionné)."""
    try:
        sb = get_admin_client()
        tx_res = sb.table('payment_transactions').select('metadata').eq('session_id', session_id).maybe_single().execute()
        if tx_res and tx_res.data:
            md = (tx_res.data or {}).get('metadata') or {}
            md.pop('pdf_path', None)
            md.pop('email_sent_at', None)
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()

        if kind == 'kabbale_arbre_de_vie':
            from services.kabbale_service import handle_kabbale_webhook
            await handle_kabbale_webhook(session_id)
            return 'regenerated (kabbale)'
        elif kind == 'pack_karmique_kabbale':
            from services.pack_karmique_service import handle_pack_karmique_webhook
            await handle_pack_karmique_webhook(session_id)
            return 'regenerated (pack_karmique)'
        elif kind == 'compatibilite_ultime':
            # Pas de handler webhook async standalone — l'email/PDF est généré à la volée
            # à la fin du checkout. Pour ce cas, on tombe en apology.
            return 'skipped (no async handler — use apology mode)'
        return f'unknown kind {kind}'
    except Exception as e:
        return f'ERROR {type(e).__name__}: {e}'


def _send_apology(email: str, kind: str, resend_key: str, sender: str) -> str:
    if not email:
        return 'no-email'
    product, price, _ = KINDS[kind]
    html = APOLOGY_HTML.format(name_part='', product=product, price=price)
    try:
        r = httpx.post(
            'https://api.resend.com/emails',
            headers={'Authorization': f'Bearer {resend_key}', 'Content-Type': 'application/json'},
            json={'from': sender, 'to': [email],
                  'subject': f"Ton document « {product} » — on te doit des excuses ✦",
                  'html': html},
            timeout=30,
        )
        if r.status_code < 300:
            body = r.json() if r.text else {}
            return f'apology sent ({body.get("id", r.status_code)})'
        return f'apology FAILED {r.status_code}: {r.text[:200]}'
    except Exception as e:
        return f'apology ERROR {type(e).__name__}: {e}'


async def main(send: bool = False, only_kinds: set | None = None):
    stripe.api_key = os.environ['STRIPE_API_KEY']
    sb = get_admin_client()
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')

    print(f'Sender configuré : {sender}')
    print(f'Kinds ciblés     : {", ".join(sorted(only_kinds)) if only_kinds else "tous"}')
    print()

    affected = []
    starting_after = None
    scanned = 0
    while True:
        kwargs = {'limit': 100}
        if starting_after:
            kwargs['starting_after'] = starting_after
        page = stripe.checkout.Session.list(**kwargs)
        if not page.data:
            break
        for s in page.data:
            scanned += 1
            md = s.get('metadata') or {}
            kind = md.get('kind') or md.get('product')
            if kind not in KINDS:
                continue
            if only_kinds and kind not in only_kinds:
                continue
            if s.get('payment_status') != 'paid':
                continue
            r = sb.table('payment_transactions').select('session_id, metadata, user_email').eq('session_id', s['id']).maybe_single().execute()
            row = r.data if r else None
            row_md = (row or {}).get('metadata') or {}
            if row and _has_been_delivered(row_md):
                continue  # déjà livré (PDF + email)
            email = (
                (row or {}).get('user_email')
                or md.get('email')
                or (s.get('customer_details') or {}).get('email')
                or ''
            )
            affected.append({
                'session_id': s['id'],
                'email': email,
                'kind': kind,
                'amount': (s.get('amount_total') or 0) / 100,
                'created': s.get('created'),
                'tx_in_db': bool(row),
                'pdf_path': row_md.get('pdf_path'),
                'email_sent_at': row_md.get('email_sent_at'),
                'strategy': KINDS[kind][2],
            })
        if not page.has_more:
            break
        starting_after = page.data[-1]['id']
        if scanned >= 2000:
            print('⚠️  Limite de 2000 sessions atteinte — augmente si nécessaire.')
            break

    print(f'Sessions Stripe scannées : {scanned}')
    print(f'Achats payés NON livrés  : {len(affected)}')
    print()
    for a in affected:
        d = datetime.fromtimestamp(a['created'], tz=timezone.utc).strftime('%d/%m/%Y')
        state = '📄+📧' if (a['pdf_path'] and a['email_sent_at']) else ('📄  ' if a['pdf_path'] else '   ')
        strategy = a['strategy']
        print(f"  {d} | {a['email'] or '(email inconnu)':40s} | {KINDS[a['kind']][0]:35s} | {a['amount']:.2f}€ | tx_db={'✓' if a['tx_in_db'] else '✗'} | {state} | → {strategy}")

    if not send:
        print('\nDry-run terminé. Relance avec --send pour executer la relivraison.')
        return

    print('\n🔄  Exécution du rattrapage…\n')
    for a in affected:
        strategy = a['strategy']
        # 1) S'assurer que la tx est en DB (cas apology + certains cas anciens)
        if not a['tx_in_db']:
            try:
                sb.table('payment_transactions').insert({
                    'session_id': a['session_id'],
                    'user_email': a['email'],
                    'pack_id': a['kind'],
                    'amount': a['amount'],
                    'currency': 'eur',
                    'credits': 0,
                    'status': 'completed',
                    'payment_status': 'paid',
                    'metadata': {'kind': a['kind'], 'retrofit': True},
                }).execute()
                print(f"  tx insérée pour {a['session_id']}")
            except Exception as e:
                print(f"  ⚠️  insert failed {a['session_id']}: {e}")

        # 2) Livraison
        if strategy == 'regenerate' and a['tx_in_db']:
            status = await _regenerate(a['session_id'], a['kind'])
        elif strategy == 'apology' or strategy == 'regenerate':
            # regenerate sans tx_in_db (pas de birth_data) → fallback apology
            status = _send_apology(a['email'], a['kind'], resend_key, sender)
        else:
            status = 'no strategy'
        print(f"  {a['email'] or a['session_id']:40s} → {status}")


if __name__ == '__main__':
    args = sys.argv[1:]
    send = '--send' in args
    only_kinds = None
    if '--only' in args:
        i = args.index('--only')
        if i + 1 < len(args):
            only_kinds = set(k.strip() for k in args[i + 1].split(',') if k.strip())
    asyncio.run(main(send=send, only_kinds=only_kinds))
