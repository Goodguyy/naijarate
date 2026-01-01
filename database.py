from pathlib import Path
import sqlite_utils

# ----------------------------
# Database location
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "naijarate.db"

# ----------------------------
# Initialize database safely
# ----------------------------
def init_db():
    """
    Create database and tables if they do not exist.
    Safe to call multiple times.
    """
    db = sqlite_utils.Database(DB_PATH)

    # Rates table
    db["rates"].create(
        {
            "timestamp": str,
            "usd_ngn": float,
            "cex": str,        # JSON
            "crypto": str,     # JSON
        },
        pk="timestamp",
        if_not_exists=True,
    )

    return db


# Initialize on import (SAFE — no network calls)
init_db()
