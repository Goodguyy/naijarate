from sources.cex_rates import get_forex
from sources.crypto import get_crypto_prices
from database import cache
from datetime import datetime

DEFAULT_USD_NGN = 1500

def fetch_all():
    if "data" in cache:
        return cache["data"]

    forex = get_forex() or {}
    usd_rate = forex.get("USD", {}).get("avg", DEFAULT_USD_NGN)
    if not isinstance(usd_rate, (int,float)):
        usd_rate = DEFAULT_USD_NGN

    crypto = get_crypto_prices(usd_rate)

    payload = {
        "forex": forex,
        "crypto": crypto,
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    cache["data"] = payload
    return payload
