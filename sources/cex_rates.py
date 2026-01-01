from .forex_sources import all_forex_sources

def get_forex():
    """Aggregate multiple sources for each currency"""
    currencies = ["USD", "EUR", "GBP", "CAD"]
    results = {}
    for cur in currencies:
        try:
            rates = all_forex_sources(cur)
            if not rates:
                continue
            results[cur] = {
                "avg": round(sum(rates)/len(rates), 2),
                "min": round(min(rates), 2),
                "max": round(max(rates), 2),
                "sources": len(rates)
            }
        except Exception:
            continue
    return results
