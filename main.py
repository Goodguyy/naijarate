from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sqlite_utils
import json
from database import DB_PATH

app = FastAPI(title="NaijaRate 🇳🇬")

# Home route
@app.get("/", response_class=HTMLResponse)
def home():
    db = sqlite_utils.Database(DB_PATH)
    table = db["rates"]
    
    # Get the latest rate
    try:
        latest = list(table.rows_ordered("timestamp desc"))[0]
    except IndexError:
        latest = None

    html = "<h1>🇳🇬 NaijaRates</h1>"

    if latest:
        html += f"""
        <p>Last updated: {latest['timestamp']}</p>
        <p>Average Forex Rate (NGN): {latest['avg_rate']}</p>
        <h2>Official Rates:</h2>
        <pre>{json.dumps(json.loads(latest['official']), indent=2)}</pre>
        <h2>Blackmarket Rates:</h2>
        <pre>{json.dumps(json.loads(latest['blackmarket']), indent=2)}</pre>
        <h2>Crypto Rates:</h2>
        <pre>{json.dumps(json.loads(latest['crypto']), indent=2)}</pre>
        """
    else:
        html += "<p>No data yet. Refreshing soon...</p>"

    return HTMLResponse(content=html)
