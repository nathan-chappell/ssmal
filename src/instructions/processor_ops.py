from components.memory import Memory
from components.registers import Registers

class HaltException(Exception):
    registers: Registers
    memory: Memory

    def __init__(self, registers: Registers, memory: Memory, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.registers = registers
        self.memory = memory

def HALT(r: Registers, m: Memory) -> None: raise HaltException(r,m)