import typing as T
from dataclasses import dataclass

@dataclass
class Line:
    ...

def format_memory(_bytes: bytes) -> T.Generator[str,None,None]