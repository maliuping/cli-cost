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


def get_summary_by_time(start_ts, end_ts):
    if start_ts is None or end_ts is None:
        raise ValueError("start_ts and end_ts are required")

    start_year, start_month, start_day = map(int, start_ts.split('-'))
    end_year, end_month, end_day = map(int, end_ts.split('-'))

    start_ts = f"{start_year:04d}-{start_month:02d}-{start_day:02d} 00:00:00"
    end_ts = f"{end_year:04d}-{end_month:02d}-{end_day:02d} 00:00:00"

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

def update_expense_by_id(
        expense_id: int,
        amount: float|None = None,
        category: str|None = None,
        note: str|None = None,
        ts: str|None = None
        )->bool:


    updates = []
    params = []

    if amount is not None:
        updates.append("amount = ?")
        params.append(amount)

    if category is not None:
        updates.append("category = ?")
        params.append(category)

    if note is not None:
        updates.append("note = ?")
        params.append(note)

    if ts is not None:
        updates.append("ts = ?")
        params.append(ts)

    if updates is None:
        return False

    params.append(expense_id)

    conn = get_conn()

    cursor = conn.execute(
        f"""
        UPDATE expenses
        SET {", ".join(updates)}
        WHERE id = ?
        """,
        params,
    )

    conn.commit()

    updated = cursor.rowcount > 0

    conn.close()

    return updated




