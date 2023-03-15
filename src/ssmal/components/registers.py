from dataclasses import dataclass


@dataclass
class Registers:
    # Flags
    # ZF: bool = 0
    # GP
    A: int = 0
    B: int = 0
    # Pointers
    IP: int = 0
    SP: int = 0

    def __repr__(self) -> str:
        return f"[{self.A:4x}, {self.B:4x}, {self.IP:4x}, {self.SP:4x}]"
