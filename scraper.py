import asyncio
from sources.crypto import get_crypto_rates
from sources.forex_sources import fetch_blackmarket_forex, fetch_official_forex
from sources.aggregator import aggregate_rates

USD_TO_NGN_FALLBACK = 765  # fallback if no rates

async def get_latest_rates():
    # Fetch forex
    forex_blackmarket = await fetch_blackmarket_forex()
    forex_official = await fetch_official_forex()

    usd_rates = []
    for val in [forex_blackmarket.get("USD"), forex_official.get("USD")]:
        if val:
            usd_rates.append(val)

    usd_to_ngn = aggregate_rates(usd_rates)["avg"] if usd_rates else USD_TO_NGN_FALLBACK

    # Fetch crypto
    crypto = await get_crypto_rates(usd_to_ngn)

    return {
        "source": "live",
        "data": {
            "forex": {
                "USD": usd_to_ngn,
                **{k: v for k, v in forex_blackmarket.items() if k != "USD"}
            },
            "crypto_usd": {k: {"USD": v["USD"]} for k,v in crypto.items()},
            "crypto_ngn": {k: v["NGN"] for k,v in crypto.items()}
        }
    }

# For synchronous use
def fetch_rates_sync():
    return asyncio.run(get_latest_rates())
