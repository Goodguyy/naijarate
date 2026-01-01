import asyncio
import httpx
from bs4 import BeautifulSoup
import sqlite_utils
import json
from datetime import datetime
from aggregator import aggregate_rates
from database import DB_PATH
from sources.cex_rates import binance_usdt_ngn, okx_usdt_ngn, kucoin_usdt_ngn, bybit_usdt_ngn

# ---------- BLACK MARKET SOURCES ----------
BLACKMARKET_SOURCES = {
    "nairatoday": "https://nairatoday.com/",
    "ngnrates": "https://www.ngnrates.com/",
    "abokifx": "https://www.abokifx.com/",
    "ratecity": "https://www.ratecityng.com/",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Render; FastAPI)"}
TIMEOUT = 15

# ----------------------------
# Fetch blackmarket rates
# ----------------------------
async def fetch_blackmarket_forex(currencies=["USD"]):
    rates = {}
    for source, url in BLACKMARKET_SOURCES.items():
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS, follow_redirects=True) as client:
                r = await client.get(url)
                r.raise_for_status()
                html = r.text

            soup = BeautifulSoup(html, "html.parser")
            source_rates = {}

            # Example parsing logic
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

            for cur, val in source_rates.items():
                if val:
                    rates[cur] = val

        except Exception as e:
            print(f"❌ Error fetching {source} rates: {e}")

    return rates

# ----------------------------
# Fetch official USD/NGN rate (fallback API)
# ----------------------------
async def fetch_official_forex():
    url = "https://open.er-api.com/v6/latest/USD"  # fallback since CBN XML 404
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            return {"USD": data["rates"]["NGN"]}
    except Exception as e:
        print(f"❌ Error fetching official forex: {e}")
        return {}

# ----------------------------
# Fetch crypto prices from CEX
# ----------------------------
async def fetch_cex_rates():
    cex_funcs = [binance_usdt_ngn, okx_usdt_ngn, kucoin_usdt_ngn, bybit_usdt_ngn]
    results = {}
    for func in cex_funcs:
        try:
            ngn_price = await func()
            results[func.__name__.upper()] = {"NGN": ngn_price}
        except Exception as e:
            print(f"❌ Error fetching {func.__name__}: {e}")
    return results

# ----------------------------
# Fetch top coins from CoinGecko
# ----------------------------
async def fetch_coingecko_top(limit=10):
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page={limit}&page=1&sparkline=false"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
        coins = {}
        for coin in data:
            coins[coin["symbol"].upper()] = {
                "USD": coin["current_price"],
                "NGN": None  # will populate after we get USD/NGN
            }
        return coins

# ----------------------------
# Update rates in database
# ----------------------------
async def update_rates():
    official = await fetch_official_forex()
    blackmarket = await fetch_blackmarket_forex()
    avg_rate_obj = aggregate_rates(list(blackmarket.values()))
    avg_rate = avg_rate_obj["avg"] if avg_rate_obj else None

    # Determine USD/NGN for CoinGecko conversion
    usd_to_ngn = avg_rate or official.get("USD") or 750

    # Crypto prices
    cex = await fetch_cex_rates()
    coingecko = await fetch_coingecko_top()
    for coin, data in coingecko.items():
        data["NGN"] = round(data["USD"] * usd_to_ngn)

    # Save in SQLite
    db = sqlite_utils.Database(DB_PATH)
    table = db.table("rates", pk="timestamp", defaults={
        "avg_rate": None,
        "min_rate": None,
        "max_rate": None,
        "sources": 0,
        "official": "{}",
        "blackmarket": "{}",
        "crypto": "{}",
        "coingecko": "{}"
    })

    timestamp = datetime.utcnow().isoformat()
    table.upsert({
        "timestamp": timestamp,
        "avg_rate": avg_rate,
        "min_rate": avg_rate_obj["min"] if avg_rate_obj else None,
        "max_rate": avg_rate_obj["max"] if avg_rate_obj else None,
        "sources": avg_rate_obj["sources"] if avg_rate_obj else 0,
        "official": json.dumps(official),
        "blackmarket": json.dumps(blackmarket),
        "crypto": json.dumps(cex),
        "coingecko": json.dumps(coingecko)
    }, pk="timestamp")

    print("✅ Updated rates successfully")
    print(f"Forex avg: {avg_rate}")
    print(f"Crypto sample: {dict(list(coingecko.items())[:3])}")

# ----------------------------
# Get latest rates from DB
# ----------------------------
def get_latest_rates():
    db = sqlite_utils.Database(DB_PATH)
    table = db["rates"]
    rows = list(table.rows_where(order_by="timestamp DESC", limit=1))
    if not rows:
        return None
    row = rows[0]
    return {
        "timestamp": row.get("timestamp"),
        "avg_rate": row.get("avg_rate"),
        "min_rate": row.get("min_rate"),
        "max_rate": row.get("max_rate"),
        "sources": row.get("sources"),
        "official": json.loads(row.get("official") or "{}"),
        "blackmarket": json.loads(row.get("blackmarket") or "{}"),
        "crypto": json.loads(row.get("crypto") or "{}"),
        "coingecko": json.loads(row.get("coingecko") or "{}")
    }

# ----------------------------
# Test scraper
# ----------------------------
if __name__ == "__main__":
    asyncio.run(update_rates())
