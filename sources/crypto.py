import requests

COINS = {
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "dash": "dash",
    "solana": "solana",
    "tether": "tether"
}

def get_crypto_prices(usd_ngn: float):
    result = {}

    try:
        ids = ",".join(COINS.values())
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": ids, "vs_currencies": "usd"},
            timeout=10
        )

        if r.status_code != 200:
            return result

        data = r.json()
    except Exception:
        return result

    for name, cid in COINS.items():
        usd_price = data.get(cid, {}).get("usd")

        if isinstance(usd_price, (int, float)):
            result[name] = {
                "USD": usd_price,
                "NGN": round(usd_price * usd_ngn, 2)
            }

    return result
