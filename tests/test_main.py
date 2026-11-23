USER = {"username": "testuser", "email": "test@example.com", "password": "testpass"}
LOGIN = {"username": "testuser", "password": "testpass"}


def signup_and_verify(client, sent_emails):
    client.post("/signup", json=USER)
    client.get("/verify", params={"token": sent_emails[-1]["token"]})


def test_signup_does_not_return_access_token(client, sent_emails):
    response = client.post("/signup", json=USER)
    assert response.status_code == 200
    assert "access_token" not in response.json()


def test_signup_sends_verification_email(client, sent_emails):
    client.post("/signup", json=USER)
    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == "test@example.com"


def test_login_rejected_before_verification(client, sent_emails):
    client.post("/signup", json=USER)
    response = client.post("/login", data=LOGIN)
    assert response.status_code == 403


def test_login_works_after_verification(client, sent_emails):
    signup_and_verify(client, sent_emails)
    response = client.post("/login", data=LOGIN)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_verify_rejects_invalid_token(client, sent_emails):
    response = client.get("/verify", params={"token": "not-a-real-token"})
    assert response.status_code == 400


def test_verify_link_can_be_opened_twice(client, sent_emails):
    client.post("/signup", json=USER)
    token = sent_emails[0]["token"]
    client.get("/verify", params={"token": token})
    response = client.get("/verify", params={"token": token})
    assert response.status_code == 200


def test_resend_sends_new_link_to_unverified_user(client, sent_emails):
    client.post("/signup", json=USER)
    response = client.post("/resend-verification", json={"email": USER["email"]})
    assert response.status_code == 200
    assert len(sent_emails) == 2
    client.get("/verify", params={"token": sent_emails[1]["token"]})
    assert client.post("/login", data=LOGIN).status_code == 200


def test_resend_does_not_email_verified_user(client, sent_emails):
    signup_and_verify(client, sent_emails)
    response = client.post("/resend-verification", json={"email": USER["email"]})
    assert response.status_code == 200
    assert len(sent_emails) == 1


def test_resend_does_not_reveal_unknown_email(client, sent_emails):
    response = client.post("/resend-verification", json={"email": "nobody@example.com"})
    assert response.status_code == 200
    assert sent_emails == []


def test_verification_token_is_not_an_access_token(client, sent_emails):
    client.post("/signup", json=USER)
    response = client.get(
        "/scrape",
        params={"url": "https://books.toscrape.com"},
        headers={"Authorization": f"Bearer {sent_emails[0]['token']}"},
    )
    assert response.status_code == 401


def test_rejects_url_without_http(client, sent_emails):
    signup_and_verify(client, sent_emails)
    token = client.post("/login", data=LOGIN).json()["access_token"]
    response = client.get(
        "/scrape",
        params={"url": "books.toscrape.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
