from core.db import get_conn
from core.models import Expense


def add_expense(expense: Expense):
    conn = get_conn()

    conn.execute(
        """
        INSERT INTO expenses(amount, category, note)
        VALUES (?, ?, ?)
        """,
        (expense.amount, expense.category, expense.note)
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


def get_month_summary():
    conn = get_conn()

    rows = conn.execute("""
        SELECT
            category,
            ROUND(SUM(amount), 2) as total
        FROM expenses
        WHERE strftime('%Y-%m', ts) =
              strftime('%Y-%m', 'now', 'localtime')
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

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
