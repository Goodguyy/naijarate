import httpx
from bs4 import BeautifulSoup

# ---------- Black Market Sources ----------
BLACKMARKET_SOURCES = {
    "nairatoday": "https://nairatoday.com/",
    "ngnrates": "https://www.ngnrates.com/",
    "abokifx": "https://www.abokifx.com/",
    "ratecity": "https://www.ratecityng.com/",
}

async def fetch_blackmarket_forex(currencies=["USD","EUR","GBP"]):
    rates = {}
    for source, url in BLACKMARKET_SOURCES.items():
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                r = await client.get(url)
                r.raise_for_status()
                html = r.text

            soup = BeautifulSoup(html, "html.parser")
            source_rates = {}

            # Example parsing per source (adjust if needed)
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

            for cur, val in source_rates.items():
                if val:
                    rates[cur] = val

        except Exception as e:
            print(f"❌ Error fetching {source} rates:", e)

    return rates


# ---------- Official CBN Rate ----------
CBN_XML_URL = "https://www.cbn.gov.ng/scripts/exchangerates.asp"

async def fetch_official_forex(currencies=["USD","EUR","GBP"]):
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
