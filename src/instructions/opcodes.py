from components.memory import Memory
from components.registers import Registers

def ADDB(r: Registers, m: Memory) -> None: r.IP += 1; r.A += r.B
def SUBB(r: Registers, m: Memory) -> None: r.IP += 1; r.A -= r.B
def MULB(r: Registers, m: Memory) -> None: r.IP += 1; r.A *= r.B
def DIVB(r: Registers, m: Memory) -> None: r.IP += 1; r.A //= r.B

def ADDi(r: Registers, m: Memory) -> None: r.IP += 1; v: int = m.load(r.IP); r.IP += 4; r.A += v
def SUBi(r: Registers, m: Memory) -> None: r.IP += 1; v: int = m.load(r.IP); r.IP += 4; r.A -= v
def MULi(r: Registers, m: Memory) -> None: r.IP += 1; v: int = m.load(r.IP); r.IP += 4; r.A *= v
def DIVi(r: Registers, m: Memory) -> None: r.IP += 1; v: int = m.load(r.IP); r.IP += 4; r.A //= v

def ADDm(r: Registers, m: Memory) -> None: r.IP += 1; a: int = m.load(r.IP); r.IP += 4; v: int = m.load(a); r.A += v
def SUBm(r: Registers, m: Memory) -> None: r.IP += 1; a: int = m.load(r.IP); r.IP += 4; v: int = m.load(a); r.A -= v
def MULm(r: Registers, m: Memory) -> None: r.IP += 1; a: int = m.load(r.IP); r.IP += 4; v: int = m.load(a); r.A *= v
def DIVm(r: Registers, m: Memory) -> None: r.IP += 1; a: int = m.load(r.IP); r.IP += 4; v: int = m.load(a); r.A //= v
