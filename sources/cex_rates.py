import httpx

HEADERS = {"User-Agent": "Mozilla/5.0 (Render; FastAPI)"}
TIMEOUT = 15

# --- Fallback USD to NGN ---
async def exchangerate_api():
    url = "https://open.er-api.com/v6/latest/USD"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(url)
        r.raise_for_status()
        return float(r.json()["rates"]["NGN"])

async def binance_usdt_ngn():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=USDTNGN"
    async with httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT) as client:
        r = await client.get(url)
        r.raise_for_status()
        return float(r.json()["price"])

async def okx_usdt_ngn():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-USD")
        r.raise_for_status()
        price = float(r.json()["data"][0]["last"])
        usd_ngn = await exchangerate_api()
        return price * usd_ngn

async def kucoin_usdt_ngn():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get("https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=USDT-USDC")
        r.raise_for_status()
        price = float(r.json()["data"]["price"])
        usd_ngn = await exchangerate_api()
        return price * usd_ngn

async def bybit_usdt_ngn():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get("https://api.bybit.com/v5/market/tickers?category=spot&symbol=USDTUSDC")
        r.raise_for_status()
        price = float(r.json()["result"]["list"][0]["lastPrice"])
        usd_ngn = await exchangerate_api()
        return price * usd_ngn

async def fallback_rate():
    return 1500.0
