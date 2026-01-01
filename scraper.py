import asyncio
from datetime import datetime
import sqlite_utils
from database import DB_PATH
from sources.binance import fetch_binance_rate
from sources.blogs import fetch_blog_rates
from sources.aggregator import aggregate_rates

async def update_rates():
    # Fetch Binance rates
    try:
        binance_rate = await fetch_binance_rate("USD")
        if binance_rate is None:
            print("⚠️ Binance returned no prices")
    except Exception as e:
        print("❌ Error fetching Binance rates:", e)
        binance_rate = None

    # Fetch blog rates
    try:
        blog_rates = await fetch_blog_rates()
        if not blog_rates:
            print("⚠️ No blog rates returned")
    except Exception as e:
        print("❌ Error fetching blog rates:", e)
        blog_rates = []

    # Aggregate all rates safely
    result = aggregate_rates([binance_rate], blog_rates)
    if not result or result["sources"] == 0:
        print("⚠️ No rates to update")
        return

    # Save to SQLite database
    db = sqlite_utils.Database(DB_PATH)
    table = db["rates"]

    table.insert({
        "timestamp": datetime.utcnow().isoformat(),
        "avg_rate": result["avg_rate"],
        "min_rate": result["min_rate"],
        "max_rate": result["max_rate"],
        "median": result.get("median"),
        "sources": result["sources"],
        "raw_data": str(result["raw_data"])
    }, alter=True)

    print("✅ Updated rates:", result)

if __name__ == "__main__":
    asyncio.run(update_rates())
