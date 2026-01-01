from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from scraper import fetch_all

app = FastAPI(title="NaijaRate")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    data = fetch_all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, **data}
    )

@app.get("/rates", response_class=JSONResponse)
def api_rates():
    data = fetch_all()
    return {
        "forex": data["forex"],
        "crypto": data["crypto"]
    }
