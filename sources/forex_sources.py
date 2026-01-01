import asyncio
import httpx
from bs4 import BeautifulSoup

# Multiple black market sources
BLACKMARKET_SOURCES = {
    "nairatoday": "https://nairatoday.com/",
    "ngnrates": "https://ngnrates.com/",
    # Add more sources here
}

OFFICIAL_RATES = {
    "central_bank": "https://www.cbn.gov.ng/rates/exchangerates.asp",
}

async def fetch_blackmarket_rate(source_name):
    url = BLACKMARKET_SOURCES.get(source_name)
    if not url:
        return {}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")
        rates = {}

        # Example parsing for USD, EUR, GBP, CAD
        if source_name == "nairatoday":
            for currency in ["USD", "EUR", "GBP", "CAD"]:
                tag = soup.find("div", string=lambda x: x and currency in x)
                if tag:
                    rate_text = tag.find_next("div").text
                    rates[currency] = int(rate_text.replace(",", "").strip())

        elif source_name == "ngnrates":
            for currency in ["USD", "EUR", "GBP", "CAD"]:
                tag = soup.find("span", string=lambda x: x and currency in x)
                if tag:
                    rate_text = tag.find_next("span").text
                    rates[currency] = int(rate_text.replace(",", "").strip())

        return rates

    except Exception as e:
        print(f"❌ Error fetching {source_name}:", e)
        return {}

async def fetch_official_rate():
    url = OFFICIAL_RATES["central_bank"]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")
        rates = {}
        for currency in ["USD", "EUR", "GBP", "CAD"]:
            tag = soup.find("td", string=lambda x: x and currency in x)
            if tag:
                rate_text = tag.find_next("td").text
                rates[currency] = int(rate_text.replace(",", "").strip())

        return rates

    except Exception as e:
        print("❌ Error fetching official rate:", e)
        return {}

async def fetch_all_forex():
    """
    Fetch all forex rates from black market and official sources
    Returns a list of dicts like:
    [{"source": "nairatoday", "USD": 750, ...}, {"source": "central_bank", "USD": 775, ...}]
    """
    tasks = [fetch_official_rate()]
    for source in BLACKMARKET_SOURCES:
        tasks.append(fetch_blackmarket_rate(source))
    
    results = await asyncio.gather(*tasks)
    all_rates = []
    for i, r in enumerate(results):
        if r:
            source_name = "central_bank" if i == 0 else list(BLACKMARKET_SOURCES.keys())[i-1]
            r["source"] = source_name
            all_rates.append(r)
    return all_rates
