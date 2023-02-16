from components.memory import Memory
from components.registers import Registers

# fmt: off
def ADDB(r: Registers, m: Memory) -> None: r.IP += 1; r.A += r.B
def SUBB(r: Registers, m: Memory) -> None: r.IP += 1; r.A -= r.B
def MULB(r: Registers, m: Memory) -> None: r.IP += 1; r.A *= r.B
def DIVB(r: Registers, m: Memory) -> None: r.IP += 1; r.A //= r.B

def ADDi(r: Registers, m: Memory) -> None: r.IP += 1; r.A += m.load(r.IP); r.IP += 4
def SUBi(r: Registers, m: Memory) -> None: r.IP += 1; r.A -= m.load(r.IP); r.IP += 4
def MULi(r: Registers, m: Memory) -> None: r.IP += 1; r.A *= m.load(r.IP); r.IP += 4
def DIVi(r: Registers, m: Memory) -> None: r.IP += 1; r.A //= m.load(r.IP); r.IP += 4

def ADDb(r: Registers, m: Memory) -> None: r.IP += 1; r.A += m.load(r.B)
def SUBb(r: Registers, m: Memory) -> None: r.IP += 1; r.A -= m.load(r.B)
def MULb(r: Registers, m: Memory) -> None: r.IP += 1; r.A *= m.load(r.B)
def DIVb(r: Registers, m: Memory) -> None: r.IP += 1; r.A //= m.load(r.B)
