import typing as T

from components.memory import Memory
from components.registers import Registers
from processors.opcodes import opcode_map, SYS_BYTE
from instructions.sys_io import SysIO

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

    @property
    def sys_io(self) -> SysIO:
        return T.cast(SysIO, self.opcode_map[SYS_BYTE])
