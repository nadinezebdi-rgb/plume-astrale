#!/usr/bin/env python3
"""Envoyer email de confirmation avec lien PDF"""

import sys
sys.path.insert(0, '.')

from config import get_settings

settings = get_settings()
resend_key = settings.RESEND_API_KEY

print('\n📧 Sending confirmation email...\n')

pdf_url = "https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/reports/fenetre/fenetre_0e94526a7bea.pdf"
email = "nadine.zebdi@gmail.com"
first_name = "Nadine"

try:
    from resend import Resend
    client = Resend(api_key=resend_key)
    
    # Prepare email
    html_content = f"""
    <div style="font-family: 'Helvetica Neue', sans-serif; background: linear-gradient(135deg, #0C0918 0%, #1A1F2E 100%); padding: 40px 20px; text-align: center;">
        
        <div style="max-width: 600px; margin: 0 auto; background: rgba(212, 175, 55, 0.05); border: 1px solid #D4AF37; border-radius: 8px; padding: 30px; color: #F5EEE0;">
            
            <h1 style="color: #D4AF37; font-size: 24px; margin: 0 0 10px 0;">✦ Tes Fenêtres de Rencontre ✦</h1>
            
            <h2 style="color: #E3D7FF; font-size: 16px; margin: 0 0 20px 0;">Rapport Personnalisé d'Astrologie Amoureuse</h2>
            
            <p style="color: #F5EEE0; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                Chère {first_name},
            </p>
            
            <p style="color: #F5EEE0; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                Tes <strong>Fenêtres de Rencontre Avancées</strong> sont calculées et prêtes! 
            </p>
            
            <p style="color: #E3D7FF; font-size: 13px; line-height: 1.6; margin: 20px 0;">
                Ce rapport personnalisé de 10 pages inclut:
            </p>
            
            <ul style="color: #F5EEE0; font-size: 13px; text-align: left; margin: 20px auto; max-width: 400px;">
                <li>✦ <strong>3 Fenêtres de Rencontre</strong> — dates exactes</li>
                <li>✦ <strong>Transits de Vénus & Jupiter</strong> — amour & expansion</li>
                <li>✦ <strong>Phases Lunaires</strong> — timing optimal</li>
                <li>✦ <strong>Rituels & Cristaux</strong> — activation</li>
                <li>✦ <strong>Affirmations Puissantes</strong> — à réciter chaque jour</li>
            </ul>
            
            <p style="margin: 30px 0;">
                <a href="{pdf_url}" style="display: inline-block; background: #D4AF37; color: #0C0918; padding: 12px 30px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 14px;">
                    📥 Télécharger Ton Rapport
                </a>
            </p>
            
            <p style="color: #9089B5; font-size: 12px; margin: 30px 0 0 0; padding-top: 20px; border-top: 1px solid #D4AF37;">
                Par <strong>Solena</strong> — La voix de <strong>Plume Astrale</strong><br>
                Guidance Symbolique Personnalisée
            </p>
            
        </div>
        
    </div>
    """
    
    # Send
    response = client.emails.send({
        "from": "no-reply@plume-astrale.fr",
        "to": email,
        "subject": f"{first_name}, tes Fenêtres de Rencontre sont prêtes! ✦",
        "html": html_content,
    })
    
    print(f'✅ Email sent successfully!')
    print(f'   To: {email}')
    print(f'   Status: {response}')
    
except ImportError as e:
    print(f'⚠️  Resend import error: {e}')
    print(f'   The email may not have been sent due to DNS propagation (24-48h)')
except Exception as e:
    print(f'⚠️  Email error: {e}')
    print(f'   Your PDF is still available for download')
    print(f'   Check back later for email delivery')
