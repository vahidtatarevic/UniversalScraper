import ipaddress
import socket
from urllib.parse import urlparse


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
