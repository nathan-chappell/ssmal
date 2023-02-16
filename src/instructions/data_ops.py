from components.memory import Memory
from components.registers import Registers

# load/store a,i,m

def LDAi(r: Registers, m: Memory) -> None: r.IP += 1; r.A = m.load(r.IP); r.IP += 4
def LDAb(r: Registers, m: Memory) -> None: r.IP += 1; r.A = m.load(r.B)
def LDA_(r: Registers, m: Memory) -> None: r.IP += 1; r.A = m.load(m.load(r.B))

def STAi(r: Registers, m: Memory) -> None: r.IP += 1; m.store(m.load(r.IP), r.A); r.IP += 4
def STAb(r: Registers, m: Memory) -> None: r.IP += 1; m.store(r.B, r.A)
def STA_(r: Registers, m: Memory) -> None: r.IP += 1; m.store(m.load(r.B), r.A)