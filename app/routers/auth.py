from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.auth import createToken, passwordHash
from app.database import getSession
from app.models import User, UserCreate

router = APIRouter()


@router.post("/signup")
def signup(data: UserCreate, session: Annotated[Session, Depends(getSession)]):
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=data.username, hashedPassword=passwordHash.hash(data.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    token = createToken(user.username)
    return {
        "message": "User registered successfully",
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(getSession)],
):
    user = session.exec(select(User).where(User.username == form.username)).first()
    if not user or not passwordHash.verify(form.password, user.hashedPassword):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = createToken(user.username)
    return {"access_token": token, "token_type": "bearer"}
