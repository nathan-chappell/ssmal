import typing as T

from components.memory import Memory
from components.registers import Registers
import instructions.arithmetic_ops as a_op
import instructions.data_ops as d_op
import instructions.stack_ops as s_op

_opcode_map = {
    b'\x10': a_op.ADDB,
    b'\x11': a_op.SUBB,
    b'\x12': a_op.MULB,
    b'\x13': a_op.DIVB,
    b'\x14': a_op.ADDi,
    b'\x15': a_op.SUBi,
    b'\x16': a_op.MULi,
    b'\x17': a_op.DIVi,
    b'\x18': a_op.ADDb,
    b'\x19': a_op.SUBb,
    b'\x1a': a_op.MULb,
    b'\x1b': a_op.DIVb,

    b'\x20': d_op.LDAi,
    b'\x21': d_op.LDAb,
    b'\x22': d_op.LDA_,
    b'\x23': d_op.STAi,
    b'\x24': d_op.STAb,
    b'\x25': d_op.STA_,

    b'\x20': s_op.PSHA,
    b'\x21': s_op.POPA,
    b'\x22': s_op.CALi,
    b'\x23': s_op.CALA,
    b'\x24': s_op.CAL_,
    b'\x25': s_op.RETN,
}

class Processor:
    memory: Memory
    opcode_map: T.Dict[bytes, T.Callable[[Registers,Memory], None]]
    registers: Registers

    def __init__(self) -> None:
        self.memory = Memory()
        self.opcode_map = _opcode_map
        self.registers = Registers()
    
    def advance(self):
        op = self.opcode_map[self.memory.load_bytes(self.registers.IP, 1)]
        op(self.registers, self.memory)
