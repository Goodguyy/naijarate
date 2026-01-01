import httpx

COINS = ["bitcoin", "ethereum", "binancecoin", "solana", "tether"]
COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"

async def fetch_crypto_rates(usd_to_ngn):
    """
    Fetch crypto prices in USD and convert to NGN.
    Returns a dict like:
    {
        "BTC": {"USD": 27200, "NGN": 22304000},
        "ETH": {"USD": 1800, "NGN": 1476000},
        ...
    }
    """
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            params = {
                "ids": ",".join(COINS),
                "vs_currencies": "usd"
            }
            r = await client.get(COINGECKO_API, params=params)
            r.raise_for_status()
            data = r.json()

        result = {}
        for coin, v in data.items():
            usd_price = round(v.get("usd", 0), 2)  # rounded USD price
            ngn_price = round(usd_price * usd_to_ngn)
            result[coin.upper()] = {"USD": usd_price, "NGN": ngn_price}

        return result

    except Exception as e:
        print("❌ Crypto fetch error:", e)
        return {}

