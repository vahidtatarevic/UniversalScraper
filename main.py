from fastapi import FastAPI
from functions import scrape_function
from fastapi import HTTPException
app = FastAPI()

@app.get("/scrape/")
def scrape(url: str):
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    try:
        response = scrape_function(url)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to scrape the page.")

    if not response:
        raise HTTPException(status_code=404, detail="No data found.")
    return response