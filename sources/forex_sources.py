import requests
from bs4 import BeautifulSoup

# ----------------- Official Sources -----------------
def exchangerate_host(cur="USD"):
    try:
        r = requests.get(f"https://api.exchangerate.host/latest?base={cur}", timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("rates", {}).get("NGN")
    except:
        return None

def cbn_official():
    try:
        r = requests.get("https://www.cbn.gov.ng/rates/api/", timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("USD")
    except:
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
        except:
            continue
    return rates

# ----------------- Blackmarket / Blogs -----------------
def aboki_fx():
    try:
        r = requests.get("https://www.abokifx.com/", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        row = soup.find("td", text="USD")
        if row:
            rate = row.find_next_sibling("td").text.strip().replace(",", "")
            return float(rate)
    except:
        return None

def naija_blog_fx():
    try:
        r = requests.get("https://nairaforex.com/", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        usd = soup.find("span", class_="usd-rate")
        if usd:
            return float(usd.text.strip().replace(",", ""))
    except:
        return None

# ----------------- Aggregate -----------------
def all_official_sources():
    rates = []
    for fn in [exchangerate_host, cbn_official]:
        try:
            rate = fn("USD") if fn == exchangerate_host else fn()
            if rate:
                rates.append(rate)
        except:
            continue
    rates.extend(bank_rates())
    return rates

def all_blackmarket_sources():
    rates = []
    for fn in [aboki_fx, naija_blog_fx]:
        try:
            rate = fn()
            if rate:
                rates.append(rate)
        except:
            continue
    return rates
