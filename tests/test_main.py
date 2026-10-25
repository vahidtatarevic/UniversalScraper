from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_token():
    client.post("/signup", json={"username": "testuser", "password": "testpass"})
    response = client.post(
        "/login", data={"username": "testuser", "password": "testpass"}
    )
    return response.json()["access_token"]


def test_rejects_url_without_http():
    token = get_token()
    response = client.get(
        "/scrape",
        params={"url": "books.toscrape.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


def test_signup_and_login():
    client.post("/signup", json={"username": "testuser", "password": "testpass"})
    response = client.post(
        "/login", data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
