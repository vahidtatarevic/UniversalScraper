from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.config import SECRET

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="login")
passwordHash = PasswordHash.recommended()


def createToken(username):
    expires = datetime.now(UTC) + timedelta(minutes=30)
    return jwt.encode({"sub": username, "exp": expires}, SECRET, algorithm="HS256")


def currentUser(token: Annotated[str, Depends(oauth2Scheme)]):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])["sub"]
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
