import httpx
import statistics

BINANCE_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

async def fetch_binance_rate(asset="USD"):
    payload = {
        "asset": asset,
        "fiat": "NGN",
        "tradeType": "SELL",
        "page": 1,
        "rows": 5
    }

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(BINANCE_URL, json=payload)
        r.raise_for_status()
        data = r.json()["data"]

    prices = [float(ad["adv"]["price"]) for ad in data]
    return statistics.median(prices)
