import typing as T

from components.memory import Memory
from components.registers import Registers
from processors.opcodes import opcode_map


class Processor:
    memory: Memory
    opcode_map: T.Dict[bytes, T.Callable[[Registers, Memory], None]]
    registers: Registers

    def __init__(self) -> None:
        self.memory = Memory()
        self.opcode_map = opcode_map
        self.registers = Registers()

    def advance(self):
        op = self.opcode_map[self.memory.load_bytes(self.registers.IP, 1)]
        op(self.registers, self.memory)
