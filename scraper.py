from sources.forex_sources import get_forex_rates
from sources.crypto import get_crypto_rates
from sources.aggregator import aggregate_rates

async def get_latest_rates():
    forex = await get_forex_rates()
    crypto_usd = await get_crypto_rates()
    crypto_ngn = {k: int(v['usd'] * forex.get('USD', 1)) for k,v in crypto_usd.items()}

    return {
        "source": "live",
        "data": {
            "forex": forex,
            "crypto_usd": crypto_usd,
            "crypto_ngn": crypto_ngn
        }
    }
