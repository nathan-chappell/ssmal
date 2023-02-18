import typing as T

from components.memory import Memory
from components.registers import Registers
from processors.opcodes import opcode_map

TOp = T.Callable[[Registers, Memory], None]

class Processor:
    memory: Memory
    opcode_map: T.Dict[bytes, TOp]
    registers: Registers

    def __init__(self) -> None:
        self.memory = Memory()
        self.opcode_map = opcode_map
        self.registers = Registers()

    def advance(self):
        op = self.opcode_map[self.memory.load_bytes(self.registers.IP, 1)]
        op(self.registers, self.memory)
    
    def update_syscall(self, op: TOp):
        self.opcode_map[b'\x80'] = op
