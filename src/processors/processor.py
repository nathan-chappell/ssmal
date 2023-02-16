import typing as T

from components.memory import Memory
from components.registers import Registers
import instructions.arithmetic_ops as a_op
import instructions.data_ops as d_op
import instructions.stack_ops as s_op

_opcode_map = {
    b'0x10': a_op.ADDB,
    b'0x11': a_op.SUBB,
    b'0x12': a_op.MULB,
    b'0x13': a_op.DIVB,
    b'0x14': a_op.ADDi,
    b'0x15': a_op.SUBi,
    b'0x16': a_op.MULi,
    b'0x17': a_op.DIVi,
    b'0x18': a_op.ADDb,
    b'0x19': a_op.SUBb,
    b'0x1a': a_op.MULb,
    b'0x1b': a_op.DIVb,

    b'0x20': d_op.LDAi,
    b'0x21': d_op.LDAb,
    b'0x22': d_op.LDA_,
    b'0x23': d_op.STAi,
    b'0x24': d_op.STAb,
    b'0x25': d_op.STA_,

    b'0x20': s_op.PSHA,
    b'0x21': s_op.POPA,
    b'0x22': s_op.CALi,
    b'0x23': s_op.CALA,
    b'0x24': s_op.CAL_,
    b'0x25': s_op.RETN,
}

class Processor:
    registers: Registers
    memory: Memory
    opcode_map: T.Dict[int, T.Callable[[Registers,Memory], None]]

    def __init__(self) -> None:
        self.registers = Registers()
        self.memory = Memory()
    
    def advance(self):
        op = self.opcode_map[self.memory.load(self.registers.IP)]
        op(self.registers, self.memory)
