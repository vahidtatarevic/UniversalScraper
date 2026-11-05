from urllib.parse import urlparse

from bs4 import BeautifulSoup
from curl_cffi import requests

from app.scrapers.parser import bookScrape, carScrape, pokemonScrape


def scrapeFunction(url, output="json"):
    response = requests.get(url, impersonate="chrome", timeout=60)
    domain = urlparse(url).hostname
    if output == "html":
        return response.text
    content = BeautifulSoup(response.text, "html.parser")

    if domain == "scrapeme.live":
        content = pokemonScrape(content)
    elif domain == "webscraper.io":
        content = carScrape(content)
    elif domain == "books.toscrape.com":
        content = bookScrape(content)
    else:
        return response.text
    return content
