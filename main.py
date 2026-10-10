import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from functions import scrapeFunction
from models import User, UserCreate
from database import engine, getSession
from sqlmodel import SQLModel, Session, select
from pwdlib import PasswordHash

SQLModel.metadata.create_all(engine)
app = FastAPI()
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET = "my-secret-key-change-me-0123456789"
passwordHash = PasswordHash.recommended()

@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), session : Session = Depends(getSession)):
    user = session.exec(select(User).where(User.username == form.username)).first()
    if not user or not passwordHash.verify(form.password, user.hashedPassword):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = jwt.encode({"sub": user.username}, SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


@app.post("/signup")
def signup(form: UserCreate = Depends(), session: Session = Depends(getSession)):
    existing = session.exec(select(User).where(User.username == form.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=form.username, hashedPassword=passwordHash.hash(form.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User registered successfully"}

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

