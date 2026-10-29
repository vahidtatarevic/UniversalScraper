from bs4 import BeautifulSoup
from curl_cffi import requests

from app.scrapers.parser import bookScrape, carScrape, pokemonScrape


def scrapeFunction(url, output="json"):
    response = requests.get(url, impersonate="chrome", timeout=60)
    if output == "html":
        return response.text
    content = BeautifulSoup(response.text, "html.parser")

    if "scrapeme.live" in url:
        content = pokemonScrape(content)
    elif "webscraper.io" in url:
        content = carScrape(content)
    elif "books.toscrape.com" in url:
        content = bookScrape(content)
    else:
        return response.text
    return content
