from sqlmodel import Session, create_engine

engine = create_engine("sqlite:///database.db")


def getSession():
    with Session(engine) as session:
        yield session
