import asyncio
from scraper import update_rates

if __name__ == "__main__":
    # Run the scraper once
    asyncio.run(update_rates())
