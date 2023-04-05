from ssmal.components.memory import Memory
from ssmal.components.registers import Registers


def _psh(r: Registers, m: Memory, v: int) -> None:
    m.store(r.SP, v)
    r.SP += 4


def _pop(r: Registers, m: Memory) -> int:
    r.SP -= 4
    return m.load(r.SP)


# fmt: off
def PSHA(r: Registers, m: Memory) -> None: r.IP += 1; _psh(r, m, r.A)
def POPA(r: Registers, m: Memory) -> None: r.IP += 1; r.A = _pop(r, m)
def PSHI(r: Registers, m: Memory) -> None: r.IP += 1; _psh(r, m, r.IP)

def CALi(r: Registers, m: Memory) -> None: _psh(r, m, r.IP + 5); r.IP = m.load(r.IP + 1)
def CALA(r: Registers, m: Memory) -> None: _psh(r, m, r.IP + 1); r.IP = r.A
def CAL_(r: Registers, m: Memory) -> None: _psh(r, m, r.IP + 1); r.IP = m.load(r.A)

def RETN(r: Registers, m: Memory) -> None: r.IP = _pop(r, m)
