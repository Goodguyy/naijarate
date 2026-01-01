# sources/crypto.py
import httpx
import asyncio

COINS = ["bitcoin", "ethereum", "dash"]  # add more as needed

async def get_crypto_rates():
    """
    Fetch live crypto prices in USD from CoinGecko API
    """
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(COINS)}&vs_currencies=usd"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            # data is like {'bitcoin': {'usd': 87765}, ...}
            return data
    except Exception as e:
        print("❌ Error fetching crypto rates:", e)
        return {}
