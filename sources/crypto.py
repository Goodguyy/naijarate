import requests

COINS = {
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "dash": "dash",
    "solana": "solana",
    "tether": "tether"
}

def get_crypto_prices(usd_ngn):
    try:
        ids = ",".join(COINS.values())
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": ids, "vs_currencies": "usd"},
            timeout=10
        )
        data = r.json()
    except:
        return {}

    result = {}
    for name, cid in COINS.items():
        usd = data.get(cid, {}).get("usd")
        if usd:
            result[name] = {
                "USD": usd,
                "NGN": round(usd * usd_ngn, 2)
            }

    return result
