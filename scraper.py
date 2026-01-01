import asyncio
from datetime import datetime
import sqlite_utils
import json
from database import DB_PATH
from sources.binance import fetch_binance_rate
from sources.blogs import fetch_blog_rates
from sources.aggregator import aggregate_rates
from sources.crypto import fetch_crypto_rates

async def update_rates():
    try:
        # ----- 1. Fetch forex rates -----
        print("Fetching forex rates from Binance...")
        binance_usd = await fetch_binance_rate("USD")
        binance_gbp = await fetch_binance_rate("GBP")
        binance_eur = await fetch_binance_rate("EUR")
        binance_cad = await fetch_binance_rate("CAD")

        print("Fetching blog rates...")
        blog_rates = await fetch_blog_rates()

        # Aggregate rates safely
        result_usd = aggregate_rates([binance_usd], blog_rates) or {}
        result_gbp = aggregate_rates([binance_gbp], blog_rates) or {}
        result_eur = aggregate_rates([binance_eur], blog_rates) or {}
        result_cad = aggregate_rates([binance_cad], blog_rates) or {}

        if not result_usd.get("avg"):
            print("❌ No USD rates fetched, aborting.")
            return

        # ----- 2. Fetch crypto rates using USD → NGN -----
        usd_to_ngn = result_usd["avg"]
        crypto_prices = await fetch_crypto_rates(usd_to_ngn)

        # ----- 3. Save everything to DB -----
        db = sqlite_utils.Database(DB_PATH)
        table = db["rates"]

        table.insert({
            "timestamp": datetime.utcnow().isoformat(),
            "usd_avg": result_usd.get("avg"),
            "usd_min": result_usd.get("min"),
            "usd_max": result_usd.get("max"),
            "gbp_avg": result_gbp.get("avg"),
            "eur_avg": result_eur.get("avg"),
            "cad_avg": result_cad.get("avg"),
            "sources": result_usd.get("sources", 0),
            "crypto": json.dumps(crypto_prices)  # store as string for templates
        }, alter=True)

        print("✅ Updated forex and crypto rates")

    except Exception as e:
        print("❌ Error updating rates:", e)


if __name__ == "__main__":
    asyncio.run(update_rates())
