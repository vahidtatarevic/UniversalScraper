import ipaddress
import socket
from urllib.parse import urljoin, urlparse

from curl_cffi import requests
from curl_cffi.requests.exceptions import TooManyRedirects


def is_public_url(url: str) -> bool:
    hostname = urlparse(url).hostname
    if not hostname:
        return False
    try:
        addresses = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False
    for address in addresses:
        ip = address[4][0]
        if not ipaddress.ip_address(ip).is_global:
            return False
    return True


MAX_REDIRECTS = 5


class UnsafeURLError(Exception):
    pass


def fetch(url: str):
    for _ in range(MAX_REDIRECTS + 1):
        if not is_public_url(url):
            raise UnsafeURLError(url)
        response = requests.get(
            url, impersonate="chrome", timeout=60, allow_redirects=False
        )
        if not response.is_redirect:
            return response
        url = urljoin(url, response.headers["location"])
    raise TooManyRedirects("Too many redirects")
