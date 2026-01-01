import asyncio
from datetime import datetime
import sqlite_utils

from database import DB_PATH
from sources.binance import fetch_binance_rate
from sources.blogs import fetch_blog_rates
from sources.aggregator import aggregate_rates

async def update_rates():
    # Fetch Binance rates
    binance_rate = await fetch_binance_rate("USD")
    
    # Fetch blog rates
    blog_rates = await fetch_blog_rates()

    # Aggregate all rates
    result = aggregate_rates([binance_rate], blog_rates)
    if not result:
        return

    # Save to SQLite database
    db = sqlite_utils.Database(DB_PATH)
    table = db["rates"]

    table.insert({
        "timestamp": datetime.utcnow().isoformat(),
        "avg_rate": result["avg"],
        "min_rate": result["min"],
        "max_rate": result["max"],
        "sources": result["sources"]
    }, alter=True)

    print("✅ Updated rate:", result["avg"])

if __name__ == "__main__":
    asyncio.run(update_rates())
