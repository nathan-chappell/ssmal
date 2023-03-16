from ssmal.components.memory import Memory
from ssmal.components.registers import Registers

# fmt: off
def LDAi(r: Registers, m: Memory) -> None: r.IP += 1; r.A = m.load(r.IP); r.IP += 4
def STAi(r: Registers, m: Memory) -> None: r.IP += 1; m.store(m.load(r.IP), r.A); r.IP += 4

def LDAb(r: Registers, m: Memory) -> None: r.IP += 1; r.A = m.load(r.B)
def STAb(r: Registers, m: Memory) -> None: r.IP += 1; m.store(r.B, r.A)

# LDA_ and STA_ use an immediate operand ($i) to access the $i-th item on the stack
def LDA_(r: Registers, m: Memory) -> None: r.IP += 1; r.A = m.load(r.SP - 4 * (m.load(r.IP) + 1)); r.IP += 4
def STA_(r: Registers, m: Memory) -> None: r.IP += 1; m.store(r.SP - 4 * (m.load(r.IP) + 1), r.A); r.IP += 4
