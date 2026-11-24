import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "support.db"


def _db_path() -> str:
    return os.environ.get("SUPPORT_DB", str(DEFAULT_DB_PATH))


@contextmanager
def get_connection():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL REFERENCES customers(id),
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                category TEXT,
                order_number TEXT,
                urgency TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
