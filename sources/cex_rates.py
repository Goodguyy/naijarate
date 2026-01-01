from .forex_sources import exchangerate_host

def get_forex():
    currencies = ["USD", "EUR", "GBP", "CAD"]
    results = {}
    for cur in currencies:
        try:
            rate = exchangerate_host(cur)
            if rate is None:
                continue
            results[cur] = {"avg": rate, "min": rate, "max": rate, "sources": 1}
        except Exception:
            continue
    return results
