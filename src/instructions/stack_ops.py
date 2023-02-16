from components.memory import Memory
from components.registers import Registers

def _psh(r: Registers, m: Memory, v: int) -> None: m.store(r.SP, v); r.SP += 1
def _pop(r: Registers, m: Memory)         -> int:  r.SP -= 1; v: int = m.load(r.SP); return v

def PSHA(r: Registers, m: Memory) -> None: r.IP += 1; _psh(r, m, r.A)
def POPA(r: Registers, m: Memory) -> None: r.IP += 1; r.A = _pop(r, m)

def CALL(r: Registers, m: Memory) -> None: _psh(r, m, r.IP); r.IP = m.load(r.IP + 1)
def RETN(r: Registers, m: Memory) -> None: r.IP = _pop(r, m)