import requests
from bs4 import BeautifulSoup

# ----------------- Official Sources -----------------
def exchangerate_host(cur="USD"):
    try:
        r = requests.get(f"https://api.exchangerate.host/latest?base={cur}", timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("rates", {}).get("NGN")
    except Exception:
        return None

def cbn_official():
    try:
        r = requests.get("https://www.cbn.gov.ng/rates/api/", timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("USD")
    except Exception:
        return None

def bank_rates():
    rates = []
    urls = [
        "https://www.gtbank.com/rates",
        "https://www.accessbank.com/rates",
        "https://www.zenithbank.com/rates"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            usd = soup.find("td", text="USD").find_next_sibling("td").text.strip().replace(",", "")
            rates.append(float(usd))
        except Exception:
            continue
    return rates

# ----------------- Blackmarket / P2P -----------------
def aboki_fx():
    try:
        r = requests.get("https://www.abokifx.com/", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        row = soup.find("td", text="USD")
        if row:
            rate = row.find_next_sibling("td").text.strip().replace(",", "")
            return float(rate)
    except Exception:
        return None

def naija_blog_fx():
    try:
        r = requests.get("https://nairaforex.com/", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        usd = soup.find("span", class_="usd-rate")
        if usd:
            return float(usd.text.strip().replace(",", ""))
    except Exception:
        return None

# ----------------- CEX P2P Blackmarket -----------------
def binance_p2p():
    try:
        url = "https://api.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {"asset":"USDT","fiat":"NGN","tradeType":"SELL","page":1,"rows":5}
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()
        prices = [float(adv["adv"]["price"]) for adv in data.get("data", [])]
        if prices:
            return sum(prices)/len(prices)
    except Exception:
        return None

def bitget_p2p():
    try:
        url = "https://c2c.bitget.com/api/v1/p2p/offers?asset=USDT&fiat=NGN&type=sell&page=1&limit=5"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        prices = [float(x["price"]) for x in data.get("data", [])]
        if prices:
            return sum(prices)/len(prices)
    except Exception:
        return None

def kucoin_p2p():
    try:
        url = "https://www.kucoin.com/_api/c2c/market/active?coinId=1&currency=NGN&type=sell&currentPage=1&paymentMethod=0"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        prices = [float(x["price"]) for x in data.get("data", {}).get("items", [])]
        if prices:
            return sum(prices)/len(prices)
    except Exception:
        return None

def bybit_p2p():
    try:
        url = "https://api.bybit.com/spot/p2p/offers?asset=USDT&fiat=NGN&type=sell&page=1&limit=5"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        prices = [float(x["price"]) for x in data.get("result", [])]
        if prices:
            return sum(prices)/len(prices)
    except Exception:
        return None

def luno_p2p():
    try:
        url = "https://api.luno.com/api/1/orderbook?pair=XBTNGN"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        asks = data.get("asks", [])
        if asks:
            prices = [float(a["price"]) for a in asks]
            return sum(prices)/len(prices)
    except Exception:
        return None

def mexc_p2p():
    try:
        url = "https://www.mexc.com/api/v2/p2p/offers?asset=USDT&fiat=NGN&type=sell&page=1&limit=5"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        prices = [float(x["price"]) for x in data.get("data", [])]
        if prices:
            return sum(prices)/len(prices)
    except Exception:
        return None

# ----------------- Aggregate -----------------
def all_official_sources():
    rates = []
    for fn in [exchangerate_host, cbn_official]:
        try:
            rate = fn("USD") if fn == exchangerate_host else fn()
            if rate:
                rates.append(rate)
        except Exception:
            continue
    rates.extend(bank_rates())
    return rates

def all_blackmarket_sources():
    rates = []
    for fn in [aboki_fx, naija_blog_fx, binance_p2p, bitget_p2p, kucoin_p2p, bybit_p2p, luno_p2p, mexc_p2p]:
        try:
            rate = fn()
            if rate:
                rates.append(rate)
        except Exception:
            continue
    return rates
