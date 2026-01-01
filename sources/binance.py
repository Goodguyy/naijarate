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

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(BINANCE_URL, json=payload)
            r.raise_for_status()
            data = r.json().get("data", [])

        prices = [float(ad["adv"]["price"]) for ad in data if "adv" in ad and "price" in ad["adv"]]

        if not prices:
            print("Binance returned no prices")
            return None

        return statistics.median(prices)

    except Exception as e:
        print(f"Binance fetch failed: {e}")
        return None
