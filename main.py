import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from functions import scrapeFunction
from models import User, UserCreate
from database import engine, getSession
from sqlmodel import SQLModel, Session, select
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

SQLModel.metadata.create_all(engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="login")

load_dotenv()
SECRET = os.environ["SECRET_KEY"]

passwordHash = PasswordHash.recommended()

@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), session : Session = Depends(getSession)):
    user = session.exec(select(User).where(User.username == form.username)).first()
    if not user or not passwordHash.verify(form.password, user.hashedPassword):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = jwt.encode({"sub": user.username, "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}, SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


@app.post("/signup")
def signup(data: UserCreate, session: Session = Depends(getSession)):
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=data.username, hashedPassword=passwordHash.hash(data.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    token = jwt.encode({"sub": user.username, "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}, SECRET, algorithm="HS256")
    return {"message": "User registered successfully", "access_token": token, "token_type": "bearer"}


def currentUser(token: str = Depends(oauth2Scheme)):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])["sub"]
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/scrape")
def scrape(url: str, username: str = Depends(currentUser)):
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    try:
        response = scrapeFunction(url)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to scrape the page.")

    if not response:
        raise HTTPException(status_code=404, detail="No data found.")
    return response