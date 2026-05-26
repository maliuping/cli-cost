from pathlib import Path
import sqlite3

DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "money.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        ts TEXT NOT NULL,

        amount REAL NOT NULL,

        category TEXT NOT NULL,

        note TEXT
    )
    """)

    conn.commit()
    conn.close()


