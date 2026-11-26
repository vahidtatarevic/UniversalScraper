from typing import Annotated, Literal

from curl_cffi.requests.exceptions import RequestException
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from app.auth import current_user
from app.scrapers.base import scrape_function
from app.scrapers.safety import is_public_url

router = APIRouter()


@router.get("/scrape")
def scrape(
    url: str,
    username: Annotated[str, Depends(current_user)],
    output: Literal["json", "html"] = "json",
):
    if not url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400, detail="URL must start with http:// or https://"
        )
    if not is_public_url(url):
        raise HTTPException(status_code=400, detail="URL is not allowed.")
    try:
        response = scrape_function(url, output)
    except RequestException:
        raise HTTPException(status_code=502, detail="Failed to fetch the page.")
    except (AttributeError, IndexError, ValueError, TypeError):
        raise HTTPException(status_code=422, detail="Page structure not recognised.")

    if not response:
        raise HTTPException(status_code=404, detail="No data found.")
    if isinstance(response, str):
        return HTMLResponse(response)
    return response
