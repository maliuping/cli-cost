from dataclasses import dataclass

@dataclass
class Expense:
    amount: float
    category: str
    note: str =  ""

