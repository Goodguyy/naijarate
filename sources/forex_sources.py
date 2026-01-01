# sources/forex_sources.py
import httpx
from bs4 import BeautifulSoup
import asyncio

# ---------- Black Market Sources ----------
BLACKMARKET_SOURCES = {
    "nairatoday": "https://nairatoday.com/",
    "ngnrates": "https://www.ngnrates.com/",
    "abokifx": "https://www.abokifx.com/",
    "ratecity": "https://www.ratecityng.com/",
}

async def fetch_blackmarket_forex(currencies=["USD","EUR","GBP","CAD"]):
    """
    Fetch black market forex rates asynchronously from multiple sources.
    Returns a dictionary of currency:rate pairs.
    """
    rates = {}
    for source, url in BLACKMARKET_SOURCES.items():
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                r = await client.get(url)
                r.raise_for_status()
                html = r.text

            soup = BeautifulSoup(html, "html.parser")
            source_rates = {}

            if source == "nairatoday":
                for cur in currencies:
                    tag = soup.find("div", string=lambda x: x and cur in x)
                    if tag:
                        val = tag.find_next("div").text
                        source_rates[cur] = int(val.replace(",", "").strip())
            elif source == "ngnrates":
                for cur in currencies:
                    tag = soup.find("span", string=lambda x: x and cur in x)
                    if tag:
                        val = tag.find_next("span").text
                        source_rates[cur] = int(val.replace(",", "").strip())
            elif source in ["abokifx", "ratecity"]:
                for cur in currencies:
                    tag = soup.find("td", string=lambda x: x and cur in x)
                    if tag:
                        val = tag.find_next("td").text
                        source_rates[cur] = int(val.replace(",", "").strip())

            # Merge rates into main dict (last source wins)
            for cur, val in source_rates.items():
                if val:
                    rates[cur] = val

        except Exception as e:
            print(f"❌ Error fetching {source} rates:", e)

    return rates

# ---------- Official CBN Rates ----------
CBN_XML_URL = "https://www.cbn.gov.ng/scripts/exchangerates.asp"

async def fetch_official_forex(currencies=["USD","EUR","GBP","CAD"]):
    """
    Fetch official CBN forex rates asynchronously.
    Returns a dictionary of currency:rate pairs.
    """
    rates = {}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(CBN_XML_URL)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if table:
            for row in table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 2:
                    cur = cols[0].text.strip()
                    val = cols[1].text.strip().replace(",", "")
                    if cur in currencies:
                        try:
                            rates[cur] = int(val)
                        except ValueError:
                            continue
    except Exception as e:
        print("❌ Error fetching official forex:", e)

    return rates

# ---------- Functions expected by scraper.py ----------
async def exchangerate_api(currencies=["USD","EUR","GBP","CAD"]):
    """
    Main async API function to fetch forex rates.
    Prioritizes black market rates, falls back to official CBN rates if needed.
    """
    rates = await fetch_blackmarket_forex(currencies)
    if not rates:
        rates = await fetch_official_forex(currencies)
    return rates

def fallback_rate(cur="USD"):
    """
    Hardcoded fallback rates if all API calls fail.
    """
    fallbacks = {"USD": 780, "EUR": 850, "GBP": 1000, "CAD": 600}
    return fallbacks.get(cur.upper(), 800)
