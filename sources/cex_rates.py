from .forex_sources import all_official_sources, all_blackmarket_sources

def get_forex():
    """
    Aggregate multiple sources for each currency:
    - Official rate (from CBN, exchangerate.host, banks)
    - Blackmarket rate (AbokiFX, blogs, CEX P2P)
    Returns a dict like:
    {
        "USD": {"official": {...}, "blackmarket": {...}},
        "EUR": {...}
    }
    """
    currencies = ["USD", "EUR", "GBP", "CAD"]
    results = {}

    for cur in currencies:
        try:
            # ----------------- Official Rates -----------------
            official_list = all_official_sources()
            official_filtered = [r for r in official_list if r]  # remove None
            if official_filtered:
                official_data = {
                    "avg": round(sum(official_filtered)/len(official_filtered), 2),
                    "min": round(min(official_filtered), 2),
                    "max": round(max(official_filtered), 2),
                    "sources": len(official_filtered)
                }
            else:
                official_data = None

            # ----------------- Blackmarket Rates -----------------
            black_list = all_blackmarket_sources()
            black_filtered = [r for r in black_list if r]
            if black_filtered:
                black_data = {
                    "avg": round(sum(black_filtered)/len(black_filtered), 2),
                    "min": round(min(black_filtered), 2),
                    "max": round(max(black_filtered), 2),
                    "sources": len(black_filtered)
                }
            else:
                black_data = None

            # ----------------- Combine -----------------
            results[cur] = {
                "official": official_data,
                "blackmarket": black_data
            }

        except Exception:
            results[cur] = {
                "official": None,
                "blackmarket": None
            }

    return results
