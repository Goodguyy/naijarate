# sources/forex_sources.py
import httpx
from bs4 import BeautifulSoup
import asyncio

# Black market sources
BLACKMARKET_SOURCES = {
    "nairatoday": "https://nairatoday.com/",
    "ngnrates": "https://ngnrates.com/",
    # Add more black market sources here if needed
}

# Official CBN rates
OFFICIAL_SOURCE = "https://www.cbn.gov.ng/rates/exchangerates.asp"

async def fetch_official_forex(currencies=["USD","EUR","GBP","CAD"]):
    """
    Fetch official forex rates from CBN.
    Returns dict: {"USD": 775, "EUR": 830, ...}
    """
    rates = {}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(OFFICIAL_SOURCE)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")
        for cur in currencies:
            tag = soup.find("td", string=lambda x: x and cur in x)
            if tag:
                rate_text = tag.find_next("td").text
                rates[cur] = int(rate_text.replace(",", "").strip())
        return rates

    except Exception as e:
        print("❌ Error fetching official forex:", e)
        return {}

async def fetch_blackmarket_forex(currencies=["USD","EUR","GBP","CAD"]):
    """
    Fetch black market rates from multiple sources.
    Returns dict: {"USD": 780, "EUR": 850, ...} (averaged if multiple sources)
    """
    results = {cur: [] for cur in currencies}

    async def fetch_source(name, url):
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(url)
                r.raise_for_status()
                html = r.text
            soup = BeautifulSoup(html, "html.parser")

            for cur in currencies:
                tag = soup.find(string=lambda x: x and cur in x)
                if tag:
                    rate_tag = tag.find_next()  # Adjust if needed per source HTML
                    if rate_tag and rate_tag.text:
                        rate = int(rate_tag.text.replace(",", "").strip())
                        results[cur].append(rate)
        except Exception as e:
            print(f"❌ Error fetching {name} rates:", e)

    # Run all sources concurrently
    tasks = [fetch_source(name, url) for name, url in BLACKMARKET_SOURCES.items()]
    await asyncio.gather(*tasks)

    # Average the rates per currency
    averaged = {cur: round(sum(vals)/len(vals)) for cur, vals in results.items() if vals}
    return averaged
