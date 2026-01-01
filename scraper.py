from sources.cex_rates import get_forex
from sources.crypto import get_crypto_prices
from database import cache
from datetime import datetime

def fetch_all():
    if "data" in cache:
        return cache["data"]

    forex = get_forex()
    usd_rate = forex.get("USD", {}).get("avg", 1500)

    crypto = get_crypto_prices(usd_rate)

    payload = {
        "forex": forex,
        "crypto": crypto,
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    cache["data"] = payload
    return payload
