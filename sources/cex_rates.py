import httpx
import statistics

# -----------------------------
# P2P endpoints
# -----------------------------
BINANCE_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

OKX_URL = "https://www.okx.com/v3/c2c/tradingOrders/books"
BYBIT_URL = "https://api2.bybit.com/fiat/otc/item/online"

# -----------------------------
# Binance P2P
# -----------------------------
async def fetch_binance_ngn():
    payload = {
        "asset": "USDT",
        "fiat": "NGN",
        "tradeType": "SELL",
        "page": 1,
        "rows": 5
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(BINANCE_URL, json=payload)
            r.raise_for_status()
            data = r.json().get("data", [])

        prices = [
            float(ad["adv"]["price"])
            for ad in data
            if "adv" in ad and ad["adv"].get("price")
        ]

        return statistics.median(prices) if prices else None

    except Exception as e:
        print("❌ Binance error:", e)
        return None


# -----------------------------
# OKX P2P
# -----------------------------
async def fetch_okx_ngn():
    params = {
        "side": "sell",
        "quoteCurrency": "NGN",
        "baseCurrency": "USDT",
        "paymentMethod": "all",
        "userType": "all"
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(OKX_URL, params=params)
            r.raise_for_status()
            data = r.json().get("data", [])

        prices = [
            float(item["price"])
            for item in data
            if item.get("price")
        ]

        return statistics.median(prices) if prices else None

    except Exception as e:
        print("❌ OKX error:", e)
        return None


# -----------------------------
# Bybit P2P
# -----------------------------
async def fetch_bybit_ngn():
    payload = {
        "tokenId": "USDT",
        "currencyId": "NGN",
        "side": "1",  # sell
        "size": "10",
        "page": "1"
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(BYBIT_URL, json=payload)
            r.raise_for_status()
            items = r.json().get("result", {}).get("items", [])

        prices = [
            float(item["price"])
            for item in items
            if item.get("price")
        ]

        return statistics.median(prices) if prices else None

    except Exception as e:
        print("❌ Bybit error:", e)
        return None


# -----------------------------
# Unified CEX fetcher
# -----------------------------
async def fetch_cex_ngn_rate():
    rates = []

    for fetcher in (
        fetch_binance_ngn,
        fetch_okx_ngn,
        fetch_bybit_ngn,
    ):
        try:
            rate = await fetcher()
            if isinstance(rate, (int, float)):
                rates.append(rate)
        except Exception:
            continue

    return rates
