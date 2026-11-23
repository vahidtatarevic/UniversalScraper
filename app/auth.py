from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.config import SECRET

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
password_hash = PasswordHash.recommended()


def create_token(username, purpose="access", minutes=30):
    expires = datetime.now(UTC) + timedelta(minutes=minutes)
    payload = {"sub": username, "purpose": purpose, "exp": expires}
    return jwt.encode(payload, SECRET, algorithm="HS256")


def decode_token(token, purpose):
    """Return the username from a token, or raise jwt.InvalidTokenError.

    Raises for bad signatures, expired tokens and tokens issued for a
    different purpose (e.g. a verification token used as an access token).
    """
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    if payload.get("purpose") != purpose:
        raise jwt.InvalidTokenError("Token was issued for a different purpose")
    return payload["sub"]


def current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        return decode_token(token, "access")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
