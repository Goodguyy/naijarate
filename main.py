from fastapi import FastAPI
from fastapi.responses import JSONResponse
from scraper import update_rates, get_latest_rates
import asyncio
import sqlite_utils
from database import DB_PATH
import json

app = FastAPI(title="Naija Rate API")

# --------------------------
# Healthcheck route
# --------------------------
@app.get("/health")
def healthcheck():
    return {"status": "ok"}

# --------------------------
# Update rates route
# --------------------------
@app.get("/update")
async def update():
    try:
        # Run the scraper to fetch and store latest rates
        await update_rates()
        return {"status": "success", "message": "Rates updated successfully"}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

# --------------------------
# Get latest stored rates
# --------------------------
@app.get("/rates")
def get_rates():
    try:
        db = sqlite_utils.Database(DB_PATH)
        table = db["rates"]
        # Fetch latest row
        rows = list(table.rows_where(order_by="timestamp DESC", limit=1))
        if not rows:
            return JSONResponse({"status": "error", "message": "No rates available"}, status_code=404)

        row = rows[0]

        # Convert stored JSON fields back to dict
        official = json.loads(row.get("official") or "{}")
        blackmarket = json.loads(row.get("blackmarket") or "{}")
        crypto = json.loads(row.get("crypto") or "{}")

        return {
            "status": "success",
            "timestamp": row.get("timestamp"),
            "avg_rate": row.get("avg_rate"),
            "min_rate": row.get("min_rate"),
            "max_rate": row.get("max_rate"),
            "sources": row.get("sources"),
            "official": official,
            "blackmarket": blackmarket,
            "crypto": crypto
        }

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
