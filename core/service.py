from core.db import get_conn
from core.models import Expense
# from datetime import datetime
from datetime import datetime, timezone, timedelta


LOCAL_TZ = timezone(timedelta(hours=8))

def add_expense(expense: Expense):
    conn = get_conn()
    # ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ts = datetime.now(LOCAL_TZ).isoformat(timespec="seconds")

    conn.execute(
        """
        INSERT INTO expenses(ts, amount, category, note, notion_synced, notion_page_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            ts,
            expense.amount,
            expense.category,
            expense.note,
            expense.notion_synced,
            expense.notion_page_id
        )
    )

    conn.commit()
    conn.close()


def get_today_expenses():
    conn = get_conn()

    rows = conn.execute("""
        SELECT *
        FROM expenses
        WHERE date(ts) = date('now', 'localtime')
        ORDER BY ts DESC
    """).fetchall()

    conn.close()

    return rows


def get_month_summary(month=None):
    if month is None:
        print("hi")
        now = datetime.now()
        year = now.year
        month = now.month
    else:
        year, month = map(int, month.split('-'))

    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    start_ts = f"{year:04d}-{month:02d}-01 00:00:00"
    end_ts = f"{next_year:04d}-{next_month:02d}-01 00:00:00"

    conn = get_conn()

    rows = conn.execute("""
        SELECT
            id,
            category,
            ROUND(SUM(amount), 2) as total
        FROM expenses
        WHERE ts >= ?
            AND ts < ?
        GROUP BY category
        ORDER BY total DESC
        """,(start_ts, end_ts)).fetchall()

    conn.close()

    return rows


def get_all_expenses(limit=50):
    conn = get_conn()

    rows = conn.execute("""
        SELECT *
        FROM expenses
        ORDER BY ts DESC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()

    return rows


def get_expense_by_id(expense_id: int):
    conn = get_conn()

    row = conn.execute("""
        SELECT *
        FROM expenses
        WHERE id = ?
    """, (expense_id,)).fetchone()

    conn.close()

    return row


def delete_expense(expense_id: int):
    conn = get_conn()

    conn.execute("""
        DELETE FROM expenses
        WHERE id = ?
    """, (expense_id,))

    conn.commit()
    conn.close()


def get_unsynced_expenses(limit: int | None = None):
    conn = get_conn()
    query = """
        SELECT *
        FROM expenses
        WHERE COALESCE(notion_synced, 0) = 0
        ORDER BY ts ASC, id ASC
    """
    params = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def mark_expense_synced(expense_id: int, notion_page_id: str):
    conn = get_conn()
    conn.execute(
        """
        UPDATE expenses
        SET notion_synced = 1,
            notion_page_id = ?
        WHERE id = ?
        """,
        (notion_page_id, expense_id)
    )
    conn.commit()
    conn.close()

