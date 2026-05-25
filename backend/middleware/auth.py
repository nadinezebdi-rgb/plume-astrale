"""JWT Supabase verification middleware + dependency."""
from fastapi import HTTPException, status, Request, Depends
from typing import Optional
from functools import lru_cache
import jwt
from jwt import InvalidTokenError, ExpiredSignatureError, PyJWKClient

from config import get_settings


@lru_cache
def _jwks_client() -> PyJWKClient:
    """Cached JWKS client — fetches public keys from Supabase Auth."""
    s = get_settings()
    jwks_url = f'{s.SUPABASE_URL}/auth/v1/.well-known/jwks.json'
    return PyJWKClient(jwks_url, cache_keys=True, lifespan=600)


def verify_supabase_token(token: str) -> dict:
    """Decode + verify un JWT Supabase. Tente d'abord JWKS (ES256/RS256), fallback HS256."""
    s = get_settings()
    # Detect algorithm from header
    try:
        header = jwt.get_unverified_header(token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

    alg = header.get('alg', 'HS256')
    try:
        if alg in ('ES256', 'RS256', 'EdDSA'):
            signing_key = _jwks_client().get_signing_key_from_jwt(token).key
            payload = jwt.decode(token, signing_key, algorithms=[alg], options={'verify_aud': False})
        else:
            payload = jwt.decode(token, s.SUPABASE_JWT_SECRET, algorithms=['HS256'], options={'verify_aud': False})
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f'Invalid token: {e}')


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
