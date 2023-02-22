import typing as T
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int
    filename: T.Optional[str] = None