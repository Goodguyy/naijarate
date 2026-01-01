import httpx
from bs4 import BeautifulSoup
import asyncio

# ----------------------------
# Black Market Sources
# ----------------------------
BLACKMARKET_SOURCES = {
    "nairatoday": "https://nairatoday.com/",
    "ngnrates": "https://www.ngnrates.com/",
    "abokifx": "https://www.abokifx.com/",
    "ratecity": "https://www.ratecityng.com/",
}

async def fetch_blackmarket_forex(currencies=["USD", "EUR", "GBP", "CAD"]):
    """
    Fetch black market rates from multiple sources.
    Returns dict: {"USD": 755, "EUR": 830, ...}
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

            # Example parsing logic per source
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

            elif source == "abokifx":
                for cur in currencies:
                    tag = soup.find("td", string=lambda x: x and cur in x)
                    if tag:
                        val = tag.find_next("td").text
                        source_rates[cur] = int(val.replace(",", "").strip())

            elif source == "ratecity":
                for cur in currencies:
                    tag = soup.find("td", string=lambda x: x and cur in x)
                    if tag:
                        val = tag.find_next("td").text
                        source_rates[cur] = int(val.replace(",", "").strip())

            # Merge into main dict (average if multiple sources exist)
            for cur, val in source_rates.items():
                if val:
                    rates[cur] = val

        except httpx.HTTPStatusError as e:
            print(f"❌ Error fetching {source} rates: {e}")
        except Exception as e:
            print(f"❌ Unexpected error fetching {source} rates: {e}")

    return rates

# ----------------------------
# Official Forex Rate from CBN
# ----------------------------
CBN_XML_URL = "https://www.cbn.gov.ng/scripts/exchangerates.asp"

async def fetch_official_forex(currencies=["USD", "EUR", "GBP", "CAD"]):
    """
    Fetch official rates from CBN XML page.
    Returns dict: {"USD": 775, "EUR": 830, ...}
    """
    rates = {}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(CBN_XML_URL)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if not table:
            print("❌ CBN table not found")
            return rates

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

    except httpx.HTTPStatusError as e:
        print(f"❌ Error fetching official forex: {e}")
    except Exception as e:
        print(f"❌ Unexpected error fetching official forex: {e}")

    return rates

# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    async def main():
        official = await fetch_official_forex()
        blackmarket = await fetch_blackmarket_forex()
        print("Official Rates:", official)
        print("Blackmarket Rates:", blackmarket)

    asyncio.run(main())
