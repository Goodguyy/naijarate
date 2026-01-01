import httpx
from bs4 import BeautifulSoup

BLOG_SOURCES = [
    {
        "name": "nairatoday",
        "url": "https://nairatoday.com",
        "selector": ".rate"  # Example selector, adjust after inspecting site
    },
    {
        "name": "ngnrates",
        "url": "https://ngnrates.com",
        "selector": ".usd-rate"  # Example selector
    }
]

async def fetch_blog_rates():
    rates = []

    async with httpx.AsyncClient(timeout=15) as client:
        for site in BLOG_SOURCES:
            try:
                r = await client.get(site["url"])
                soup = BeautifulSoup(r.text, "lxml")
                el = soup.select_one(site["selector"])
                if not el:
                    continue

                rate = float(
                    el.text.replace("₦", "").replace(",", "").strip()
                )
                rates.append(rate)
            except Exception:
                continue

    return rates
