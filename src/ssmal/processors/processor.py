from typing import Callable
from ssmal.components.memory import Memory
from ssmal.components.registers import Registers
from ssmal.instructions.processor_signals import SysSignal, TrapSignal
from ssmal.processors.opcodes import opcode_map

TOp = Callable[[Registers, Memory], None]


class Processor:
    memory: Memory
    opcode_map: dict[bytes, TOp]
    registers: Registers
    sys_vector: dict[int, TOp]

    def __init__(self) -> None:
        self.memory = Memory()
        self.opcode_map = opcode_map
        self.registers = Registers()
        self.sys_vector = {}

    def advance(self, trace=False, steps=1):
        for _ in range(steps):
            try:
                op = self.opcode_map[self.memory.load_bytes(self.registers.IP, 1)]
                if trace:  # pragma: no cover
                    print(f" op: {op.__name__}")
            except KeyError as e:
                raise TrapSignal(self.registers, self.memory, *e.args)
            try:
                op(self.registers, self.memory)
            except SysSignal:
                sys_op = self.sys_vector[self.registers.A]
                sys_op(self.registers, self.memory)
                self.registers.IP += 1
