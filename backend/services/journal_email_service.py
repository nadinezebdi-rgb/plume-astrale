"""Daily journal email service — sends horoscope + Plume advice via Resend."""
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from services.daily_content import get_daily_content
from services.supabase_client import get_admin_client
from services.resend_service import send_email

RESEND_API_KEY = os.getenv('RESEND_API_KEY')
# Utilise la même variable centrale que tous les autres services (contact@plume-astrale.fr, domaine vérifié)
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')

async def get_users_for_daily_journal() -> List[Dict[str, Any]]:
    """Fetch all users with email and birth_date set, excluding those already sent today."""
    if not get_admin_client():
        return []
    
    try:
        sb = get_admin_client()
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # Get all users with birth_date (colonne email_verified n'existe pas dans profiles)
        users_res = sb.table('profiles').select('id,email,prenom,birth_date').execute()
        users = users_res.data or []
        
        # Filter: must have email + birth_date
        users = [u for u in users if u.get('email') and u.get('birth_date')]
        
        # Exclude already sent today (journal_email_logs peut ne pas exister — fallback silencieux)
        try:
            logs_res = sb.table('journal_email_logs').select('user_id').eq('sent_date', today).execute()
            sent_ids = {log['user_id'] for log in (logs_res.data or [])}
        except Exception:
            sent_ids = set()
        users = [u for u in users if u['id'] not in sent_ids]
        
        return users
    except Exception as e:
        print(f'[journal_email] get_users error: {e}')
        return []


def _build_journal_html(prenom: str, horoscope: str, advice: str) -> str:
    """Build styled HTML email for daily journal."""
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Georgia, serif; background: #0c0918; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #1a1726; border-radius: 12px; overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #2a2435 0%, #1a1726 100%); padding: 30px; text-align: center; border-bottom: 1px solid #c5a059; }}
            .title {{ color: #f0e6d3; font-size: 28px; margin: 0; font-weight: 300; letter-spacing: 2px; }}
            .subtitle {{ color: #b8b0c8; font-size: 12px; margin-top: 8px; letter-spacing: 1px; text-transform: uppercase; }}
            .content {{ padding: 30px; }}
            .greeting {{ color: #c5a059; font-size: 16px; margin-bottom: 20px; }}
            .section {{ margin-bottom: 25px; }}
            .section-title {{ color: #c5a059; font-size: 14px; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid rgba(197,160,89,0.2); padding-bottom: 8px; }}
            .section-text {{ color: #b8b0c8; font-size: 14px; line-height: 1.8; }}
            .footer {{ background: rgba(197,160,89,0.05); padding: 20px; text-align: center; border-top: 1px solid rgba(197,160,89,0.1); }}
            .footer-text {{ color: #b8b0c8; font-size: 12px; margin: 0; }}
            .logo {{ font-size: 12px; color: #c5a059; letter-spacing: 2px; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">✦ PLUME ASTRALE ✦</div>
                <h1 class="title">Ton Journal du Jour</h1>
                <p class="subtitle">Guidance Astrologique Personnalisée</p>
            </div>
            
            <div class="content">
                <p class="greeting">Bonjour {prenom},</p>
                
                <div class="section">
                    <div class="section-title">📖 Ton Horoscope</div>
                    <p class="section-text">{horoscope}</p>
                </div>
                
                <div class="section">
                    <div class="section-title">✨ Conseil de la Plume</div>
                    <p class="section-text">{advice}</p>
                </div>
            </div>
            
            <div class="footer">
                <p class="footer-text">Plume Astrale — Éclaire ta route avec les étoiles</p>
                <p class="footer-text">© 2026 · Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """


async def send_daily_journal_email(user_id: str, email: str, prenom: str, birth_date: str) -> bool:
    """Send daily journal email to one user; return True if sent successfully."""
    if not RESEND_API_KEY or not email:
        print('[journal_email] Resend not configured or email missing')
        return False

    try:
        # Get horoscope + advice for this user's sign
        content = await get_daily_content(birth_date)
        if not content:
            print(f'[journal_email] No daily content for {user_id}')
            return False

        horoscope_text = content.get('horoscope') or 'Les énergies du jour t\'invitent à explorer tes possibilités. Reste attentif aux synchronicités.'
        advice_text = content.get('conseil') or 'Prends un moment aujourd\'hui pour t\'aligner avec tes intentions profondes.'

        html_body = _build_journal_html(prenom or 'Voyageur', horoscope_text, advice_text)
        subject = f'✦ Ton Horoscope du Jour — {prenom or "Voyageur"}'

        eid = await send_email(email, subject, html_body)
        if eid:
            print(f'[journal_email] Sent to {email} (resend_id={eid})')
            return True
        print(f'[journal_email] Send returned no id for {email}')
        return False
    except Exception as e:
        print(f'[journal_email] Exception sending to {email}: {e}')
        return False


async def log_sent(user_id: str, email: str, sent_date: str = None) -> bool:
    """Log that email was sent today to prevent duplicates."""
    if not get_admin_client():
        return False
    
    try:
        sb = get_admin_client()
        if not sent_date:
            sent_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        sb.table('journal_email_logs').insert({
            'user_id': user_id,
            'email': email,
            'sent_date': sent_date,
            'sent_at': datetime.now(timezone.utc).isoformat(),
        }).execute()
        return True
    except Exception as e:
        print(f'[journal_email] log_sent error: {e}')
        return False


async def get_bundle_guests_for_daily_journal() -> List[Dict[str, Any]]:
    """Retourne les acheteurs du bundle Lecture Complete 97€ actifs (<90j) qui NE SONT PAS
    deja dans la table profiles (guests). Ils recoivent le journal quotidien automatiquement
    pendant les 90 jours actifs du bundle.
    """
    from datetime import timedelta
    if not get_admin_client():
        return []
    try:
        sb = get_admin_client()
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        min_dt = datetime.now(timezone.utc) - timedelta(days=90)

        # Fetch les bundles actifs (paid, non refund, <90j)
        r = sb.table('payment_transactions').select(
            'session_id, user_email, created_at, metadata'
        ).eq('pack_id', 'lecture_complete').eq('payment_status', 'paid').gte(
            'created_at', min_dt.isoformat()
        ).execute()
        rows = (r.data or []) if r else []
        # Filtre : exclure refunded
        rows = [
            row for row in rows
            if not ((row.get('metadata') or {}).get('refunded_at'))
        ]

        # Deduplique par email en gardant la commande la plus recente
        by_email: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            e = (row.get('user_email') or '').lower()
            if not e or '@' not in e:
                continue
            if e not in by_email or (row.get('created_at') or '') > (by_email[e].get('created_at') or ''):
                by_email[e] = row

        if not by_email:
            return []

        # Exclure emails deja dans profiles (deja traites par get_users_for_daily_journal)
        try:
            emails_list = list(by_email.keys())
            prof = sb.table('profiles').select('email').in_('email', emails_list).execute()
            existing_emails = {(p.get('email') or '').lower() for p in (prof.data or [])}
        except Exception:
            existing_emails = set()

        # Exclure ceux deja envoyes aujourd'hui (guest_email log)
        try:
            logs = sb.table('journal_email_logs').select('email').eq('sent_date', today).execute()
            sent_today = {(log.get('email') or '').lower() for log in (logs.data or [])}
        except Exception:
            sent_today = set()

        # Construit la liste finale (guest = pas dans profiles)
        result = []
        for e, row in by_email.items():
            if e in existing_emails:
                continue  # deja envoye via /api/admin/cron/send-daily-journal
            if e in sent_today:
                continue
            md = row.get('metadata') or {}
            octx = md.get('order_ctx') or {}
            result.append({
                'id': None,  # guest, pas de profile id
                'email': e,
                'prenom': octx.get('first_name') or 'Ami(e)',
                'birth_date': octx.get('birth_date') or '',
                'session_id': row.get('session_id'),
                'bundle_guest': True,
            })
        return result
    except Exception as e:
        print(f'[journal_email] bundle_guests fetch error: {e}')
        return []


async def send_daily_journal_batch() -> Dict[str, Any]:
    """Send daily journal to all eligible users (main cron task).

    Inclut :
      - Les utilisateurs profiles avec email_verified=True + birth_date
      - Les guests ayant achete un bundle Lecture Complete 97€ dans les 90 derniers jours
        (Cercle Solena actif automatiquement pendant 90j).
    """
    users = await get_users_for_daily_journal()
    guests = await get_bundle_guests_for_daily_journal()
    all_users = list(users) + list(guests)
    if not all_users:
        return {'status': 'ok', 'sent': 0, 'users': 0, 'guests': 0, 'message': 'No eligible users'}

    sent_count = 0
    failed_count = 0

    for user in all_users:
        user_id = user.get('id') or f'guest:{user["email"]}'
        email = user['email']
        prenom = user.get('prenom') or 'Voyageur'
        birth_date = user.get('birth_date') or ''
        if not birth_date:
            continue  # sans birth_date pas de journal personnalise
        success = await send_daily_journal_email(user_id, email, prenom, birth_date)
        if success:
            await log_sent(user_id, email)
            sent_count += 1
        else:
            failed_count += 1

    return {
        'status': 'ok',
        'sent': sent_count,
        'failed': failed_count,
        'users': len(users),
        'guests': len(guests),
        'total_eligible': len(all_users),
    }


async def daily_journal_scheduler_loop() -> None:
    """Boucle background : envoie le journal quotidien une fois par jour.

    Verifie toutes les heures si la date a change ; si oui et si pas encore
    envoye aujourd'hui, lance send_daily_journal_batch.
    """
    import asyncio
    print('[journal_email] scheduler demarre (verifie toutes les heures)')
    last_run_date: Optional[str] = None
    while True:
        try:
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            if last_run_date != today:
                # Nouveau jour : lance le batch
                res = await send_daily_journal_batch()
                print(f'[journal_email] batch quotidien: {res}')
                last_run_date = today
        except Exception as e:
            print(f'[journal_email] scheduler erreur: {e}')
        await asyncio.sleep(3600)  # verif toutes les heures
