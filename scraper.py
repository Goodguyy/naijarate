import asyncio
from database import insert_rate
from sources.forex_sources import (
    binance_usdt_ngn,
    okx_usdt_ngn,
    kucoin_usdt_ngn,
    bybit_usdt_ngn,
    exchangerate_api,
    fallback_rate,
)

async def update_rates():
    success = False

    sources = [
        ("binance", binance_usdt_ngn, "USDT/NGN"),
        ("okx", okx_usdt_ngn, "USDT/NGN"),
        ("kucoin", kucoin_usdt_ngn, "USDT/NGN"),
        ("bybit", bybit_usdt_ngn, "USDT/NGN"),
    ]

    for name, func, pair in sources:
        try:
            rate = await func()
            insert_rate(name, pair, rate)
            success = True
            print(f"✅ {name} inserted: {rate}")
        except Exception as e:
            print(f"❌ {name} failed:", e)

    # Official FX
    try:
        usd_ngn = await exchangerate_api()
        insert_rate("official", "USD/NGN", usd_ngn)
        success = True
    except Exception as e:
        print("❌ Official FX failed:", e)

    # Absolute fallback
    if not success:
        rate = await fallback_rate()
        insert_rate("fallback", "USD/NGN", rate)
        print("⚠ Using fallback rate")


if __name__ == "__main__":
    asyncio.run(update_rates())
