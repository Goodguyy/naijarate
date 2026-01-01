from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scraper import get_latest_rates

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    rates = await get_latest_rates()
    return templates.TemplateResponse("index.html", {"request": request, "rates": rates})


@app.get("/rates")
async def rates_api():
    return await get_latest_rates()
