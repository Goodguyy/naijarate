import requests

TOP_COINS = ["bitcoin","ethereum","tether","binancecoin","ripple"]

def get_crypto_prices(usd_rate=1500):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(TOP_COINS)}&vs_currencies=usd"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        results = {}
        for coin, values in data.items():
            usd = values.get("usd")
            results[coin] = {
                "usd": usd,
                "ngn": round(usd*usd_rate,2) if usd else None
            }
        # Also add USDT
        results["tether"] = {"usd": 1, "ngn": usd_rate}
        return results
    except:
        return {}
