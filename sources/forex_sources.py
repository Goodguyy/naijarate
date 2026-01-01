import requests
from bs4 import BeautifulSoup

def exchangerate_host(cur="USD"):
    """Official exchange rate from exchangerate.host"""
    try:
        r = requests.get(f"https://api.exchangerate.host/latest?base={cur}", timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("rates", {}).get("NGN")
    except Exception:
        return None

def cbn_official():
    """CBN official rate"""
    try:
        r = requests.get("https://www.cbn.gov.ng/rates/api/", timeout=10)  # Example endpoint
        r.raise_for_status()
        data = r.json()
        return data.get("USD")  # adjust key based on actual CBN API
    except Exception:
        return None

def bank_rates():
    """Fetch rates from major Nigerian bank websites (dummy placeholders)"""
    rates = []
    try:
        # Example: GTBank rate
        r = requests.get("https://www.gtbank.com/rates", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        usd = soup.find("td", text="USD").find_next_sibling("td").text.strip().replace(",", "")
        rates.append(float(usd))
    except Exception:
        pass
    try:
        # Example: Access Bank rate
        r = requests.get("https://www.accessbank.com/rates", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        usd = soup.find("td", text="USD").find_next_sibling("td").text.strip().replace(",", "")
        rates.append(float(usd))
    except Exception:
        pass
    return rates

def aboki_fx():
    """Parallel market USD→NGN from AbokiFX"""
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
    """Scrape other Naija forex blogs"""
    try:
        r = requests.get("https://nairaforex.com/", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        usd = soup.find("span", class_="usd-rate")
        if usd:
            return float(usd.text.strip().replace(",", ""))
    except Exception:
        return None

def all_forex_sources(cur="USD"):
    """Return list of all available rates for a currency"""
    rates = []
    for fn in [exchangerate_host, cbn_official, aboki_fx, naija_blog_fx]:
        try:
            rate = fn(cur) if fn == exchangerate_host else fn()
            if rate:
                rates.append(rate)
        except Exception:
            continue
    # Include bank rates list
    rates.extend(bank_rates())
    return rates
