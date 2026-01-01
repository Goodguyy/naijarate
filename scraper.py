# sources/crypto.py
import requests

TOP_COINS = ["bitcoin", "ethereum", "tether", "binancecoin", "cardano"]  # extend as needed

def get_crypto_prices(usd_rate=1500):
    """
    Fetch top crypto prices from CoinGecko (free API) and return USD + NGN values.
    usd_rate: USD to NGN conversion rate from forex sources
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(TOP_COINS),
        "vs_currencies": "usd",
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return {}  # fallback if API fails

    result = {}
    for coin in TOP_COINS:
        price_usd = data.get(coin, {}).get("usd")
        if price_usd is None:
            continue
        result[coin] = {
            "USD": price_usd,
            "NGN": round(price_usd * usd_rate, 2)
        }

    return result
