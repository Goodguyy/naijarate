from sources.forex_sources import exchangerate_host, parallel_estimate
from sources.aggregator import aggregate

CURRENCIES = ["USD", "EUR", "GBP", "CAD"]

def get_forex():
    results = {}

    for cur in CURRENCIES:
        values = []

        official = exchangerate_host(cur)
        if official:
            values.append(official)

        parallels = parallel_estimate(cur)
        values.extend(parallels)

        agg = aggregate(values)
        if agg:
            results[cur] = agg

    return results
