import requests

def exchangerate_host(cur="USD"):
    """
    Get official forex rates from exchangerate.host.
    Returns float or None if fails.
    """
    try:
        r = requests.get(f"https://api.exchangerate.host/latest?base={cur}", timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        # Check if 'rates' exists
        if "rates" not in data or "NGN" not in data["rates"]:
            return None
        return data["rates"]["NGN"]
    except Exception:
        return None  # Never crash
