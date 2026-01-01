import statistics

def aggregate_rates(*sources):
    # Flatten and remove None
    all_rates = [rate for source in sources for rate in source if rate is not None]

    if not all_rates:
        return {
            "avg_rate": None,
            "min_rate": None,
            "max_rate": None,
            "sources": 0,
            "raw_data": sources
        }

    avg_rate = sum(all_rates) / len(all_rates)
    min_rate = min(all_rates)
    max_rate = max(all_rates)
    median_rate = statistics.median(all_rates)

    return {
        "avg_rate": round(avg_rate, 2),
        "min_rate": min_rate,
        "max_rate": max_rate,
        "median": median_rate,
        "sources": len(all_rates),
        "raw_data": sources
    }
