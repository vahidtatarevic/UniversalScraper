import pytest

USER = {"username": "testuser", "email": "test@example.com", "password": "testpass"}
LOGIN = {"username": "testuser", "password": "testpass"}


def google_payload(email="test@example.com", email_verified=True):
    # Mirrors the claims Google puts in a verified ID token.
    return {
        "iss": "https://accounts.google.com",
        "azp": "test-client-id",
        "aud": "test-client-id",
        "sub": "109876543210",
        "email": email,
        "email_verified": email_verified,
        "name": "Test User",
        "picture": "https://example.com/avatar.png",
        "given_name": "Test",
        "family_name": "User",
        "iat": 1700000000,
        "exp": 1700003600,
    }


@pytest.fixture
def google(monkeypatch):
    """Replace Google's token check; set `google.payload` to control the result."""

    class Google:
        payload = google_payload()

    monkeypatch.setattr("app.routers.auth.GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setattr(
        "app.routers.auth.id_token.verify_oauth2_token",
        lambda token, request, audience: Google.payload,
    )
    return Google


def test_google_login_links_to_existing_email_account(client, sent_emails, google):
    client.post("/signup", json=USER)
    response = client.post("/auth/google", json={"token": "google-id-token"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_google_login_verifies_existing_email_account(client, sent_emails, google):
    client.post("/signup", json=USER)
    client.post("/auth/google", json={"token": "google-id-token"})
    assert client.post("/login", data=LOGIN).status_code == 200


def test_google_login_rejects_unverified_google_email(client, sent_emails, google):
    google.payload = google_payload(email_verified=False)
    response = client.post("/auth/google", json={"token": "google-id-token"})
    assert response.status_code == 400
