from dataclasses import dataclass

@dataclass
class Expense:
    amount: float
    category: str
    note: str =  ""
    ts: str = ""
    notion_synced: int = 0
    notion_page_id: str = ""
