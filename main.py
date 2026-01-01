from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite_utils

from database import DB_PATH

app = FastAPI(title="NaijaRate")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = sqlite_utils.Database(DB_PATH)
    latest = list(db["rates"].rows_where(order_by="-timestamp", limit=1))
    history = list(db["rates"].rows_where(order_by="-timestamp", limit=15))

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "latest": latest, "history": history}
    )
