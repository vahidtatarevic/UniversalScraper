import pytest

from app.scrapers.safety import is_public_url


@pytest.mark.parametrize(
    "url",
    [
        "http://8.8.8.8",
        "https://1.1.1.1/page",
    ],
)
def test_allows_public_addresses(url):
    assert is_public_url(url) is True


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1",  # this machine
        "http://localhost:5432",  # local Postgres
        "http://169.254.169.254",  # AWS instance metadata
        "http://10.0.0.5",  # private network
        "http://192.168.1.1",  # home router
        "http://[::1]",  # localhost (IPv6)
        "http://0.0.0.0",
        "http://doesnotexist.invalid",  # domain that does not exist
        "http://",  # no host at all
    ],
)
def test_blocks_internal_addresses(url):
    assert is_public_url(url) is False
