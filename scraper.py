import asyncio
from datetime import datetime
import sqlite_utils
import json

from database import DB_PATH
from sources.crypto import fetch_crypto_rates
from sources.cex_rates import fetch_cex_ngn_rate
from sources.aggregator import aggregate_rates

async def update_rates():
    # 1️⃣ Get NGN rate from multiple CEXs
    cex_rates = await fetch_cex_ngn_rate()

    if not cex_rates:
        print("❌ No CEX data available")
        return

    usd_to_ngn = aggregate_rates(list(cex_rates.values()))["avg"]

    # 2️⃣ Crypto prices
    crypto = await fetch_crypto_rates(usd_to_ngn)

    # 3️⃣ Save
    db = sqlite_utils.Database(DB_PATH)
    table = db["rates"]

    table.insert(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "usd_ngn": usd_to_ngn,
            "cex": json.dumps(cex_rates),
            "crypto": json.dumps(crypto),
        },
        alter=True,
    )

    print("✅ Rates updated:", usd_to_ngn)


if __name__ == "__main__":
    asyncio.run(update_rates())
