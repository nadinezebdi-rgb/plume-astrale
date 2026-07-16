try:
    import resend
    resend.api_key = resend_key

    # ... (html_content inchangé) ...

    # Send
    params = {
        "from": "no-reply@plume-astrale.fr",
        "to": [email],  # Resend attend une liste pour "to"
        "subject": f"{first_name}, tes Fenêtres de Rencontre sont prêtes! ✦",
        "html": html_content,
    }
    response = resend.Emails.send(params)

    print('✅ Email sent successfully!')
    print(f'   To: {email}')
    print(f'   Status: {response}')

except ImportError as e:
    print(f'⚠️ Resend library not installed: {e}')
    print('   Install it with: pip install resend')
except Exception as e:
    print(f'⚠️ Email error: {e}')
    print('   Your PDF is still available for download')
