from dataclasses import dataclass

@dataclass
class Registers:
    # Flags
    IP: int = 0
    ZF: bool = 0
    # GP
    A: int = 0
    B: int = 0