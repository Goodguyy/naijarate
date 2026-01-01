from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite_utils
from database import DB_PATH

app = FastAPI(title="NaijaRate")

# Static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ----------------------------
# Home Page
# ----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    try:
        db = sqlite_utils.Database(DB_PATH)
        rows = list(db["rates"].rows_ordered_by("timestamp desc", limit=1))
        latest = rows[0] if rows else None
    except Exception as e:
        latest = None

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "latest": latest,
        },
    )

# ----------------------------
# API: Latest Rates
# ----------------------------
@app.get("/api/latest")
def api_latest():
    try:
        db = sqlite_utils.Database(DB_PATH)
        rows = list(db["rates"].rows_ordered_by("timestamp desc", limit=1))
        if not rows:
            return JSONResponse({"status": "empty"})
        return rows[0]
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )

# ----------------------------
# Health Check (VERY IMPORTANT)
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
