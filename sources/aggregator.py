import statistics

def aggregate_rates(primary, secondary):
    weighted = []

    # Give Binance rates more weight
    for r in primary:
        weighted.extend([r] * 6)

    # Blog rates get less weight
    for r in secondary:
        weighted.extend([r] * 3)

    if not weighted:
        return None

    median = statistics.median(weighted)

    # Filter out outliers more than 7% from median
    filtered = [
        r for r in weighted
        if abs(r - median) / median < 0.07
    ]

    return {
        "avg": round(statistics.mean(filtered), 2),
        "min": min(filtered),
        "max": max(filtered),
        "sources": len(filtered)
    }
