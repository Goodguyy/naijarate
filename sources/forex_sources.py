import httpx
from bs4 import BeautifulSoup

# Multiple black market sources
BLACKMARKET_SOURCES = {
    "nairatoday": "https://nairatoday.com/",
    "ngnrates": "https://ngnrates.com/",
    # Add more sources as needed
}

OFFICIAL_RATES = {
    "central_bank": "https://www.cbn.gov.ng/rates/exchangerates.asp",
}

async def fetch_blackmarket_rate(source_name):
    """
    Fetch black market rates for USD (extendable for EUR, GBP, etc.)
    Returns a dict: {"USD": 750, "EUR": 820, ...}
    """
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

        # Example parsing for USD, EUR, GBP
        if source_name == "nairatoday":
            # NaijaToday example
            usd_tag = soup.find("div", string=lambda x: x and "USD" in x)
            if usd_tag:
                rate_text = usd_tag.find_next("div").text
                rates["USD"] = int(rate_text.replace(",", "").strip())

            eur_tag = soup.find("div", string=lambda x: x and "EUR" in x)
            if eur_tag:
                rate_text = eur_tag.find_next("div").text
                rates["EUR"] = int(rate_text.replace(",", "").strip())

        elif source_name == "ngnrates":
            # NGN Rates example
            usd_tag = soup.find("span", string=lambda x: x and "USD" in x)
            if usd_tag:
                rate_text = usd_tag.find_next("span").text
                rates["USD"] = int(rate_text.replace(",", "").strip())

        # Add more source-specific parsing here
        return rates

    except Exception as e:
        print(f"❌ Error fetching {source_name}:", e)
        return {}

async def fetch_official_rate():
    """
    Fetch official rate from Central Bank of Nigeria
    Returns dict: {"USD": 775, "EUR": 830, ...}
    """
    url = OFFICIAL_RATES["central_bank"]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")
        rates = {}

        usd_tag = soup.find("td", string=lambda x: x and "USD" in x)
        if usd_tag:
            rate_text = usd_tag.find_next("td").text
            rates["USD"] = int(rate_text.replace(",", "").strip())

        eur_tag = soup.find("td", string=lambda x: x and "EUR" in x)
        if eur_tag:
            rate_text = eur_tag.find_next("td").text
            rates["EUR"] = int(rate_text.replace(",", "").strip())

        return rates

    except Exception as e:
        print("❌ Error fetching official rate:", e)
        return {}
