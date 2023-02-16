from dataclasses import dataclass

@dataclass
class Registers:
    # Flags
    ZF: bool = 0
    # GP
    A: int = 0
    B: int = 0
    # Pointers
    IP: int = 0
    SP: int = 0