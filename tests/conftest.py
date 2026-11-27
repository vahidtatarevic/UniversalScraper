import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.limiter import limiter
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sent_emails(monkeypatch):
    sent = []
    monkeypatch.setattr(
        "app.routers.auth.send_verification_email",
        lambda email, token: sent.append({"to": email, "token": token}),
        raising=False,
    )
    return sent


@pytest.fixture(autouse=True)
def reset_rate_limits():
    # Every test client shares one address, so start each test with a clean
    # rate-limit counter instead of inheriting hits from earlier tests.
    limiter.reset()
