import sqlite3
from pathlib import Path

import pandas as pd


# Use app/data for both CSVs and the SQLite DB
BASE_DIR = Path(__file__).resolve().parent  # .../backend/app
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
PAYMENTS_CSV = DATA_DIR / "payments.csv"
MERCHANTS_CSV = DATA_DIR / "merchants_loyalty.csv"


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cur.fetchone() is not None


def _row_count(conn: sqlite3.Connection, table_name: str) -> int:
    cur = conn.execute(f"SELECT COUNT(1) FROM {table_name}")
    return int(cur.fetchone()[0])


def init_db_from_csv() -> None:
    """
    Initialize the SQLite database from CSVs if tables are missing or empty.
    Creates basic indexes for faster aggregations used by dashboards.
    """
    with _connect() as conn:
        # Create tables if not exist
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                PaymentID TEXT PRIMARY KEY,
                CustomerID TEXT,
                CustomerName TEXT,
                MerchantID TEXT,
                MerchantName TEXT,
                PaymentDate TEXT,
                PaymentAmount REAL,
                PaymentStatus TEXT,
                DisputeFlag INTEGER,
                DefaultFlag INTEGER
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS merchants_loyalty (
                MerchantID TEXT PRIMARY KEY,
                MerchantName TEXT,
                RepaymentRate REAL,
                DisputeRate REAL,
                DefaultRate REAL,
                TransactionVolume INTEGER,
                TenureMonths INTEGER,
                EngagementScore REAL,
                ComplianceScore REAL,
                ResponsivenessScore REAL,
                ExclusivityFlag INTEGER
            )
            """
        )

        # Load from CSV if empty
        if PAYMENTS_CSV.exists() and (_row_count(conn, "payments") == 0):
            df = pd.read_csv(PAYMENTS_CSV)
            df.to_sql("payments", conn, if_exists="append", index=False)

        if MERCHANTS_CSV.exists() and (_row_count(conn, "merchants_loyalty") == 0):
            dfm = pd.read_csv(MERCHANTS_CSV)
            dfm.to_sql("merchants_loyalty", conn, if_exists="append", index=False)

        # Indexes for speed
        conn.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(PaymentStatus)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(PaymentDate)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_payments_merchant ON payments(MerchantName)")


