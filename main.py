# main.py
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from scraper import update_rates, get_latest_rates  # make sure get_latest_rates exists in scraper.py
from pathlib import Path
from jinja2 import Template

app = FastAPI(title="NaijaRate")

# Allow cross-origin requests (optional, useful if front-end is separate)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load HTML template
TEMPLATE_FILE = Path(__file__).parent / "templates" / "index.html"
with open(TEMPLATE_FILE, "r") as f:
    html_template = Template(f.read())

# Startup task to fetch initial rates
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_rates())  # run in background
    print("Initial rates update started...")


@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Serve the main HTML page with latest rates.
    """
    rates = get_latest_rates()
    return html_template.render(
        forex=rates.get("forex"),
        crypto=rates.get("crypto")
    )


@app.get("/api", response_class=JSONResponse)
async def api():
    """
    Return latest rates as JSON.
    """
    rates = get_latest_rates()
    return JSONResponse(content=rates)


# Optional endpoint to force update rates
@app.post("/update")
async def manual_update():
    """
    Trigger an update manually (for testing or cron jobs).
    """
    try:
        await update_rates()
        return {"status": "success", "message": "Rates updated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=10000)
