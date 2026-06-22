"""Daily journal email service — sends horoscope + Plume advice via Resend."""
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from resend import Resend
from services.daily_content import get_daily_content
from services.supabase_client import get_admin_client

RESEND_API_KEY = os.getenv('RESEND_API_KEY')
SENDER_EMAIL = os.getenv('RESEND_SENDER_EMAIL', 'contact.plume@gmail.com')

resend = Resend(api_key=RESEND_API_KEY) if RESEND_API_KEY else None

async def get_users_for_daily_journal() -> List[Dict[str, Any]]:
    """Fetch all users with email and birth_date set, excluding those already sent today."""
    if not get_admin_client():
        return []
    
    try:
        sb = get_admin_client()
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # Get all users with birth_date
        users_res = sb.table('profiles').select('id,email,prenom,birth_date').eq('email_verified', True).execute()
        users = users_res.data or []
        
        # Filter: must have email + birth_date
        users = [u for u in users if u.get('email') and u.get('birth_date')]
        
        # Exclude already sent today
        logs_res = sb.table('journal_email_logs').select('user_id').eq('sent_date', today).execute()
        sent_ids = {log['user_id'] for log in (logs_res.data or [])}
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
    if not resend or not email:
        print(f'[journal_email] Resend not configured or email missing')
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
        
        # Send via Resend
        res = resend.emails.send({
            'from': SENDER_EMAIL,
            'to': email,
            'subject': f'✦ Ton Horoscope du Jour — {prenom or "Voyageur"}',
            'html': html_body,
        })
        
        if res.get('id'):
            print(f'[journal_email] Sent to {email} (resend_id={res["id"]})')
            return True
        else:
            print(f'[journal_email] Send failed: {res}')
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


async def send_daily_journal_batch() -> Dict[str, Any]:
    """Send daily journal to all eligible users (main cron task)."""
    users = await get_users_for_daily_journal()
    if not users:
        return {'status': 'ok', 'sent': 0, 'users': 0, 'message': 'No eligible users'}
    
    sent_count = 0
    failed_count = 0
    
    for user in users:
        user_id = user['id']
        email = user['email']
        prenom = user.get('prenom') or 'Voyageur'
        birth_date = user['birth_date']
        
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
        'total_eligible': len(users),
    }
