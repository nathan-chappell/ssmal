from dataclasses import dataclass
from typing import Optional


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int
    filename: Optional[str] = None
