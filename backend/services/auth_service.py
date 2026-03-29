"""Authentication service - JWT auth, password hashing, user management"""
import os
import bcrypt as _bcrypt
try:
    import jwt
except ImportError:
    from jose import jwt
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

JWT_SECRET = os.environ.get("JWT_SECRET", "plume-astrale-secret-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 72


def hash_password(password: str) -> str:
    """Hash a password using bcrypt directly (compatible with all bcrypt versions)."""
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")


async def get_current_user(request: Request, db: AsyncIOMotorDatabase) -> dict:
    """Extract and validate JWT from Authorization header, return user doc."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentification requise")
    token = auth.split(" ", 1)[1]
    payload = decode_token(token)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    return user

