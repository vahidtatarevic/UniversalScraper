from sqlmodel import SQLModel, Field, create_engine, Session
import sqlmodel

engine = create_engine("sqlite:///database.db")

def getSession():
    with Session(engine) as session:
        yield session

