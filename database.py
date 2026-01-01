from sqlite_utils import Database
from pathlib import Path
import time

DB_PATH = Path("naijarate.db")

db = Database(DB_PATH)

def init_db():
    if "rates" not in db.table_names():
        db["rates"].create(
            {
                "source": str,
                "pair": str,
                "rate": float,
                "timestamp": int,
            },
            pk="id",
            if_not_exists=True,
        )

def insert_rate(source: str, pair: str, rate: float):
    init_db()
    db["rates"].insert(
        {
            "source": source,
            "pair": pair,
            "rate": rate,
            "timestamp": int(time.time()),
        }
    )
