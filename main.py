# main.py
from fastapi import FastAPI
from scraper import update_rates, get_latest_rates
import asyncio

app = FastAPI(title="Crypto + Forex Rates API", version="1.0")

# In-memory cache (optional, for faster API responses)
CACHE = {
    "data": None
}

# ---------- Endpoint: Get latest rates ----------
@app.get("/rates")
async def rates():
    """
    Returns the latest forex and crypto rates.
    """
    # Use cache if available
    if CACHE["data"]:
        return {"source": "cache", "data": CACHE["data"]}

    data = await get_latest_rates()
    CACHE["data"] = data
    return {"source": "live", "data": data}

# ---------- Endpoint: Force update ----------
@app.post("/update")
async def force_update():
    """
    Force an update of all rates.
    """
    data = await update_rates()
    CACHE["data"] = data
    return {"message": "Rates updated", "data": data}

# ---------- Root ----------
@app.get("/")
async def root():
    return {"message": "Welcome to Crypto + Forex Rates API. Visit /rates to get latest data."}

# ---------- Optional: Background scheduler ----------
# You can schedule `update_rates` periodically (e.g., every 5 minutes)
# using libraries like APScheduler or just a background asyncio task.
