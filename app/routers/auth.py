from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.auth import create_token, password_hash
from app.database import get_session
from app.models import User, UserCreate

router = APIRouter()


@router.post("/signup")
def signup(data: UserCreate, session: Annotated[Session, Depends(get_session)]):
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
    session: Annotated[Session, Depends(get_session)],
):
    user = session.exec(select(User).where(User.username == form.username)).first()
    if not user or not password_hash.verify(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(user.username)
    return {"access_token": token, "token_type": "bearer"}
