from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def print_today(rows):
    table = Table(title="Today's Expenses")

    table.add_column("Time")
    table.add_column("Category")
    table.add_column("Amount", justify="right")
    table.add_column("Note")

    total = 0

    for row in rows:
        table.add_row(
            row["ts"][11:16],
            row["category"],
            f"{row['amount']:.2f}",
            row["note"] or ""
        )

        total += row["amount"]

    console.print(table)

    console.print(
        Panel.fit(
            f"[bold green]TOTAL: {total:.2f}[/bold green]"
        )
    )

def print_month(rows):
    table = Table(title="Monthly Summary")

    table.add_column("Category")
    table.add_column("Total", justify="right")

    grand_total = 0

    for row in rows:
        table.add_row(
            row["category"],
            f"{row['total']:.2f}"
        )

        grand_total += row["total"]

    console.print(table)

    console.print(
        Panel.fit(
            f"[bold cyan]MONTH TOTAL: {grand_total:.2f}[/bold cyan]"
        )
    )


def print_all(rows):
    table = Table(title="Recent Expenses")

    table.add_column("Date")
    table.add_column("Category")
    table.add_column("Amount", justify="right")
    table.add_column("Note")

    for row in rows:
        table.add_row(
            row["ts"],
            row["category"],
            f"{row['amount']:.2f}",
            row["note"] or ""
        )

    console.print(table)
