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
