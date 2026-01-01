from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from scraper import fetch_rates_sync
from pathlib import Path

app = FastAPI()

# Serve static CSS
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

@app.get("/")
def home():
    rates = fetch_rates_sync()
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Replace placeholders in HTML
    html = html.replace("{{FOREX_RATES}}", str(rates["data"]["forex"]))
    html = html.replace("{{CRYPTO_USD}}", str(rates["data"]["crypto_usd"]))
    html = html.replace("{{CRYPTO_NGN}}", str(rates["data"]["crypto_ngn"]))
    return HTMLResponse(content=html)

@app.get("/rates")
def rates():
    return fetch_rates_sync()
