from urllib.parse import urlparse

from bs4 import BeautifulSoup
from curl_cffi import requests

from app.scrapers.json_ld import extract_json_ld
from app.scrapers.parser import book_scrape, car_scrape, pokemon_scrape


def scrape_function(url, output="json"):
    response = requests.get(url, impersonate="chrome", timeout=60)
    domain = urlparse(url).hostname
    if output == "html":
        return response.text
    content = BeautifulSoup(response.text, "html.parser")

    if domain == "scrapeme.live":
        content = pokemon_scrape(content)
    elif domain == "webscraper.io":
        content = car_scrape(content)
    elif domain == "books.toscrape.com":
        content = book_scrape(content)
    else:
        json_ld = extract_json_ld(content)
        if not json_ld:
            return response.text
        return json_ld
    return content
