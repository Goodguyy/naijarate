import statistics

def aggregate_rates(rates):
    clean = [r for r in rates if isinstance(r, (int, float))]

    if not clean:
        return None

    return {
        "avg": round(statistics.mean(clean)),
        "min": min(clean),
        "max": max(clean),
        "sources": len(clean)
    }
