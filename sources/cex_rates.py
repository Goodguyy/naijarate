from .forex_sources import all_official_sources, all_blackmarket_sources
import requests

# ----------------- CEX P2P -----------------
def binance_p2p():
    try:
        url = "https://api.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {"asset":"USDT","fiat":"NGN","tradeType":"SELL","page":1,"rows":5}
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()
        prices = [float(adv["adv"]["price"]) for adv in data.get("data", [])]
        if prices:
            return sum(prices)/len(prices)
    except:
        return None

def kucoin_p2p():
    try:
        url = "https://www.kucoin.com/_api/c2c/market/active?coinId=1&currency=NGN&type=sell&currentPage=1&paymentMethod=0"
        r = requests.get(url, timeout=10)
        data = r.json()
        prices = [float(x["price"]) for x in data.get("data", {}).get("items", [])]
        if prices:
            return sum(prices)/len(prices)
    except:
        return None

def bybit_p2p():
    try:
        url = "https://api.bybit.com/spot/p2p/offers?asset=USDT&fiat=NGN&type=sell&page=1&limit=5"
        r = requests.get(url, timeout=10)
        data = r.json()
        prices = [float(x["price"]) for x in data.get("result", [])]
        if prices:
            return sum(prices)/len(prices)
    except:
        return None

def gate_p2p():
    try:
        url = "https://api.gateio.ws/api2/1/p2p/offers?currency=NGN&asset=USDT&type=sell&limit=5"
        r = requests.get(url, timeout=10)
        data = r.json()
        prices = [float(x["price"]) for x in data.get("data", [])]
        if prices:
            return sum(prices)/len(prices)
    except:
        return None

def mexc_p2p():
    try:
        url = "https://www.mexc.com/api/v2/p2p/offers?asset=USDT&fiat=NGN&type=sell&page=1&limit=5"
        r = requests.get(url, timeout=10)
        data = r.json()
        prices = [float(x["price"]) for x in data.get("data", [])]
        if prices:
            return sum(prices)/len(prices)
    except:
        return None

def bitget_p2p():
    try:
        url = "https://c2c.bitget.com/api/v1/p2p/offers?asset=USDT&fiat=NGN&type=sell&page=1&limit=5"
        r = requests.get(url, timeout=10)
        data = r.json()
        prices = [float(x["price"]) for x in data.get("data", [])]
        if prices:
            return sum(prices)/len(prices)
    except:
        return None

def luno_p2p():
    try:
        url = "https://api.luno.com/api/1/orderbook?pair=XBTNGN"
        r = requests.get(url, timeout=10)
        data = r.json()
        asks = data.get("asks", [])
        if asks:
            prices = [float(a["price"]) for a in asks]
            return sum(prices)/len(prices)
    except:
        return None

# ----------------- Aggregate -----------------
def get_forex():
    results = {}
    # Official
    official_rates = all_official_sources()
    blackmarket_rates = all_blackmarket_sources()
    cex_rates = []
    for fn in [binance_p2p, kucoin_p2p, bybit_p2p, gate_p2p, mexc_p2p, bitget_p2p, luno_p2p]:
        try:
            rate = fn()
            if rate:
                cex_rates.append(rate)
        except:
            continue

    combined_blackmarket = blackmarket_rates + cex_rates

    if official_rates:
        results["USD"] = {"avg": round(sum(official_rates)/len(official_rates),2), 
                          "min": round(min(official_rates),2),
                          "max": round(max(official_rates),2),
                          "sources": len(official_rates)}
    if combined_blackmarket:
        results["USD_blackmarket"] = {"avg": round(sum(combined_blackmarket)/len(combined_blackmarket),2),
                                      "min": round(min(combined_blackmarket),2),
                                      "max": round(max(combined_blackmarket),2),
                                      "sources": len(combined_blackmarket)}
    return results
