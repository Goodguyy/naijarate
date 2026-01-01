import statistics

def aggregate_rates(rates_list):
    # Remove any None or invalid values
    valid_rates = [r for r in rates_list if r is not None]
    if not valid_rates:
        return None

    return {
        "avg": round(statistics.mean(valid_rates), 2),
        "min": min(valid_rates),
        "max": max(valid_rates),
        "sources": len(valid_rates)
    }
