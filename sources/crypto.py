import requests

def coingecko_prices(usd_to_ngn):
    coins = ["bitcoin", "ethereum", "dash", "solana", "tether"]
    url = "https://api.coingecko.com/api/v3/simple/price"
    try:
        r = requests.get(url, params={"ids": ",".join(coins), "vs_currencies": "usd"}, timeout=10)
        r.raise_for_status()
        data = r.json()
        result = {}
        for coin, v in data.items():
            usd = v.get("usd")
            if usd:
                result[coin] = {"USD": round(usd, 2), "NGN": round(usd*usd_to_ngn, 2)}
        return result
    except Exception:
        return {}

def coinmarketcap_prices(usd_to_ngn, api_key=None):
    try:
        headers = {"X-CMC_PRO_API_KEY": api_key} if api_key else {}
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        coins = ["1","1027","131"]  # BTC, ETH, etc
        r = requests.get(url, headers=headers, params={"id": ",".join(coins)}, timeout=10)
        r.raise_for_status()
        data = r.json().get("data", {})
        result = {}
        for k, v in data.items():
            usd = v["quote"]["USD"]["price"]
            coin_name = v["name"].lower()
            result[coin_name] = {"USD": round(usd,2), "NGN": round(usd*usd_to_ngn,2)}
        return result
    except Exception:
        return {}

def binance_prices(usd_to_ngn):
    try:
        coins = ["BTCUSDT","ETHUSDT","DASHUSDT","SOLUSDT","USDTUSDT"]
        result = {}
        for sym in coins:
            r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={sym}", timeout=5)
            r.raise_for_status()
            data = r.json()
            coin = sym[:-4].lower() if sym != "USDTUSDT" else "tether"
            usd = float(data["price"])
            result[coin] = {"USD": round(usd,2), "NGN": round(usd*usd_to_ngn,2)}
        return result
    except Exception:
        return {}

def okx_prices(usd_to_ngn):
    try:
        coins = ["BTC-USDT","ETH-USDT","DASH-USDT","SOL-USDT","USDT-USDT"]
        result = {}
        for sym in coins:
            r = requests.get(f"https://www.okx.com/api/v5/market/ticker?instId={sym}", timeout=5)
            r.raise_for_status()
            data = r.json()
            coin = sym.split("-")[0].lower()
            usd = float(data["data"][0]["last"])
            result[coin] = {"USD": round(usd,2), "NGN": round(usd*usd_to_ngn,2)}
        return result
    except Exception:
        return {}

def aggregate_crypto(usd_to_ngn):
    """Aggregate multiple crypto sources"""
    sources = [coingecko_prices, binance_prices, okx_prices]
    data = {}
    for fn in sources:
        try:
            d = fn(usd_to_ngn)
            for coin, v in d.items():
                if coin not in data:
                    data[coin] = []
                data[coin].append(v)
        except Exception:
            continue

    # Compute average USD & NGN per coin
    final = {}
    for coin, lst in data.items():
        if not lst:
            continue
        avg_usd = round(sum([v["USD"] for v in lst])/len(lst),2)
        avg_ngn = round(sum([v["NGN"] for v in lst])/len(lst),2)
        final[coin] = {"USD": avg_usd, "NGN": avg_ngn}
    return final
