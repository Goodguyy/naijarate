from datetime import datetime
from .cex_rates import get_forex
from .crypto import aggregate_crypto

def fetch_all():
    """Fetch aggregated Forex and Crypto from multiple sources safely"""
    try:
        forex = get_forex() or {}
        usd_to_ngn = forex.get("USD", {}).get("avg", 750)
        crypto = aggregate_crypto(usd_to_ngn) or {}
        return {
            "forex": forex,
            "crypto": crypto,
            "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    except Exception:
        return {
            "forex": {},
            "crypto": {},
            "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }
