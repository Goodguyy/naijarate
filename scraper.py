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

async def update_rates():
    # 1️⃣ Fetch official forex rates
    official_rates = await fetch_official_forex(["USD","GBP","EUR","CAD"])
    
    # 2️⃣ Fetch black market rates from multiple sources
    blackmarket_rates = await fetch_blackmarket_forex(["USD","GBP","EUR","CAD"])

    # 3️⃣ Fetch Binance/USD P2P rates (optional fallback)
    binance_rate = await fetch_binance_rate("USD")
    
    # 4️⃣ Fetch top crypto rates from CoinGecko (converted to NGN using USD rate)
    usd_to_ngn = official_rates.get("USD") or (blackmarket_rates.get("USD") or 800) # fallback
    crypto_rates = await fetch_crypto_rates(usd_to_ngn)
    
    # 5️⃣ Aggregate forex rates (official + blackmarket + binance)
    forex_result = aggregate_rates(
        list(official_rates.values()) + list(blackmarket_rates.values()) + ([binance_rate] if binance_rate else [])
    )

    if not forex_result:
        print("❌ No forex data available")
        return

    # 6️⃣ Save to SQLite database
    db = sqlite_utils.Database(DB_PATH)
    table = db["rates"]

    table.insert({
        "timestamp": datetime.utcnow().isoformat(),
        "avg_rate": forex_result["avg"],
        "min_rate": forex_result["min"],
        "max_rate": forex_result["max"],
        "sources": forex_result["sources"],
        "official": json.dumps(official_rates),
        "blackmarket": json.dumps(blackmarket_rates),
        "crypto": json.dumps(crypto_rates)
    }, alter=True)

    print("✅ Updated forex and crypto rates:", forex_result["avg"])

if __name__ == "__main__":
    asyncio.run(update_rates())
