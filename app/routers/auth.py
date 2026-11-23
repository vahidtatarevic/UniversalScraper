from typing import Annotated

import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlmodel import select

from app.auth import create_token, decode_token, password_hash
from app.config import GOOGLE_CLIENT_ID
from app.database import SessionDep
from app.mailer import send_verification_email
from app.models import (
    GoogleLogin,
    ResendVerification,
    User,
    UserCreate,
    UserIdentity,
)

VERIFY_TOKEN_MINUTES = 24 * 60

router = APIRouter()


@router.post("/signup")
def signup(data: UserCreate, session: SessionDep, background_tasks: BackgroundTasks):
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    existing_email = session.exec(select(User).where(User.email == data.email)).first()
    if existing_email:
        return {"message": "Check your email to verify your account"}
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=password_hash.hash(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    send_verification_link(user, background_tasks)
    return {"message": "Check your email to verify your account"}


def send_verification_link(user, background_tasks):
    # Sent after the response goes out, so a slow or failing mail server
    # never delays or breaks the request.
    token = create_token(user.username, purpose="verify", minutes=VERIFY_TOKEN_MINUTES)
    background_tasks.add_task(send_verification_email, user.email, token)


@router.get("/verify")
def verify_email(token: str, session: SessionDep):
    # One message for every failure, so the response never reveals whether
    # an account exists.
    invalid = HTTPException(
        status_code=400, detail="Invalid or expired verification link"
    )
    try:
        username = decode_token(token, "verify")
    except jwt.InvalidTokenError:
        raise invalid
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise invalid
    # Idempotent: mail scanners often open links before the user does, so a
    # second click must succeed too.
    if not user.is_verified:
        user.is_verified = True
        session.add(user)
        session.commit()
    return {"message": "Email verified"}


@router.post("/resend-verification")
def resend_verification(
    data: ResendVerification, session: SessionDep, background_tasks: BackgroundTasks
):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if user and not user.is_verified:
        send_verification_link(user, background_tasks)
    return {"message": "If that account needs verification, a new link was sent"}


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
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email is not verified")
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
    # Only trust the email if Google has verified it; otherwise anyone could
    # take over an account by adding its address to a Google account.
    if not info.get("email_verified"):
        raise HTTPException(status_code=400, detail="Google email is not verified")
    identity = session.exec(
        select(UserIdentity).where(
            UserIdentity.provider == "google",
            UserIdentity.provider_id == info["sub"],
        )
    ).first()
    if identity:
        user = session.get(User, identity.user_id)
    else:
        # Link to an existing account with the same email, or create one.
        user = session.exec(select(User).where(User.email == info["email"])).first()
        if not user:
            user = User(username=info["email"], email=info["email"])
        user.is_verified = True
        session.add(user)
        session.commit()
        session.refresh(user)
        session.add(
            UserIdentity(user_id=user.id, provider="google", provider_id=info["sub"])
        )
        session.commit()
    token = create_token(user.username)
    return {"access_token": token, "token_type": "bearer"}
