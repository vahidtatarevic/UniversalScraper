from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

def test_rejects_url_without_http():
    response = client.get("/scrape", params={"url": "books.toscrape.com"})
    assert response.status_code == 400