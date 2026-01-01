# scraper.py
import asyncio
import httpx
from sources.aggregator import aggregate_rates
from sources.forex_sources import exchangerate_api, fallback_rate
from sources.cex_rates import binance_usdt_ngn, kucoin_usdt_ngn, bybit_usdt_ngn, okx_usdt_ngn
from database import DB_PATH
import sqlite3

# ---------- Helper functions ----------

async def fetch_forex_rates():
    """Fetch USD/NGN from multiple sources."""
    rates = []

    # Try official API
    try:
        official = await exchangerate_api()
        rates.append(official)
    except Exception as e:
        print(f"❌ Error fetching official forex: {e}")

    # Fallback hardcoded rate
    try:
        fallback = await fallback_rate()
        rates.append(fallback)
    except Exception as e:
        print(f"❌ Error fetching fallback rate: {e}")

    return rates

async def fetch_crypto_rates():
    """Fetch top crypto prices in USD/NGN from CoinGecko and CEXs."""
    crypto_data = {}

    async with httpx.AsyncClient(timeout=15) as client:
        # CoinGecko top 10 coins
        try:
            r = await client.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}
            )
            r.raise_for_status()
            coins = r.json()
            for coin in coins:
                crypto_data[coin["symbol"].upper()] = {
                    "USD": coin["current_price"],
                    "NGN": None  # Will populate after fetching USD/NGN
                }
        except Exception as e:
            print(f"❌ Error fetching CoinGecko data: {e}")

    # Fetch USD/NGN for CEX conversion
    usd_to_ngn_rates = []
    for func in [binance_usdt_ngn, kucoin_usdt_ngn, bybit_usdt_ngn, okx_usdt_ngn]:
        try:
            rate = await func()
            usd_to_ngn_rates.append(rate)
        except Exception as e:
            print(f"❌ Error fetching CEX USD/NGN rate ({func.__name__}): {e}")

    usd_to_ngn = aggregate_rates(usd_to_ngn_rates)["avg"] if usd_to_ngn_rates else 1500

    # Convert CoinGecko USD prices to NGN
    for coin in crypto_data.values():
        coin["NGN"] = round(coin["USD"] * usd_to_ngn)

    return crypto_data, usd_to_ngn

# ---------- Main update function ----------

async def update_rates():
    """Fetch latest forex and crypto rates and save to SQLite DB."""
    # Fetch forex rates
    forex_rates = await fetch_forex_rates()
    forex_avg = aggregate_rates(forex_rates)["avg"] if forex_rates else 1500

    # Fetch crypto prices
    crypto_data, cex_usd_to_ngn = await fetch_crypto_rates()

    # Save to SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Forex table
        c.execute("""
            CREATE TABLE IF NOT EXISTS forex_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usd_to_ngn REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("INSERT INTO forex_rates (usd_to_ngn) VALUES (?)", (forex_avg,))

        # Crypto table
        c.execute("""
            CREATE TABLE IF NOT EXISTS crypto_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                usd REAL,
                ngn REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        for symbol, data in crypto_data.items():
            c.execute(
                "INSERT INTO crypto_rates (symbol, usd, ngn) VALUES (?, ?, ?)",
                (symbol, data["USD"], data["NGN"])
            )

        conn.commit()
        conn.close()
        print(f"✅ Updated rates successfully\nForex avg: {forex_avg}\nCrypto sample: {dict(list(crypto_data.items())[:3])}")
    except Exception as e:
        print(f"❌ Error saving to database: {e}")

# ---------- Utility to get latest rates ----------

def get_latest_rates():
    """Retrieve latest forex and crypto rates from DB."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Latest forex
    c.execute("SELECT usd_to_ngn FROM forex_rates ORDER BY timestamp DESC LIMIT 1")
    forex = c.fetchone()[0] if c.fetchone() else None

    # Latest crypto
    c.execute("SELECT symbol, usd, ngn FROM crypto_rates ORDER BY timestamp DESC")
    crypto = {row[0]: {"USD": row[1], "NGN": row[2]} for row in c.fetchall()}

    conn.close()
    return {"forex": forex, "crypto": crypto}

# ---------- Async entrypoint for testing ----------

if __name__ == "__main__":
    asyncio.run(update_rates())
