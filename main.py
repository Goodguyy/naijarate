import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from scraper import fetch_all

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="NaijaRate")

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

# Templates folder
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    data = fetch_all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "forex": data.get("forex", {}),
            "crypto": data.get("crypto", {}),
            "updated": data.get("updated", "N/A")
        }
    )

@app.get("/rates", response_class=JSONResponse)
def api_rates():
    data = fetch_all()
    return {
        "forex": data.get("forex", {}),
        "crypto": data.get("crypto", {})
    }
