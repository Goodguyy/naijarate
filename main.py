from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from scraper import fetch_rates_sync
from pathlib import Path
from fastapi import Request

app = FastAPI()

# Serve static CSS
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    rates = fetch_rates_sync()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "FOREX_RATES": rates["data"]["forex"],
        "CRYPTO_USD": rates["data"]["crypto_usd"],
        "CRYPTO_NGN": rates["data"]["crypto_ngn"]
    })

@app.get("/rates")
def rates():
    return fetch_rates_sync()
