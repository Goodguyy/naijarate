import asyncio
from datetime import datetime
import sqlite_utils
import json

from database import DB_PATH
from sources.binance import fetch_binance_rate
from sources.crypto import fetch_crypto_rates
from sources.cex_rates import fetch_cex_ngn_rate
from sources.forex_sources import fetch_official_forex, fetch_blackmarket_forex
from sources.aggregator import aggregate_rates

async def update_rates():
    # 1️⃣ Fetch official forex rates (USD, GBP, EUR, CAD)
    official_rates = await fetch_official_forex(["USD", "GBP", "EUR", "CAD"])
    
    # 2️⃣ Fetch black market rates from multiple sources
    blackmarket_rates = await fetch_blackmarket_forex(["USD", "GBP", "EUR", "CAD"])

    # 3️⃣ Fetch CEX USD/NGN rates from Binance, OKX, KuCoin, Bybit
    cex_rates = await fetch_cex_ngn_rate("USD")  # returns list of numbers
    usd_to_ngn = aggregate_rates(cex_rates)["avg"] if cex_rates else \
                 official_rates.get("USD") or blackmarket_rates.get("USD") or 800

    # 4️⃣ Fetch Binance P2P rates (optional fallback)
    binance_rate = await fetch_binance_rate("USD")
    if binance_rate:
        cex_rates.append(binance_rate)

    # 5️⃣ Fetch top crypto rates from CoinGecko (converted to NGN)
    crypto_rates = await fetch_crypto_rates(usd_to_ngn)

    # 6️⃣ Aggregate all forex rates
    all_forex_values = (
        list(official_rates.values()) +
        list(blackmarket_rates.values()) +
        cex_rates  # already list
    )
    forex_result = aggregate_rates(all_forex_values)

    if not forex_result:
        print("❌ No forex data available")
        return

    # 7️⃣ Save all rates to SQLite database
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
        "cex": json.dumps(cex_rates),
        "crypto": json.dumps(crypto_rates)
    }, alter=True)

    print("✅ Updated forex and crypto rates:", forex_result["avg"])

if __name__ == "__main__":
    asyncio.run(update_rates())
