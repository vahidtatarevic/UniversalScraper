from fastapi import FastAPI
from functions import scrape_function

app = FastAPI()

@app.get("/scrape/{url:path}")
def scrape(url: str):
    response = scrape_function(url)
    return response