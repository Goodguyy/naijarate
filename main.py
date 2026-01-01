from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from scraper import get_latest_rates

app = FastAPI()

# Serve static files (CSS)
app.mount("/static", StaticFiles(directory="sources/static"), name="static")

# Jinja2 templates folder
templates = Jinja2Templates(directory="sources/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    data = await get_latest_rates()
    return templates.TemplateResponse("index.html", {"request": request, "data": data})


@app.get("/rates")
async def rates():
    # API endpoint for JSON
    return await get_latest_rates()
