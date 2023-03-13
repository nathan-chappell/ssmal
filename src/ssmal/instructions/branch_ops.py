from ssmal.components.memory import Memory
from ssmal.components.registers import Registers


def _br_if(r: Registers, condition: bool, true_case: int, false_case: int):
    if condition:
        r.IP = true_case
    else:
        r.IP = false_case


# fmt: off
def BRi(r: Registers, m: Memory) -> None: r.IP += 1; r.IP = m.load(r.IP)
def BRa(r: Registers, m: Memory) -> None: r.IP = r.A

def BRZi(r: Registers, m: Memory) -> None: r.IP += 1; _br_if(r, r.A == 0, m.load(r.IP), r.IP + 4)
def BRNi(r: Registers, m: Memory) -> None: r.IP += 1; _br_if(r, r.A < 0, m.load(r.IP), r.IP + 4)
def BRZb(r: Registers, m: Memory) -> None: r.IP += 1; _br_if(r, r.A == 0, r.B, r.IP)
def BRNb(r: Registers, m: Memory) -> None: r.IP += 1; _br_if(r, r.A < 0, r.B, r.IP)

def BRb(r: Registers, m: Memory) -> None: r.IP = r.B