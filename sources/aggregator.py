import statistics

def aggregate_rates(rates_list):
    """
    Aggregate a list of rates from multiple sources.

    Args:
        rates_list (list): Each item can be:
            - a number (int/float)
            - a dict of currency rates, e.g., {"USD": 755, "EUR": 820}
            - None (ignored)
    
    Returns:
        dict: {
            "avg": float,
            "min": float,
            "max": float,
            "sources": int
        } 
        Returns {} if no valid rates found.
    """
    # Flatten all rates into a single list
    flat_rates = []
    for r in rates_list:
        if isinstance(r, dict):
            flat_rates.extend([v for v in r.values() if isinstance(v, (int, float))])
        elif isinstance(r, (int, float)):
            flat_rates.append(r)
        # Ignore None or invalid entries

    if not flat_rates:
        return {}

    return {
        "avg": round(statistics.mean(flat_rates), 2),
        "min": round(min(flat_rates), 2),
        "max": round(max(flat_rates), 2),
        "sources": len(flat_rates)
    }
