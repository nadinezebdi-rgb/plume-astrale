"""
RATTRAPAGE — Achats numerologie/karma-destin/fenetre-rencontre jamais livres.

Contexte : jusqu'au fix du 18/07/2026, les routes de ces 3 produits creaient la session
Stripe mais n'inseraient JAMAIS la transaction en DB (.insert() sans .execute()).
Resultat : le webhook ne retrouvait pas la transaction -> aucun PDF genere ni email envoye.
Les donnees de naissance n'etaient stockees QUE dans la ligne DB manquante -> impossible
de regenerer automatiquement. On envoie donc un email d'excuse demandant les infos.

Usage (depuis /app/backend) :
    python scripts/retrofit_lost_pdfs.py            # dry-run : liste les clients touches
    python scripts/retrofit_lost_pdfs.py --send     # insere les tx manquantes + envoie les emails
"""
import os
import sys
import httpx
import stripe

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

from services.supabase_client import get_admin_client  # noqa: E402

KINDS = {
    'numerologie_code': ('Code Numérologique', '19€'),
    'karma_destin_analysis': ('Analyse Karmique & Destinée', '24€'),
    'fenetre_rencontre_avancee': ('Fenêtres de Rencontre Avancées', '29€'),
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


def main(send: bool = False):
    stripe.api_key = os.environ['STRIPE_API_KEY']
    sb = get_admin_client()
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')

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
            kind = md.get('kind')
            if kind not in KINDS:
                continue
            if s.get('payment_status') != 'paid':
                continue
            r = sb.table('payment_transactions').select('session_id, metadata').eq('session_id', s['id']).maybe_single().execute()
            row = r.data if r else None
            if row and (row.get('metadata') or {}).get('pdf_path'):
                continue  # deja livre
            email = md.get('email') or (s.get('customer_details') or {}).get('email') or ''
            affected.append({
                'session_id': s['id'],
                'email': email,
                'kind': kind,
                'amount': (s.get('amount_total') or 0) / 100,
                'created': s.get('created'),
                'tx_in_db': bool(row),
            })
        if not page.has_more:
            break
        starting_after = page.data[-1]['id']
        if scanned >= 1000:
            break

    print(f'Sessions Stripe scannées : {scanned}')
    print(f'Achats payés NON livrés : {len(affected)}')
    for a in affected:
        from datetime import datetime, timezone
        d = datetime.fromtimestamp(a['created'], tz=timezone.utc).strftime('%d/%m/%Y')
        print(f"  - {d} | {a['email'] or '(email inconnu)'} | {KINDS[a['kind']][0]} | {a['amount']:.2f}€ | tx_db={a['tx_in_db']}")

    if not send:
        print('\nDry-run terminé. Relance avec --send pour insérer les tx + envoyer les emails.')
        return

    for a in affected:
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
                print(f"  ERREUR insert {a['session_id']}: {e}")
        if a['email'] and resend_key:
            product, price = KINDS[a['kind']]
            html = APOLOGY_HTML.format(name_part='', product=product, price=price)
            r = httpx.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {resend_key}', 'Content-Type': 'application/json'},
                json={'from': sender, 'to': [a['email']],
                      'subject': f"Ton document « {product} » — on te doit des excuses ✦",
                      'html': html},
                timeout=30,
            )
            print(f"  email {a['email']} -> {r.status_code}")


if __name__ == '__main__':
    main(send='--send' in sys.argv)
