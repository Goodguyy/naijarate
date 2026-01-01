# scraper.py
import asyncio
import httpx
from sources.forex_sources import exchangerate_api, fallback_rate
from sources.aggregator import aggregate_rates

# ---------- CoinGecko API ----------
COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"

async def fetch_crypto_prices(crypto_ids=["bitcoin","ethereum","dash"], vs_currencies=["usd"]):
    """
    Fetch latest crypto prices from CoinGecko.
    Returns a dict: {crypto: {currency: price}}
    """
    params = {
        "ids": ",".join(crypto_ids),
        "vs_currencies": ",".join(vs_currencies)
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(COINGECKO_API, params=params)
            r.raise_for_status()
            data = r.json()
        return data
    except Exception as e:
        print("❌ Error fetching crypto prices:", e)
        return {}

# ---------- Convert crypto to NGN ----------
async def convert_to_naira(crypto_prices, forex_rates):
    """
    Convert crypto prices in USD to NGN using forex rates.
    Returns {crypto: NGN price}
    """
    naira_prices = {}
    usd_rate = forex_rates.get("USD") or fallback_rate("USD")
    for crypto, price_info in crypto_prices.items():
        usd_price = price_info.get("usd")
        if usd_price:
            naira_prices[crypto] = round(usd_price * usd_rate)
    return naira_prices

# ---------- Get latest forex and crypto rates ----------
async def get_latest_rates(cryptos=["bitcoin","ethereum","dash"]):
    """
    Fetch latest forex and crypto rates.
    Returns structured dict with aggregation.
    """
    # Fetch forex rates first
    forex_rates = await exchangerate_api(["USD","EUR","GBP","CAD"])

    # Aggregate forex rates if multiple sources available
    aggregated_forex = {}
    for cur, rate in forex_rates.items():
        aggregated_forex[cur] = aggregate_rates([rate])

    # Fetch crypto prices
    crypto_prices = await fetch_crypto_prices(cryptos, ["usd"])

    # Convert to NGN
    crypto_naira = await convert_to_naira(crypto_prices, forex_rates)

    return {
        "forex": aggregated_forex,
        "crypto_usd": crypto_prices,
        "crypto_ngn": crypto_naira
    }

# ---------- Update rates (for scheduled tasks) ----------
async def update_rates():
    """
    Fetch latest rates and return them.
    Can be called periodically for cron jobs or endpoints.
    """
    rates = await get_latest_rates()
    print("✅ Updated rates:", rates)
    return rates

# ---------- Test run ----------
if __name__ == "__main__":
    asyncio.run(update_rates())
