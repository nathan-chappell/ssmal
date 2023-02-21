from typing import Dict, Callable

from components.memory import Memory
from components.registers import Registers

import instructions.arithmetic_ops as a_op
import instructions.data_ops as d_op
import instructions.processor_ops as p_op
import instructions.stack_ops as s_op
import instructions.sys_io as sys_io

SYS_BYTE = b"\x80"

opcode_map: Dict[bytes, Callable[[Registers, Memory], None]] = {
    # processor ops
    b"\x00": p_op.HALT,
    b"\x01": p_op.DBG,
    # arithmetic ops
    b"\x10": a_op.ADDB,
    b"\x11": a_op.SUBB,
    b"\x12": a_op.MULB,
    b"\x13": a_op.DIVB,
    b"\x14": a_op.ADDi,
    b"\x15": a_op.SUBi,
    b"\x16": a_op.MULi,
    b"\x17": a_op.DIVi,
    b"\x18": a_op.ADD_,
    b"\x19": a_op.SUB_,
    b"\x1a": a_op.MUL_,
    b"\x1b": a_op.DIV_,
    # data ops
    b"\x20": d_op.LDAi,
    b"\x21": d_op.LDAb,
    b"\x22": d_op.LDA_,
    b"\x23": d_op.STAi,
    b"\x24": d_op.STAb,
    b"\x25": d_op.STA_,
    # stack ops
    b"\x30": s_op.PSHA,
    b"\x31": s_op.POPA,
    b"\x32": s_op.CALi,
    b"\x33": s_op.CALA,
    b"\x34": s_op.CAL_,
    b"\x35": s_op.RETN,
    # syscall - must be added later so that io can be put in...
    SYS_BYTE: sys_io.SysIO(),
}