import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def safe_get(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def official_cbn():
    data = safe_get("https://api.exchangerate.host/latest?base=USD&symbols=NGN")
    if not data:
        return None
    return data["rates"]["NGN"]


def exchangerate_host(currency):
    data = safe_get(f"https://api.exchangerate.host/latest?base={currency}&symbols=NGN")
    if not data:
        return None
    return data["rates"]["NGN"]


def parallel_estimate(currency):
    """Simulated black-market blend from multiple FX APIs"""
    rates = []
    for base in ["https://open.er-api.com/v6/latest/", "https://api.exchangerate-api.com/v4/latest/"]:
        data = safe_get(base + currency)
        if data and "rates" in data and "NGN" in data["rates"]:
            rates.append(data["rates"]["NGN"] * 1.05)  # parallel premium
    return rates
