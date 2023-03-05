from dataclasses import dataclass
from typing import Literal


@dataclass
class TmTransition:
    cur_state: str
    cur_symbol: Literal["0", "1", "2"]
    next_state: str
    next_symbol: Literal["0", "1", "2"]
    move_head: Literal["L", "R", "STAY"]
