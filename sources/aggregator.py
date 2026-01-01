from statistics import mean

def aggregate(values):
    clean = [v for v in values if isinstance(v, (int, float))]
    if not clean:
        return None

    return {
        "avg": round(mean(clean), 2),
        "min": round(min(clean), 2),
        "max": round(max(clean), 2),
        "sources": len(clean)
    }
