from curl_cffi import requests
from bs4 import BeautifulSoup
from parser import pokemonScrape, carScrape, bookScrape


def scrape_function(url):
    response = requests.get(url, impersonate="chrome", timeout = 60)
    content = BeautifulSoup(response.text, "html.parser")
    if "scrapeme.live" in url:
        content = pokemonScrape(content)
    elif "webscraper.io" in url:
        content = carScrape(content)
    elif "books.toscrape.com" in url:
        content = bookScrape(content)
    else:
        return {
            "title": content.title.text.strip() if content.title else None,
            "text": content.get_text(separator=" ", strip=True)[:1000]
        }
    return content

