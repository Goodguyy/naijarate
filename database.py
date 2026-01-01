from cachetools import TTLCache

# Cache forex & crypto data for 2 minutes
cache = TTLCache(maxsize=10, ttl=120)
