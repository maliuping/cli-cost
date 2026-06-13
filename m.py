from typing import List, Optional

import typer

from core.db import init_db
from core.models import Expense
from sync.notion_sync import NotionConfigError, NotionSyncError, sync_notion
from core.service import (
    add_expense,
    get_today_expenses,
    get_month_summary,
    get_all_expenses,
    delete_expense,
    get_expense_by_id,
    get_summary_by_time
)

from core.ui import (
    print_today,
    print_month,
    print_range,
    print_all
)

app = typer.Typer(
    add_completion=False
)
sync_app = typer.Typer(help="Sync commands")
app.add_typer(sync_app, name="sync")

init_db()




def _run_notion_sync(limit: int | None):
    try:
        count = sync_notion(limit)
    except NotionConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1)
    except NotionSyncError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Synced {count} records")


@app.command()
def add(
    amount: float,
    category: str,
    note_parts: Optional[List[str]] = typer.Argument(None)
):
    """
    Add expense
    """

    note = " ".join(note_parts or [])

    expense = Expense(
        amount=amount,
        category=category,
        note=note
    )

    add_expense(expense)

    typer.echo(
        f"Added: {amount} {category} {note}"
    )


@app.command()
def today():
    """
    Show today's expenses
    """

    rows = get_today_expenses()

    print_today(rows)


@app.command()
def month(mon: str = None):
    """
    Show monthly summary

    m month(current month)
    m month --mon 2026-5
    """

    rows = get_month_summary(mon)

    print_month(rows)


@app.command()
def list(limit: int = 20):
    """
    Show recent expenses
    """

    rows = get_all_expenses(limit)

    print_all(rows)


@app.command()
def delete(expense_id: int):
    """
    Delete expense by id
    """

    row = get_expense_by_id(expense_id)

    if not row:
        print("Expense not found")
        return

    confirm = input(
        f"Delete #{row['id']} "
        f"{row['category']} "
        f"{row['amount']} ? [y/N] "
    )

    if confirm.lower() != "y":
        print("Cancelled")
        return

    delete_expense(expense_id)

    print("Deleted")

@app.command()
def seek(
    s_ts: str = typer.Option(..., help="start date"),
    e_ts: str = typer.Option(..., help="end date"),
):
    """
    Seek expense summary by time

    m seek --s-ts 2026-5-1 --e-ts 2026-5-31
    """
    rows = get_summary_by_time(s_ts, e_ts)

    print_range(rows)


@sync_app.callback(invoke_without_command=True)
def sync_root(ctx: typer.Context, limit: int = typer.Option(None, "--limit", help="Limit records to sync")):
    """
    Sync expenses to external services
    """

    if ctx.invoked_subcommand is not None:
        return

    _run_notion_sync(limit)


@sync_app.command("notion")
def sync_notion_command(limit: int = typer.Option(None, "--limit", help="Limit records to sync")):
    """
    Sync unsynced expenses to Notion
    """

    _run_notion_sync(limit)


# -----------------------------
# 快速输入模式
# m 32 lunch 麦当劳
# -----------------------------

# @app.callback(invoke_without_command=True)
# def main(
#     ctx: typer.Context,
#     amount: float = None,
#     category: str = None,
#     note: str = ""
# ):
#     """
#     Quick add mode
#     """
#
#     if ctx.invoked_subcommand:
#         return
#
#     if amount is None or category is None:
#         typer.echo("""
# Usage:
#
#   m 32 lunch 麦当劳
#
# Commands:
#
#   m today
#   m month
#   m list
# """)
#         raise typer.Exit()
#
#     expense = Expense(
#         amount=amount,
#         category=category,
#         note=note
#     )
#
#     add_expense(expense)
#
#     typer.echo(
#         f"Added: {amount} {category} {note}"
#     )


if __name__ == "__main__":
    app()
