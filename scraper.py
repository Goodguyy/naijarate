import asyncio
from datetime import datetime
import sqlite_utils
import json

from database import DB_PATH
from sources.binance import fetch_binance_rate
from sources.blogs import fetch_blog_rates
from sources.crypto import fetch_crypto_rates
from sources.aggregator import aggregate_rates
from sources.forex_sources import fetch_official_forex, fetch_blackmarket_forex

CURRENCIES = ["USD", "GBP", "EUR", "CAD"]

async def update_rates():
    # 1️⃣ Fetch official forex rates
    official_rates = await fetch_official_forex(CURRENCIES)
    
    # 2️⃣ Fetch black market rates from multiple sources
    blackmarket_rates = await fetch_blackmarket_forex(CURRENCIES)

    # 3️⃣ Fetch Binance P2P USD rate (optional fallback)
    try:
        binance_rate = await fetch_binance_rate("USD")
    except Exception:
        binance_rate = None
        print("⚠️ Binance rate fetch failed, skipping")

    # 4️⃣ Fetch top crypto rates from CoinGecko (converted to NGN using USD rate)
    usd_to_ngn = official_rates.get("USD") or blackmarket_rates.get("USD") or 800  # fallback
    try:
        crypto_rates = await fetch_crypto_rates(usd_to_ngn)
    except Exception:
        crypto_rates = {}
        print("⚠️ Crypto fetch failed, skipping")

    # 5️⃣ Aggregate forex rates (official + black market + binance)
    combined_forex = list(official_rates.values()) + list(blackmarket_rates.values())
    if binance_rate:
        combined_forex.append(binance_rate)

    forex_result = aggregate_rates(combined_forex)

    if not forex_result:
        print("❌ No forex data available")
        return

    # 6️⃣ Save all data to SQLite database
    db = sqlite_utils.Database(DB_PATH)
    table = db["rates"]

    table.insert({
        "timestamp": datetime.utcnow().isoformat(),
        "avg_rate": forex_result.get("avg"),
        "min_rate": forex_result.get("min"),
        "max_rate": forex_result.get("max"),
        "sources": forex_result.get("sources"),
        "official": json.dumps(official_rates),
        "blackmarket": json.dumps(blackmarket_rates),
        "crypto": json.dumps(crypto_rates)
    }, alter=True)

    print("✅ Updated forex and crypto rates successfully")
    print("Forex avg:", forex_result.get("avg"))
    print("Crypto sample:", {k: v for k, v in list(crypto_rates.items())[:3]})  # show 3 coins

if __name__ == "__main__":
    asyncio.run(update_rates())
