from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite_utils

from database import DB_PATH

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = sqlite_utils.Database(DB_PATH)
    table = db["rates"]

    row = table.order_by("-timestamp").first()

    if not row:
        # SAFE EMPTY STATE
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "rate": None,
                "history": []
            }
        )

    history = list(table.order_by("-timestamp").limit(10))

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "rate": row,
            "history": history
        }
    )
