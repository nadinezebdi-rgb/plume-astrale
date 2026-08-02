#!/usr/bin/env python3
"""
Reset password d'un utilisateur Supabase via admin API.

Usage :
  python3 backend/scripts/reset_test_user_password.py \
      --email plume_test_863a0303@gmail.com --password TestPlume2026!

Utilise SUPABASE_SERVICE_ROLE_KEY depuis backend/.env.
"""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

# Load .env from backend/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / '.env')

from supabase import create_client


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', required=True)
    parser.add_argument('--password', required=True)
    args = parser.parse_args()

    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_SERVICE_KEY')
    if not url or not key:
        print('[reset] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY manquant')
        return 2

    sb = create_client(url, key)
    # Find user id by email via admin.list_users
    try:
        page = sb.auth.admin.list_users()
        # `page` is a list of users (or an object with .users)
        users = getattr(page, 'users', None) or (page if isinstance(page, list) else [])
        target = None
        for u in users:
            u_email = getattr(u, 'email', None) or (u.get('email') if isinstance(u, dict) else None)
            if u_email and u_email.lower() == args.email.lower():
                target = u
                break
        if not target:
            print(f'[reset] Utilisateur non trouve: {args.email}')
            return 3
        user_id = getattr(target, 'id', None) or (target.get('id') if isinstance(target, dict) else None)
        if not user_id:
            print('[reset] user_id introuvable dans la reponse')
            return 4
        sb.auth.admin.update_user_by_id(user_id, {'password': args.password})
        print(f'[reset] OK — password reset pour {args.email} (id={user_id})')
        return 0
    except Exception as e:
        print(f'[reset] Echec: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
