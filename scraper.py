import asyncio
from datetime import datetime
import sqlite_utils
import json

from database import DB_PATH
from sources.forex_sources import fetch_official_forex, fetch_blackmarket_forex
from sources.cex_rates import binance_usdt_ngn, okx_usdt_ngn, kucoin_usdt_ngn, bybit_usdt_ngn
from sources.crypto import fetch_crypto_rates
from sources.aggregator import aggregate_rates


async def update_rates():
    # ----------------------------
    # 1️⃣ Fetch official forex rates
    # ----------------------------
    official_rates = await fetch_official_forex(["USD", "EUR", "GBP", "CAD"])
    
    # ----------------------------
    # 2️⃣ Fetch black market rates
    # ----------------------------
    blackmarket_rates = await fetch_blackmarket_forex(["USD", "EUR", "GBP", "CAD"])
    
    # ----------------------------
    # 3️⃣ Fetch CEX USDT → NGN rates
    # ----------------------------
    cex_tasks = [
        binance_usdt_ngn(),
        okx_usdt_ngn(),
        kucoin_usdt_ngn(),
        bybit_usdt_ngn(),
    ]
    
    cex_rates_list = await asyncio.gather(*cex_tasks, return_exceptions=True)
    # Filter out failed tasks
    cex_rates = [r for r in cex_rates_list if isinstance(r, (int, float))]
    
    # ----------------------------
    # 4️⃣ Determine USD → NGN rate for crypto
    # ----------------------------
    usd_to_ngn = official_rates.get("USD") or blackmarket_rates.get("USD") or (cex_rates[0] if cex_rates else 800)
    
    # ----------------------------
    # 5️⃣ Fetch top crypto prices (USD + NGN)
    # ----------------------------
    crypto_rates = await fetch_crypto_rates(usd_to_ngn)
    
    # ----------------------------
    # 6️⃣ Aggregate all forex rates
    # ----------------------------
    combined_forex = list(official_rates.values()) + list(blackmarket_rates.values()) + cex_rates
    forex_result = aggregate_rates(combined_forex)
    
    if not forex_result:
        print("❌ No forex data available")
        return
    
    # ----------------------------
    # 7️⃣ Save everything to SQLite
    # ----------------------------
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
        "cex_rates": json.dumps(cex_rates),
        "crypto": json.dumps(crypto_rates)
    }, alter=True)
    
    print("✅ Updated rates successfully")
    print("Forex avg:", forex_result["avg"])
    print("Crypto sample:", {k: crypto_rates[k] for k in list(crypto_rates)[:3]})


if __name__ == "__main__":
    asyncio.run(update_rates())
