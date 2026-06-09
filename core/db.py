from pathlib import Path
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DB_DIR = PROJECT_ROOT / "data"
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

        note TEXT,

        notion_synced INTEGER DEFAULT 0,

        notion_page_id TEXT
    )
    """)

    _ensure_column(
        conn,
        "ALTER TABLE expenses ADD COLUMN notion_synced INTEGER DEFAULT 0"
    )
    _ensure_column(
        conn,
        "ALTER TABLE expenses ADD COLUMN notion_page_id TEXT"
    )

    conn.commit()
    conn.close()


def _ensure_column(conn, ddl: str):
    try:
        conn.execute(ddl)
    except sqlite3.OperationalError as exc:
        if "duplicate column name" not in str(exc).lower():
            raise
