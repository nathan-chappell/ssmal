from ssmal.components.memory import Memory
from ssmal.components.registers import Registers

# fmt: off
def SWPAB(r: Registers, m: Memory) -> None: r.A, r.B = r.B, r.A
def SWPAS(r: Registers, m: Memory) -> None: r.A, r.SP = r.SP, r.A
def SWPAI(r: Registers, m: Memory) -> None: r.A, r.IP = r.IP, r.A
