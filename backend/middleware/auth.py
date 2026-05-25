"""JWT Supabase verification middleware + dependency."""
from fastapi import HTTPException, status, Request, Depends
from typing import Optional
import jwt
from jwt import InvalidTokenError, ExpiredSignatureError

from config import get_settings


def verify_supabase_token(token: str) -> dict:
    """Decode + verify un JWT Supabase HS256. Retourne le payload."""
    s = get_settings()
    try:
        payload = jwt.decode(
            token,
            s.SUPABASE_JWT_SECRET,
            algorithms=[s.SUPABASE_JWT_ALGORITHM],
            options={'verify_aud': False},
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')


def get_current_user(request: Request) -> dict:
    """Dependency FastAPI — extrait + verifie le Bearer token de Supabase."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Authentication required')
    token = auth_header.split(' ', 1)[1]
    payload = verify_supabase_token(token)
    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=401, detail='Token missing subject')
    return {
        'id': user_id,
        'email': payload.get('email'),
        'token': token,
        'claims': payload,
    }


def get_optional_user(request: Request) -> Optional[dict]:
    """Dependency optionnelle — retourne None si pas de token (pour les routes publiques + chat invite)."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    try:
        return get_current_user(request)
    except HTTPException:
        return None
