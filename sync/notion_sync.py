import os
from typing import Iterable

from core.service import get_unsynced_expenses, mark_expense_synced


class NotionConfigError(RuntimeError):
    pass


class NotionSyncError(RuntimeError):
    pass


def _load_notion_config():
    token = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_TOKEN")
    database_id = os.getenv("NOTION_DATABASE_ID")

    if not token or not database_id:
        raise NotionConfigError(
            "Missing Notion config. Set NOTION_TOKEN and NOTION_DATABASE_ID."
        )

    return token, database_id


def _build_notion_client():
    try:
        from notion_client import Client
    except ImportError as exc:
        raise NotionSyncError(
            "notion-client is not installed. Add it to requirements.txt first."
        ) from exc

    token, _ = _load_notion_config()
    return Client(auth=token)


def _rich_text(text: str):
    return [{"type": "text", "text": {"content": text or ""}}]


def _expense_to_page(expense):
    note = expense["note"] or ""
    return {
        "Date": {"date": {"start": expense["ts"]}},
        "Amount": {"number": float(expense["amount"])},
        #"Category": {"title": _rich_text(expense["category"])},
        "Category": {"rich_text": _rich_text(expense["category"])},
        "Note": {"rich_text": _rich_text(note)},
    }


def sync_notion(limit: int | None = None) -> int:
    client = _build_notion_client()
    _, database_id = _load_notion_config()
    expenses = get_unsynced_expenses(limit)

    synced = 0
    for expense in expenses:
        page = client.pages.create(
            parent={"database_id": database_id},
            properties=_expense_to_page(expense),
        )
        page_id = page.get("id")
        mark_expense_synced(expense["id"], page_id)
        synced += 1

    return synced
