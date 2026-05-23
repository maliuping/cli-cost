import typer

from core.db import init_db
from core.models import Expense
from core.service import (
    add_expense,
    get_today_expenses,
    get_month_summary,
    get_all_expenses
)

from core.ui import (
    print_today,
    # print_month,
    # print_all
)

app = typer.Typer(
    add_completion=False
)

init_db()


@app.command()
def add(
    amount: float,
    category: str,
    note: str = ""
):
    """
    Add expense
    """

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
def month():
    """
    Show monthly summary
    """

    rows = get_month_summary()

    print_month(rows)


@app.command()
def list(limit: int = 20):
    """
    Show recent expenses
    """

    rows = get_all_expenses(limit)

    print_all(rows)


# -----------------------------
# 快速输入模式
# m 32 lunch 麦当劳
# -----------------------------

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    amount: float = None,
    category: str = None,
    note: str = ""
):
    """
    Quick add mode
    """

    if ctx.invoked_subcommand:
        return

    if amount is None or category is None:
        typer.echo("""
Usage:

  m 32 lunch 麦当劳

Commands:

  m today
  m month
  m list
""")
        raise typer.Exit()

    expense = Expense(
        amount=amount,
        category=category,
        note=note
    )

    add_expense(expense)

    typer.echo(
        f"Added: {amount} {category} {note}"
    )


if __name__ == "__main__":
    app()
