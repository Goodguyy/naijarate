import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Render; FastAPI)",
}

TIMEOUT = 15


# ---------- BINANCE ----------
async def binance_usdt_ngn():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=USDTNGN"
    async with httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT) as client:
        r = await client.get(url)
        r.raise_for_status()
        return float(r.json()["price"])


# ---------- OKX ----------
async def okx_usdt_ngn():
    # OKX does NOT have direct NGN
    # Use USDT/USD * USD/NGN
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        usdt_usd = await client.get(
            "https://www.okx.com/api/v5/market/ticker?instId=USDT-USD"
        )
        usdt_usd.raise_for_status()
        price1 = float(usdt_usd.json()["data"][0]["last"])

        usd_ngn = await exchangerate_api()
        return price1 * usd_ngn


# ---------- KUCOIN ----------
async def kucoin_usdt_ngn():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        usdt_usd = await client.get(
            "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=USDT-USDC"
        )
        usdt_usd.raise_for_status()
        price1 = float(usdt_usd.json()["data"]["price"])

        usd_ngn = await exchangerate_api()
        return price1 * usd_ngn


# ---------- BYBIT ----------
async def bybit_usdt_ngn():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(
            "https://api.bybit.com/v5/market/tickers?category=spot&symbol=USDTUSDC"
        )
        r.raise_for_status()
        price1 = float(r.json()["result"]["list"][0]["lastPrice"])

        usd_ngn = await exchangerate_api()
        return price1 * usd_ngn


# ---------- OFFICIAL USD/NGN ----------
async def exchangerate_api():
    url = "https://open.er-api.com/v6/latest/USD"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(url)
        r.raise_for_status()
        return float(r.json()["rates"]["NGN"])


# ---------- HARD FALLBACK ----------
async def fallback_rate():
    return 1500.0
