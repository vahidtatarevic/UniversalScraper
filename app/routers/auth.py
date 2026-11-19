from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlmodel import select

from app.auth import create_token, password_hash
from app.config import GOOGLE_CLIENT_ID
from app.database import SessionDep
from app.models import GoogleLogin, User, UserCreate, UserIdentity

router = APIRouter()


@router.post("/signup")
def signup(data: UserCreate, session: SessionDep):
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=data.username, hashed_password=password_hash.hash(data.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_token(user.username)
    return {
        "message": "User registered successfully",
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    user = session.exec(select(User).where(User.username == form.username)).first()
    if (
        not user
        or not user.hashed_password
        or not password_hash.verify(form.password, user.hashed_password)
    ):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(user.username)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/google")
def google_login(data: GoogleLogin, session: SessionDep):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google login is not configured")
    try:
        info = id_token.verify_oauth2_token(
            data.token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    identity = session.exec(
        select(UserIdentity).where(
            UserIdentity.provider == "google",
            UserIdentity.provider_id == info["sub"],
        )
    ).first()
    if identity:
        user = session.get(User, identity.user_id)
    else:
        user = User(username=info["email"], email=info["email"])
        session.add(user)
        session.commit()
        session.refresh(user)
        user_identity = UserIdentity(
            user_id=user.id,
            provider="google",
            provider_id=info["sub"],
        )
        session.add(user_identity)
        session.commit()
        session.refresh(user_identity)
    token = create_token(user.username)
    return {"access_token": token, "token_type": "bearer"}
