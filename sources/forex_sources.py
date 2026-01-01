# sources/forex_sources.py
import httpx
from bs4 import BeautifulSoup

BLACKMARKET_SOURCES = {
    "nairatoday": "https://nairatoday.com/",
    "ngnrates": "https://ngnrates.com/",
}

OFFICIAL_SOURCE = "https://www.cbn.gov.ng/rates/exchangerates.asp"

async def fetch_official_forex(currencies=["USD","EUR","GBP","CAD"]):
    """Fetch official forex rates from CBN"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(OFFICIAL_SOURCE)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")
        rates = {}
        for cur in currencies:
            tag = soup.find("td", string=lambda x: x and cur in x)
            if tag:
                rate_text = tag.find_next("td").text
                rates[cur] = int(rate_text.replace(",", "").strip())
        return rates
    except Exception as e:
        print("❌ Official fetch error:", e)
        return {}

async def fetch_blackmarket_forex(currencies=["USD","EUR","GBP","CAD"]):
    """Fetch black market rates from all sources"""
    result = {}
    for source, url in BLACKMARKET_SOURCES.items():
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(url)
                r.raise_for_status()
                html = r.text
            soup = BeautifulSoup(html, "html.parser")
            for cur in currencies:
                tag = soup.find(string=lambda x: x and cur in x)
                if tag:
                    rate_tag = tag.find_next()  # adjust based on HTML
                    rate = int(rate_tag.text.replace(",", "").strip())
                    if cur not in result:
                        result[cur] = []
                    result[cur].append(rate)
        except Exception as e:
            print(f"❌ {source} fetch error:", e)
    # Take average per currency
    averaged = {cur: sum(vals)//len(vals) for cur, vals in result.items() if vals}
    return averaged
