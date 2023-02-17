import instructions.syscalls as V

from components.memory import Memory
from components.registers import Registers

def SYS(r: Registers, m: Memory) -> None:
    if (r.A == V.PMEM):
        ...
    elif (r.A == V.PREG):
        ...
    elif (r.A == V.PTOPz):
        ...
    elif (r.A == V.PTOPi):
        ...
    elif (r.A == V.PTOPx):
        ...
    else:
        raise Exception(f'unknown syscall: 0x{r.A:x}')
